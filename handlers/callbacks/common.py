from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from database.db import Database
from keyboards.inline import get_main_menu_keyboard
from utils.logger_conf import setup_logger
from config import UPLOADS_DIR, ADMIN_CHAT_ID
import os

logger = setup_logger(__name__)
router = Router()

PROBLEM_NAMES = {
    'terms': 'Сроки',
    'supply': 'Поставки',
    'staff': 'Персонал',
    'other': 'Другое'
}

async def finalize_report(bot, message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    workshop_code = data.get('workshop_code')
    if not workshop_code:
        await message.answer("❌ Ошибка: цех не определён. Начните заново.")
        await state.clear()
        return

    await db.save_report(
        user_id=message.from_user.id,
        workshop_code=workshop_code,
        project_code=data.get('project_code'),
        master_fullname=data.get('fullname'),
        color=data.get('color'),
        report_type=data.get('report_type'),
        problem_type=data.get('problem_type'),
        description=data.get('description'),
        photo_path=data.get('photo_path'),
    )

    # Отправка уведомления
    if ADMIN_CHAT_ID:
        workshop_names = {
            'welding': 'цеха сварки',
            'auxiliary': 'вспомогательного цеха',
            'preparatory': 'заготовительного цеха',
            'assembly': 'сборочного цеха',
            'rvi': 'цеха RVI',
        }
        name = workshop_names.get(workshop_code, 'цеха')
        text = f"🔧 **Отчёт {name}**\n"
        text += f"Мастер: {data.get('fullname', 'не указан')}\n"
        text += f"Проект: {data.get('project_code', 'не указан')}\n"
        text += f"Цвет: {'🟢 Зелёный' if data.get('color') == 'green' else '🔴 Красный'}\n"
        if data.get('report_type'):
            text += f"Тип: {data['report_type']}\n"
        if data.get('problem_type'):
            prob_name = PROBLEM_NAMES.get(data['problem_type'], data['problem_type'])
            text += f"Проблема: {prob_name}\n"
        if data.get('description'):
            text += f"Описание: {data['description']}\n"
        await bot.send_message(ADMIN_CHAT_ID, text, parse_mode="Markdown")
        if data.get('photo_path') and os.path.exists(data['photo_path']):
            await bot.send_photo(ADMIN_CHAT_ID, photo=FSInputFile(data['photo_path']))

    await message.answer("✅ Спасибо! Сообщение отправлено администратору.")
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())


# Общий обработчик для кнопки "Приложить фото"
@router.callback_query(F.data == "attach_photo")
async def attach_photo(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        await callback.answer("Кнопка не активна", show_alert=True)
        return
    await callback.message.edit_text("📸 Отправьте фото (одно):")
    # Состояние остаётся photo_optional, но текст сообщения меняется
    await callback.answer()

# Общий обработчик для кнопки "Пропустить фото"
@router.callback_query(F.data == "skip_photo")
async def skip_photo(callback: CallbackQuery, state: FSMContext, db: Database):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        await callback.answer("Кнопка не активна", show_alert=True)
        return
    await finalize_report(callback.bot, callback.message, state, db)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

# Общий обработчик для приёма фото (после нажатия "Приложить фото")
@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext, db: Database):
    current_state = await state.get_state()
    if not current_state or not current_state.endswith("photo_optional"):
        # Если не ожидаем фото, просто игнорируем или отвечаем
        return
    # Скачиваем фото
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    # Имя файла: цех_айди_уникальный.jpg
    workshop_code = (await state.get_data()).get('workshop_code', 'unknown')
    f_name = f"{workshop_code}_{message.from_user.id}_{photo.file_unique_id}.jpg"
    file_path = os.path.join(UPLOADS_DIR, f_name)
    await message.bot.download_file(file.file_path, file_path)
    await state.update_data(photo_path=file_path)
    await finalize_report(message.bot, message, state, db)