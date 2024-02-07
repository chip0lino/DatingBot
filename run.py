import asyncio
from aiogram import Dispatcher
from handlers import router, bot
import database as db

async def on_startup(): # подключение бд
    await db.db_start()

async def main(): # создание бота, роутера
    bot_ls = bot
    dp = Dispatcher()
    dp.include_router(router)
    print("Бот запущен")
    await dp.start_polling(bot_ls)

if __name__ == '__main__': # входящие обновления
    try:
        asyncio.run(main())
        asyncio.run(on_startup())
    except KeyboardInterrupt:
        print('Exit')