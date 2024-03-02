from aiogram import Router, F, types, Bot
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os

import handlers.keyboards as kb
import database.database as bd

router = Router()

class Likes_state(StatesGroup):
    ank_id = State()
    accept_or_reject = State()
    username = State()
    stop_or_cont = State()

#отправка случайной анкеты юзеру
@router.message(F.text == 'Смотреть анкеты')
async def look_ankets(message: Message):
    ank = await bd.get_anket(message.from_user.id)
    if ank != 'no':
        faculty=ank[10]
        if faculty == 'LF':
            faculty = 'ЮФ'
        if faculty == 'FEIF':
            faculty = 'ФЭИФ'
        if faculty == 'GF':
            faculty = 'ГФ'
        if faculty == 'BTB':
            faculty = 'ФБТДиЭБ'
        if faculty == 'FIPM':
            faculty = 'ФИПМ'
        if faculty == 'FSTIG':
            faculty = 'ФСТИГ'
        if faculty == 'FU':
            faculty = 'ФУ'
        current_dir = os.path.split(os.path.dirname(__file__))[0] # путь к папке проекта
        await message.answer_photo(photo=types.input_file.FSInputFile(f"{current_dir}/photos/{ank[6]}.jpg"), caption=f'🔎 {ank[3]}, {ank[5]}, {ank[8]}\n\n🧑🏻‍🎓 Учится на {ank[9]} курсе {ank[11]} {faculty}\n\n📎 Описание анкеты: {ank[7]}', reply_markup=kb.view)
    else:
        await message.answer('Вы посмотрели все анкеты. Возможно в следующий раз их будет больше 😞', reply_markup=kb.last)

# если юзеру нравится анкета
@router.message(F.text == 'Нравится')
async def like(message: Message, bot: Bot):
    last_id = await bd.like_ank(message.from_user.id)
    await message.answer('💌')
    try:
        await bot.send_message(chat_id=last_id, text="Невероятно!\nВашу анкету оценили. зайдите в Мой профиль -> Меня оценили, чтобы посмотреть кто это")
        await message.answer('💕')
    except:
        print(f'Увы, пользователь {last_id} не пользуется ботом. Сообщение не отправлено 😩')
    await bd.do_not_show(message.from_user.id)
    await look_ankets(message)

# пропуск анкеты
@router.message(F.text == 'Пропустить')
async def skip(message: Message):
    await bd.do_not_show(message.from_user.id)
    await message.answer('❌')
    await look_ankets(message)

# возвращение в главное меню
@router.message(F.text == "Назад в меню")
async def back_to_menu(message: Message):
    await message.answer('Возвращаюсь в меню', reply_markup=kb.main)

# отправляет анкету человека который оценил юзера
async def ank_who_like(people_id, message, state, user_id):
    ank = await bd.like_person(people_id)
    current_dir = os.path.split(os.path.dirname(__file__))[0] # путь к папке проекта
    await message.answer_photo(photo=types.input_file.FSInputFile(f"{current_dir}/photos/{ank[6]}.jpg"),
                                    caption=f'Имя: {ank[3]}\nВозраст: {ank[5]}\nОписание анкеты: {ank[7]}\nЗЗ: {ank[8]}\nКурс: {ank[9]}\nФакультет: {ank[10]}\nНазначение: {ank[11]}',
                                    reply_markup=kb.who_like)
    stop_or_continue = await bd.delete_one_like(user_id)
    await state.set_state(Likes_state.accept_or_reject)
    await state.update_data(username=ank[1])
    await state.update_data(ank_id=people_id)
    if stop_or_continue == "cont":
        await state.update_data(stop_or_cont="cont")
    elif stop_or_continue == "stop":
        await state.update_data(stop_or_cont="stop")

# кто оценил юзера
@router.message(F.text == 'Меня оценили')
async def my_likes(message: Message, state: FSMContext):
    like = await bd.who_like(message.from_user.id)
    if like == "no likes":
        await message.answer("За это время вы не прибавили популярности 😭😭😭\n\nНовых оценок нет.")
    else:
        people_id = like[0]
        user_id = message.from_user.id
        await ank_who_like(people_id, message, state, user_id)

# ответная оценка юзера или пропуск анкеты
@router.message(Likes_state.accept_or_reject)
async def accep_or_reject(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    data = await state.get_data()
    if message.text == "Оценить ответно":
        people_id = data.get("ank_id")
        username = data.get("username")
        ank_id = data.get("ank_id")
        await message.answer(f"Вы оценили @{username} в ответ.\n\nМожет пора заводить детей? 👶")
        try:
            await bot.send_message(chat_id=ank_id, text = f"Ого! У вас случился мэтч! Пользователь {message.from_user.username} оценил вас в ответ.")
            await message.answer('💞')
        except:
            print(f'Увы, пользователь {ank_id} не пользуется ботом. Сообщение не может быть отправлено 😩')
    elif message.text == "Следующая анкета":
        await message.answer("Увы, вы не оценили человека в ответ. А ведь он может уйти в депрессию 😭\nНу ладно, вот следующая анкета:")
    stop_or_cont = data.get("stop_or_cont")
    like = await bd.who_like(message.from_user.id)
    people_id = like[0]
    if stop_or_cont == "cont":
        await ank_who_like(people_id, message, state, user_id)
    elif stop_or_cont=="stop":
        await message.answer("Вы посмотрели все свои оценки. Тут больше ничего нет 😞", reply_markup=kb.main)
        await state.clear()