from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS
from database.db import Database
from keyboards.inline import (get_admin_menu_keyboard, get_cancel_keyboard,
                              get_main_menu_keyboard,
                              get_workshop_projects_keyboard,
                              get_workshops_keyboard)
from utils.logger_conf import setup_logger

from .states import AdminFSM

logger = setup_logger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("projects"))
async def cmd_projects(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return
    await message.answer(
        "🛠 Администрирование проектов\n\nЧто хотите сделать?",
        reply_markup=get_admin_menu_keyboard(),
    )


@router.callback_query(F.data == "admin_add_project")
async def admin_add_project_start(
    callback: CallbackQuery, state: FSMContext, db: Database
):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    workshops = await db.get_workshops()
    if not workshops:
        await callback.message.edit_text("❌ Список цехов пуст.")
        await callback.answer()
        return
    keyboard = get_workshops_keyboard(workshops, prefix="admin_workshop_")
    await callback.message.edit_text(
        "Выберите цех для добавления проекта:", reply_markup=keyboard
    )
    await state.set_state(AdminFSM.waiting_for_workshop_add)
    await callback.answer()


@router.callback_query(
    AdminFSM.waiting_for_workshop_add, F.data.startswith("admin_workshop_")
)
async def admin_workshop_selected(callback: CallbackQuery, state: FSMContext):
    workshop_code = callback.data.replace("admin_workshop_", "")
    await state.update_data(workshop_code=workshop_code)
    await callback.message.edit_text(
        "Введите название нового проекта:", reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminFSM.waiting_for_project_name)
    await callback.answer()


@router.message(AdminFSM.waiting_for_project_name)
async def admin_project_name(message: Message, state: FSMContext, db: Database):
    project_name = message.text.strip()
    if not project_name:
        await message.answer(
            "❌ Название не может быть пустым. Попробуйте ещё раз:",
            reply_markup=get_cancel_keyboard(),
        )
        return
    data = await state.get_data()
    workshop_code = data["workshop_code"]
    success = await db.add_workshop_project(workshop_code, project_name)
    if success:
        await message.answer(
            f"✅ Проект «{project_name}» добавлен для цеха {workshop_code}."
        )
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer(
            f"❌ Проект «{project_name}» уже существует для этого цеха. Попробуйте другое название.",
            reply_markup=get_cancel_keyboard(),
        )


@router.callback_query(F.data == "admin_remove_project")
async def admin_remove_project_start(
    callback: CallbackQuery, state: FSMContext, db: Database
):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав", show_alert=True)
        return
    workshops = await db.get_workshops()
    if not workshops:
        await callback.message.edit_text("❌ Список цехов пуст.")
        await callback.answer()
        return
    keyboard = get_workshops_keyboard(workshops, prefix="admin_remove_workshop_")
    await callback.message.edit_text(
        "Выберите цех для удаления проекта:", reply_markup=keyboard
    )
    await state.set_state(AdminFSM.waiting_for_workshop_remove)
    await callback.answer()


@router.callback_query(
    AdminFSM.waiting_for_workshop_remove, F.data.startswith("admin_remove_workshop_")
)
async def admin_remove_workshop_selected(
    callback: CallbackQuery, state: FSMContext, db: Database
):
    workshop_code = callback.data.replace("admin_remove_workshop_", "")
    projects = await db.get_workshop_projects(workshop_code)
    if not projects:
        await callback.message.edit_text("В этом цехе нет проектов.")
        await state.clear()
        await callback.answer()
        return
    keyboard = get_workshop_projects_keyboard(projects, prefix="admin_remove_project_")
    await callback.message.edit_text(
        "Выберите проект для удаления:", reply_markup=keyboard
    )
    await state.update_data(workshop_code=workshop_code)
    await state.set_state(AdminFSM.waiting_for_project_remove)
    await callback.answer()


@router.callback_query(
    AdminFSM.waiting_for_project_remove, F.data.startswith("admin_remove_project_")
)
async def admin_remove_project(
    callback: CallbackQuery, state: FSMContext, db: Database
):
    project_code = callback.data.replace("admin_remove_project_", "")
    data = await state.get_data()
    workshop_code = data["workshop_code"]
    await db.delete_workshop_project(workshop_code, project_code)
    await callback.message.edit_text("✅ Проект удалён.")
    await state.clear()
    await callback.message.answer(
        "Главное меню:", reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Операция отменена.")
    await callback.message.answer(
        "Главное меню:", reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
