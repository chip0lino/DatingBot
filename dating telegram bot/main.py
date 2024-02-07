import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
# from dotenv import load_dotenv, find_dotenv

from handlers import register_handler, my_profile, handlers, keyboards

# load_dotenv(find_dotenv())
bot = Bot(token=config.BOT_TOKEN)


async def main() -> None:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logging.basicConfig(level=logging.INFO)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    dp.include_routers(
        register_handler.router,
        my_profile.router,
        handlers.router,
        keyboards.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot Stopped.')