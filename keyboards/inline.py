from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from database.models import Workshop

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Продажи", callback_data="direction_sales")
    builder.button(text="🎨 Креатив", callback_data="direction_creative")
    builder.button(text="✏️ КБ", callback_data="direction_kb")
    builder.button(text="⚙️ Производство", callback_data="direction_production")
    builder.button(text="🚛 Логистика", callback_data="direction_logistics")
    builder.button(text="🛠 Монтаж", callback_data="direction_installation")
    builder.adjust(2)
    return builder.as_markup()

def get_production_menu_keyboard(workshops: List[Workshop]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for w in workshops:
        builder.button(text=w.name, callback_data=f"workshop_{w.code}")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(2)
    return builder.as_markup()

def get_under_construction_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    return builder.as_markup()

def get_projects_keyboard(projects) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in projects:
        if hasattr(p, 'name') and hasattr(p, 'code'):
            name = p.name
            code = p.code
        elif isinstance(p, dict):
            name = p.get('name')
            code = p.get('code')
        else:
            continue
        builder.button(text=name, callback_data=f"project_{code}")
    builder.button(text="🔙 Назад", callback_data="back_to_production")
    builder.adjust(2)
    return builder.as_markup()

def get_efficiency_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Зелёный", callback_data="efficiency_green")
    builder.button(text="🔴 Красный", callback_data="efficiency_red")
    builder.adjust(2)
    return builder.as_markup()

def get_red_reason_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Вопросы", callback_data="red_questions")
    builder.button(text="⚠️ Проблемы", callback_data="red_problems")
    builder.button(text="🔙 Назад", callback_data="back_to_production")
    builder.adjust(2)
    return builder.as_markup()

def get_problem_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Сроки", callback_data="problem_terms")
    builder.button(text="🚚 Поставки", callback_data="problem_supply")
    builder.button(text="👥 Персонал", callback_data="problem_staff")
    builder.button(text="❓ Другое", callback_data="problem_other")
    builder.button(text="🔙 Назад", callback_data="back_to_red_reason")
    builder.adjust(2)
    return builder.as_markup()

def get_problem_desc_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="back_to_red_reason")
    return builder.as_markup()

def get_attach_photo_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📎 Приложить фото", callback_data="attach_photo")
    builder.button(text="⏩ Пропустить", callback_data="skip_photo")
    builder.adjust(2)
    return builder.as_markup()

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить проект", callback_data="admin_add_project")
    builder.button(text="➖ Удалить проект", callback_data="admin_remove_project")
    builder.button(text="🔙 Отмена", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_workshops_keyboard(workshops, prefix="workshop_"):
    builder = InlineKeyboardBuilder()
    for w in workshops:
        builder.button(text=w.name, callback_data=f"{prefix}{w.code}")
    builder.button(text="🔙 Назад", callback_data="admin_cancel")
    builder.adjust(2)
    return builder.as_markup()

def get_workshop_projects_keyboard(projects, prefix="project_"):
    builder = InlineKeyboardBuilder()
    for p in projects:
        builder.button(text=p['name'], callback_data=f"{prefix}{p['code']}")
    builder.button(text="🔙 Назад", callback_data="admin_cancel")
    builder.adjust(2)
    return builder.as_markup()

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Отмена", callback_data="admin_cancel")
    return builder.as_markup()