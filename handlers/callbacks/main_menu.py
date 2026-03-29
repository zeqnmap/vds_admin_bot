from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import Database
from keyboards.inline import (
    get_main_menu_keyboard,
    get_production_menu_keyboard,
    get_under_construction_keyboard,
)
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)
router = Router()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🏭 Главное меню\n\nВыберите направление:", reply_markup=get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "direction_production")
async def direction_production(callback: CallbackQuery, db: Database):
    workshops = await db.get_workshops()
    if not workshops:
        await callback.message.edit_text("❌ Список цехов пуст.")
        await callback.answer()
        return
    text = "⚙️ Производство\n\nВыберите цех:"
    await callback.message.edit_text(text, reply_markup=get_production_menu_keyboard(workshops))
    await callback.answer()

@router.callback_query(F.data == "direction_kb")
async def direction_kb(callback: CallbackQuery):
    await callback.message.edit_text("🔧 КБ\n\nФункция в разработке.", reply_markup=get_under_construction_keyboard())
    await callback.answer()

@router.callback_query(F.data == "direction_creative")
async def direction_creative(callback: CallbackQuery):
    await callback.message.edit_text("🎨 Креатив\n\nФункция в разработке.", reply_markup=get_under_construction_keyboard())
    await callback.answer()

@router.callback_query(F.data == "direction_product")
async def direction_product(callback: CallbackQuery):
    await callback.message.edit_text("🏭 Продукт\n\nФункция в разработке.", reply_markup=get_under_construction_keyboard())
    await callback.answer()