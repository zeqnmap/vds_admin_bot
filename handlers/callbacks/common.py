import os
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from config import ADMIN_CHAT_ID, UPLOADS_DIR
from database.db import Database
from keyboards.inline import get_main_menu_keyboard
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)
router = Router()

PROBLEM_NAMES_COMMON = {
    'terms': 'Сроки',
    'supply': 'Поставки',
    'staff': 'Персонал',
    'other': 'Другое',
    'machine': 'Оборудование',
    'equipment': 'Комплектация',
}

PROBLEM_NAMES_SALE = {
    'contracting': 'Контрактование',
    'advance': 'Авансирование',
    'deadline': 'Сроки',
    'activation': 'Актирование',
    'payment': 'Поступление ДС (100%)',
    'other': 'Другое',
}

PROBLEM_NAMES_INSTALLATION = {
    'terms': 'Сроки',
    'staff': 'Персонал',
    'equipment': 'Комплектация',
    'other': 'Другое',
}

PRODUCTION_WORKSHOPS = ["welding", "auxiliary", "preparatory", "assembly", "rvi"]

def get_problem_name(workshop_code: str, problem_code: str) -> str:
    """Возвращает человекочитаемое название проблемы в зависимости от направления"""
    if workshop_code == 'sales':
        return PROBLEM_NAMES_SALE.get(problem_code, problem_code)
    elif workshop_code == 'installation':
        return PROBLEM_NAMES_INSTALLATION.get(problem_code, problem_code)
    else:
        return PROBLEM_NAMES_COMMON.get(problem_code, problem_code)

async def finalize_report(bot, message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    workshop_code = data.get("workshop_code")
    if not workshop_code:
        await message.answer("❌ Ошибка: цех не определён. Начните заново.")
        await state.clear()
        return

    await db.save_report(
        user_id=message.from_user.id,
        workshop_code=workshop_code,
        project_code=data.get("project_code"),
        master_fullname=data.get("fullname"),
        color=data.get("color"),
        report_type=data.get("report_type"),
        problem_type=data.get("problem_type"),
        description=data.get("description"),
        photo_path=data.get("photo_path"),
    )

    if ADMIN_CHAT_ID:
        from datetime import datetime
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        workshop_names = {
            "welding": "Цех сварки",
            "auxiliary": "Вспомогательный цех",
            "preparatory": "Заготовительный цех",
            "assembly": "Сборочный цех",
            "rvi": "Цех RVI",
            "creative": "Креатива",
            "sales": "Продаж",
            "kb": "КБ",
            "logistics": "Логистики",
            "installation": "Монтажа",
            'passport': 'Паспортизации',
            'supply': 'Снабжения',
            'economics': 'Экономики',
        }

        if workshop_code in PRODUCTION_WORKSHOPS:
            role = "Мастер"
            text = f"Отчёт Производства\n{workshop_names.get(workshop_code)}\n\n"
        else:
            role = "Специалист"
            text = f"Отчёт {workshop_names.get(workshop_code)}\n\n"

        text += f"Дата: {now}\n"
        text += f"{role}: {data.get('fullname', 'не указан')}\n"
        text += f"Проект: {data.get('project_code', 'не указан')}\n"
        text += f"{'🟢 Зелёный' if data.get('color') == 'green' else '🔴 Красный'}\n"

        if data.get("problem_type"):
            prob_name = get_problem_name(workshop_code, data["problem_type"])
            text += f"Проблема: {prob_name}\n"
        if data.get("description"):
            text += f"Описание: {data['description']}\n"

        await bot.send_message(ADMIN_CHAT_ID, text)
        if data.get("photo_path") and os.path.exists(data["photo_path"]):
            await bot.send_photo(ADMIN_CHAT_ID, photo=FSInputFile(data["photo_path"]))

    await message.answer("✅ Спасибо! Сообщение отправлено администратору.")
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "attach_photo")
async def attach_photo(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        await callback.answer("Кнопка не активна", show_alert=True)
        return
    await callback.message.edit_text("📸 Отправьте фото (одно):")
    await callback.answer()


@router.callback_query(F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext, db: Database):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        await callback.answer("Кнопка не активна", show_alert=True)
        return
    await finalize_report(callback.bot, callback.message, state, db)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext, db: Database):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        return
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    workshop_code = (await state.get_data()).get("workshop_code", "unknown")
    f_name = f"{workshop_code}_{message.from_user.id}_{photo.file_unique_id}.jpg"
    file_path = os.path.join(UPLOADS_DIR, f_name)
    await message.bot.download_file(file.file_path, file_path)
    await state.update_data(photo_path=file_path)
    await finalize_report(message.bot, message, state, db)
