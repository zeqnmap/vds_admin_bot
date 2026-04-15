from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.db import Database
from keyboards.inline import (get_main_menu_keyboard,
                              get_production_menu_keyboard)
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)
router = Router()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🏭 Главное меню\n\nВыберите направление:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "direction_production")
async def direction_production(callback: CallbackQuery, db: Database):
    workshops_prod = await db.get_workshops_prod()
    if not workshops_prod:
        await callback.message.edit_text("❌ Список цехов пуст.")
        await callback.answer()
        return
    text = "⚙️ Производство\n\nВыберите цех:"
    await callback.message.edit_text(
        text, reply_markup=get_production_menu_keyboard(workshops_prod)
    )
    await callback.answer()


@router.callback_query(F.data == "direction_kb")
async def direction_kb(callback: CallbackQuery, state: FSMContext):
    from .kb import start_kb

    await start_kb(callback, state)


@router.callback_query(F.data == "direction_creative")
async def direction_creative(callback: CallbackQuery, state: FSMContext):
    from .creative import start_creative

    await start_creative(callback, state)


@router.callback_query(F.data == "direction_sales")
async def direction_sales(callback: CallbackQuery, state: FSMContext):
    from .sales import start_sales

    await start_sales(callback, state)


@router.callback_query(F.data == "direction_logistics")
async def direction_logistics(callback: CallbackQuery, state: FSMContext):
    from .logistics import start_logistics

    await start_logistics(callback, state)


@router.callback_query(F.data == "direction_installation")
async def direction_installation(callback: CallbackQuery, state: FSMContext):
    from .installation import start_installation

    await start_installation(callback, state)


@router.callback_query(F.data == "direction_passport")
async def direction_passport(callback: CallbackQuery, state: FSMContext):
    from .passport import start_passport
    await start_passport(callback, state)

@router.callback_query(F.data == "direction_supply")
async def direction_supply(callback: CallbackQuery, state: FSMContext):
    from .supply import start_supply
    await start_supply(callback, state)

@router.callback_query(F.data == "direction_economics")
async def direction_economics(callback: CallbackQuery, state: FSMContext):
    from .economics import start_economics
    await start_economics(callback, state)
