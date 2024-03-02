import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
import handlers.likes_handlers as likes_handlers
import handlers.my_profile as my_profile
import handlers.register_handler as register_handler
import handlers.report_handlers as report_handlers
import handlers.admin_panel as admin_panel

bot = Bot(token=config.BOT_TOKEN)


async def main() -> None:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp.include_routers(
        admin_panel.router,
        likes_handlers.router,
        register_handler.router,
        my_profile.router,
        report_handlers.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot Stopped.')