from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.db import Database
from keyboards.inline import (get_production_menu_keyboard,
                              get_red_reason_keyboard, get_efficiency_keyboard)

from .states import (AssemblyFSM, AuxiliaryFSM, PreparatoryFSM, RviFSM,
                     WeldingFSM)

router = Router()


@router.callback_query(F.data == "back_to_production")
async def back_to_production(callback: CallbackQuery, state: FSMContext, db: Database):
    await state.clear()
    workshops = await db.get_workshops_prod()
    text = "⚙️ Производство\n\nВыберите цех:"
    await callback.message.edit_text(
        text, reply_markup=get_production_menu_keyboard(workshops)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_red_reason")
async def back_to_red_reason(callback: CallbackQuery, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state.startswith("WeldingFSM"):
        await state.set_state(WeldingFSM.red_reason)
    elif cur_state.startswith("AuxiliaryFSM"):
        await state.set_state(AuxiliaryFSM.red_reason)
    elif cur_state.startswith("PreparatoryFSM"):
        await state.set_state(PreparatoryFSM.red_reason)
    elif cur_state.startswith("AssemblyFSM"):
        await state.set_state(AssemblyFSM.red_reason)
    elif cur_state.startswith("RviFSM"):
        await state.set_state(RviFSM.red_reason)
    else:
        await state.clear()
    await callback.message.edit_text(
        "Выберите причину:", reply_markup=get_red_reason_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_efficiency")
async def back_to_efficiency(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        class_name = current_state.split(':')[0]
        await state.set_state(f"{class_name}:efficiency")
    else:
        await state.clear()
    await callback.message.edit_text("Оцените статус своей задачи по проекту:", reply_markup=get_efficiency_keyboard())
    await callback.answer()
