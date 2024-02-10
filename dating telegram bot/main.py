import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
# from dotenv import load_dotenv, find_dotenv
import config
import handlers.handlers as handlers
import handlers.keyboards as keyboards
import handlers.my_profile as my_profile
import handlers.register_handler as register_handler
#from handlers import register_handler, my_profile, handlers, keyboards

# load_dotenv(find_dotenv())
bot = Bot(token=config.BOT_TOKEN)


async def main() -> None:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp.include_routers(
        register_handler.router,
        my_profile.router,
        handlers.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot Stopped.')