from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.db import Database
from keyboards.inline import get_main_menu_keyboard
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, db: Database):
    await db.add_user(message.from_user.id, message.from_user.username)
    text = "🏭 **Производственный бот**\n\nВыберите направление:"
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
    logger.info(f"User {message.from_user.id} started")