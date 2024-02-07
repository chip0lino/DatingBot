from aiogram import Router, F, Bot, types
import config
from aiogram.types import Message
import keyboards as kb
import database as bd


bot = Bot(token=config.BOT_TOKEN)
router = Router()

#отправка случайное анкеты юзеру
@router.message(F.text == 'Смотреть анкеты')
async def look_ankets(message: Message):
    ank = await bd.get_anket(message.from_user.id)
    if ank != 'no':
        await message.answer_photo(photo=types.input_file.FSInputFile(f"photos/{ank[1]}.jpg"), caption=f'Имя: {ank[2]}\nВозраст: {ank[4]}\nОписание анкеты: {ank[5]}\nЗЗ: {ank[6]}\nКурс: {ank[7]}\nФакультет: {ank[8]}', reply_markup=kb.view)
    else:
        await message.answer('Вы посмотрели все анкеты', reply_markup=kb.last)

# если юзеру нравится анкета
@router.message(F.text == 'Нравится')
async def like(message: Message):
    await bd.like_ank(message.from_user.id)
    await message.answer('💌')
    await bd.do_not_show(message.from_user.id)
    await look_ankets(message)

# пропуск анкеты
@router.message(F.text == 'Пропустить')
async def like(message: Message):
    await bd.do_not_show(message.from_user.id)
    await message.answer('❌')
    await look_ankets(message)

# возвращение в главное меню
@router.message(F.text == "Назад в меню")
async def back_to_menu(message: Message):
    await message.answer('Возвращаюсь в меню', reply_markup=kb.main)
