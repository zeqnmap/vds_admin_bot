from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import Database
from keyboards.inline import (
    get_efficiency_keyboard,
    get_projects_keyboard,
    get_green_red,
    get_attach_photo_keyboard,
    get_main_menu_keyboard,
)
from .states import PassportFSM
from .common import finalize_report
from utils.logger_conf import setup_logger
from config import ADMIN_CHAT_ID
import os

logger = setup_logger(__name__)
router = Router()


@router.callback_query(F.data == "direction_passport")
async def start_passport(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PassportFSM.fullname)
    await state.update_data(workshop_code="passport")
    text = "🗂 Паспортизация\n\nВведите ваши ФИО:"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.message(PassportFSM.fullname)
async def process_fullname(message: Message, state: FSMContext, db: Database):
    fullname = message.text.strip()
    if not fullname:
        await message.answer("❌ ФИО не может быть пустым.")
        return
    await state.update_data(fullname=fullname)
    workshop_code = (await state.get_data()).get("workshop_code")
    projects = await db.get_workshop_projects(workshop_code)
    if not projects:
        await message.answer(
            "⚠️ Для этого направления ещё не добавлены проекты. Обратитесь к администратору."
        )
        await state.clear()
        return
    await message.answer(
        "Выберите проект:", reply_markup=get_projects_keyboard(projects)
    )
    await state.set_state(PassportFSM.project)


@router.callback_query(PassportFSM.project, F.data.startswith("project_"))
async def process_project(callback: CallbackQuery, state: FSMContext):
    project_code = callback.data.replace("project_", "")
    await state.update_data(project_code=project_code)
    await callback.message.edit_text(
        "Оцените эффективность работы:", reply_markup=get_efficiency_keyboard()
    )
    await state.set_state(PassportFSM.efficiency)
    await callback.answer()


@router.callback_query(PassportFSM.efficiency, F.data.startswith("efficiency_"))
async def process_efficiency(callback: CallbackQuery, state: FSMContext, db: Database):
    color = callback.data.replace("efficiency_", "")
    await state.update_data(color=color)
    if color == "green":
        data = await state.get_data()
        await db.save_report(
            user_id=callback.from_user.id,
            workshop_code=data["workshop_code"],
            project_code=data["project_code"],
            master_fullname=data["fullname"],
            color="green",
        )

        if ADMIN_CHAT_ID:
            from datetime import datetime

            now = datetime.now().strftime("%d-%m-%Y %H:%M")
            text = f"🗂 Отчёт Паспортизации\n\n"
            text += f"Дата: {now}\n"
            text += f"Специалист: {data['fullname']}\n"
            text += f"Проект: {data['project_code']}\n"
            text += f"🟢 Зелёный\n"
            await callback.bot.send_message(ADMIN_CHAT_ID, text)
        await callback.message.edit_text("Отлично! 👍")
        await state.clear()
        await callback.message.answer(
            "Главное меню:", reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            "Опишите проблему текстом:", reply_markup=get_green_red()
        )
        await state.set_state(PassportFSM.problem_desc)
        await callback.answer()



@router.message(PassportFSM.problem_desc, F.text)
async def process_problem_text(message: Message, state: FSMContext):
    desc = message.text.strip()
    if not desc:
        await message.answer("❌ Описание не может быть пустым.")
        return
    await state.update_data(description=desc)
    await message.answer(
        "Теперь вы можете приложить фото или пропустить:",
        reply_markup=get_attach_photo_keyboard(),
    )
    await state.set_state(PassportFSM.photo_optional)


@router.callback_query(F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext, db: Database):
    current_state = await state.get_state()
    if current_state != PassportFSM.photo_optional.state:
        await callback.answer("Эта кнопка больше не активна.", show_alert=True)
        return
    await finalize_report(callback.bot, callback.message, state, db)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(F.data == "attach_photo")
async def attach_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📸 Отправьте фото:")
    await state.set_state(PassportFSM.photo_optional)
    await callback.answer()


@router.message(PassportFSM.photo_optional, F.photo)
async def process_photo(message: Message, state: FSMContext, db: Database):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_name = f"creative_{message.from_user.id}_{photo.file_unique_id}.jpg"
    file_path = os.path.join("uploads", file_name)
    await message.bot.download_file(file.file_path, file_path)
    await state.update_data(photo_path=file_path)
    await finalize_report(message.bot, message, state, db)
