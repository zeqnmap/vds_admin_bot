import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN, DATABASE_PATH
from database.db import Database
from handlers import main_callback_router, start_router
from utils.logger_conf import setup_logger

logger = setup_logger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="projects", description="Управление проектами (админ)"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    db = Database(DATABASE_PATH)
    dp.include_router(start_router)
    dp.include_router(main_callback_router)
    dp["db"] = db
    await db.create_tables()
    await set_bot_commands(bot)
    logger.info("Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
