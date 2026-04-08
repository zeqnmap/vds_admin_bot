from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from config import ADMIN_CHAT_ID
from database.db import Database
from keyboards.inline import (get_attach_photo_keyboard,
                              get_efficiency_keyboard, get_main_menu_keyboard,
                              get_problem_desc_keyboard,
                              get_problem_production_keyboard, get_projects_keyboard,
                              get_red_reason_keyboard)
from utils.logger_conf import setup_logger

from .common import finalize_report
from .states import WeldingFSM

logger = setup_logger(__name__)
router = Router()


@router.callback_query(F.data == "workshop_welding")
async def start_welding(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(WeldingFSM.fullname)
    await state.update_data(workshop_code="welding")
    text = "👨‍🏭 Цех сварки\n\nВведите ваши ФИО:"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_production")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.message(WeldingFSM.fullname)
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
            "⚠️ Для этого цеха ещё не добавлены проекты. Обратитесь к администратору."
        )
        await state.clear()
        return
    await message.answer(
        "Выберите проект:", reply_markup=get_projects_keyboard(projects)
    )
    await state.set_state(WeldingFSM.project)


@router.callback_query(WeldingFSM.project, F.data.startswith("project_"))
async def process_project(callback: CallbackQuery, state: FSMContext):
    project_code = callback.data.replace("project_", "")
    await state.update_data(project_code=project_code)
    await callback.message.edit_text(
        "Оцените статус своей задачи по проекту:", reply_markup=get_efficiency_keyboard()
    )
    await state.set_state(WeldingFSM.efficiency)
    await callback.answer()


@router.callback_query(WeldingFSM.efficiency, F.data.startswith("efficiency_"))
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
            text = f"🔧 Отчёт Производства\n"
            text += f"Сварочный цех\n\n"
            text += f"Дата: {now}\n"
            text += f"Мастер: {data['fullname']}\n"
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
            "Выберите причину:", reply_markup=get_red_reason_keyboard()
        )
        await state.set_state(WeldingFSM.red_reason)
        await callback.answer()


@router.callback_query(WeldingFSM.red_reason, F.data == "red_questions")
async def red_questions(callback: CallbackQuery, state: FSMContext):
    await state.update_data(report_type="question")
    await callback.message.edit_text("📝 Напишите ваш вопрос:")
    await state.set_state(WeldingFSM.question_desc)
    await callback.answer()


@router.callback_query(WeldingFSM.red_reason, F.data == "red_problems")
async def red_problems(callback: CallbackQuery, state: FSMContext):
    await state.update_data(report_type="problem")
    await callback.message.edit_text(
        "Выберите тип проблемы:", reply_markup=get_problem_production_keyboard()
    )
    await state.set_state(WeldingFSM.problem_type)
    await callback.answer()


@router.callback_query(WeldingFSM.problem_type, F.data.startswith("problem_"))
async def process_problem_type(callback: CallbackQuery, state: FSMContext):
    problem_type = callback.data.replace("problem_", "")
    await state.update_data(problem_type=problem_type)
    await callback.message.edit_text(
        "Опишите проблему текстом:", reply_markup=get_problem_desc_keyboard()
    )
    await state.set_state(WeldingFSM.problem_desc)
    await callback.answer()


@router.message(WeldingFSM.problem_desc, F.text)
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
    await state.set_state(WeldingFSM.photo_optional)


@router.message(WeldingFSM.question_desc, F.text)
async def process_question(message: Message, state: FSMContext, db: Database):
    text = message.text.strip()
    if not text:
        await message.answer("❌ Вопрос не может быть пустым.")
        return
    await state.update_data(description=text)
    await finalize_report(message.bot, message, state, db)
