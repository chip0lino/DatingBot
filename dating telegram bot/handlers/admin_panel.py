import asyncio
from os import read

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, \
	ReplyKeyboardRemove

from config import ADMIN_ID
from database.database import cursor, conn
from handlers.inline_kb_admin import admin_panel_for_admins, create_keyboard, user_checkout, redaction_inline, \
	user_checkout_push, redaction_inline_view
from state.register_state import Redaction_inline_mode, Touch, Redaction_inline_view

router = Router()


@router.message(Command('admin'))
async def admin_panel(message: Message, bot: Bot, state: FSMContext):
	user_id: int = message.from_user.id
	nickname = message.from_user.full_name
	user_link = f'<a href="tg://user?id={user_id}">{nickname}</a>'

	if user_id not in ADMIN_ID:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ У вас нет доступа к данной команде'
		)

	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'🌟 <b>{user_link}</b>, добро пожаловать в админ панель!',
			reply_markup=admin_panel_for_admins()
		)


@router.callback_query(F.data == 'anket_admin_view')
async def admin_view_ankets(callback: CallbackQuery, bot: Bot, state: FSMContext):
	await state.clear()
	keyboard_markup, user_dict = create_keyboard()

	user_info_lines = []
	for user_id, user_data in user_dict.items():
		nickname = user_data['nickname']
		faculty = user_data['faculty']
		user_info_lines.append(f"{user_id}: <b>{nickname}</b>\nФакультет: {faculty}")
	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text="Выберите id пользователя:\n\n" + "\n\n".join(user_info_lines),
		reply_markup=keyboard_markup
	)


@router.callback_query(F.data.startswith('prev_'))
async def process_callback_prev(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    page = int(callback.data.split('_')[1])
    keyboard_markup, user_dict = create_keyboard(page)

    user_info_lines = []
    for user_id, user_data in user_dict.items():
        nickname = user_data['nickname']
        faculty = user_data['faculty']
        user_info_lines.append(f"{user_id}: <b>{nickname}</b>\nФакультет: {faculty}")

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
	    message_id=callback.message.message_id,
        text="Выберите id пользователя:\n\n" + "\n\n".join(user_info_lines),
    )
    await bot.edit_message_reply_markup(callback.message.chat.id,
                                        callback.message.message_id,
                                        reply_markup=keyboard_markup)



@router.callback_query(F.data.startswith('next_'))
async def process_callback_next(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    page = int(callback.data.split('_')[1])
    keyboard_markup, user_dict = create_keyboard(page)

    user_info_lines = []
    for user_id, user_data in user_dict.items():
        nickname = user_data['nickname']
        faculty = user_data['faculty']
        user_info_lines.append(f"{user_id}: <b>{nickname}</b>\nФакультет: {faculty}")

    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
	    message_id=callback.message.message_id,
        text="Выберите id пользователя:\n\n" + "\n\n".join(user_info_lines)
    )
    await bot.edit_message_reply_markup(callback.message.chat.id,
                                        callback.message.message_id,
                                        reply_markup=keyboard_markup)



@router.callback_query(F.data.startswith('user_call_'))
async def call_for_user_ids(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id_from_call = str(callback.data.split('_')[2])
    await state.clear()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id_from_call,))
    user_data = cursor.fetchone()

    if user_data:
        user_id, _, nickname, name, gender, age, photo, anketa_description, zodiac_sign, kurs, faculty, grade, _ = user_data

    user_link = f'<a href="tg://user?id={user_id}">{nickname}</a>'
    path = f'C:\\Users\\light\\PycharmProjects\\tgbotikaio3\\photos/{photo}.jpg'

    if gender == "male":
        gender = 'Мужской'
    if gender == "female":
        gender = 'Женский'
    if faculty == 'LF':
        faculty = 'ЮФ'
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

    try:
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=FSInputFile(path),
            caption=f"Анкета пользователя <b>{user_link}</b>:\n\n"
                    f"Имя: <b>{name}</b>\n"
                    f"Гендер: <b>{gender}</b>\n"
                    f"возраст: <b>{age}</b>\n"
                    f'Описание анкеты: <b>{anketa_description}</b>\n'
                    f'Знак зодиака: <b>{zodiac_sign}</b>\n'
                    f'Курс: <b>{kurs}</b>\n'
                    f'Факультет: <b>{faculty}</b>\n'
                    f'Назначение: <b>{grade}</b>',
            reply_markup=user_checkout()
        )
        await bot.delete_message(
	        chat_id=callback.message.chat.id,
	        message_id=callback.message.message_id
        )
        await state.update_data(path=path)
        await state.update_data(name=name)
        await state.update_data(gender=gender)
        await state.update_data(age=age)
        await state.update_data(anketa_description=anketa_description)
        await state.update_data(zodiac_sign=zodiac_sign)
        await state.update_data(kurs=kurs)
        await state.update_data(faculty=faculty)
        await state.update_data(grade=grade)
        await state.update_data(user_id_from_call=user_id_from_call)
        await state.update_data(nickname=nickname)
    except:
        await callback.answer(
	        text='Данная анкета не существует!',
	        show_alert=True
        )


@router.callback_query(F.data == 'redaction_with_inline')
async def call_redaction(callback: CallbackQuery, bot: Bot, state: FSMContext):
	data = await state.get_data()
	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaPhoto(
			media=FSInputFile(path),
			caption=caption
		),
		reply_markup=redaction_inline()

	)



@router.callback_query(F.data == 'red_name')
async def call_redaction_name(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.name)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Напиши имя пользователю!"
	)


@router.message(Redaction_inline_mode.name)
async def call_redaction_name(message: Message, bot: Bot, state: FSMContext):
	name = message.text
	await state.update_data(name=name)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_gender')
async def call_redaction_gender(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.gender)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Женский')],
			[KeyboardButton(text='Мужской')],
		],
		resize_keyboard=True,
	)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери гендер пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_mode.gender)
async def call_redaction_gender(message: Message, bot: Bot, state: FSMContext):
	gender = message.text
	await state.update_data(gender=gender)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	if gender == "Мужской":
		gender = 'male'
	if gender == "Женский":
		gender = 'female'

	cursor.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_age')
async def call_redaction_age(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.age)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери возраст пользователю!"
	)


@router.message(Redaction_inline_mode.age)
async def call_redaction_age(message: Message, bot: Bot, state: FSMContext):
	age = message.text
	await state.update_data(age=age)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET age = ? WHERE user_id = ?", (age, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_photo')
async def call_redaction_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.photo)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери фоточку пользователю!"
	)


@router.message(Redaction_inline_mode.photo)
async def call_redaction_age(message: Message, bot: Bot, state: FSMContext):
	if message.photo:
		photo = message.photo[-1]
		file_id = photo.file_id
		file_info = await bot.get_file(file_id)
		file_path = file_info.file_path
		path = f'C:\\Users\\light\\PycharmProjects\\tgbotikaio3\\photos/{file_id}.jpg'
		await bot.download_file(file_path, path)
		await state.update_data(path=path)

		data = await state.get_data()
		user_id = data.get('user_id_from_call')

		cursor.execute("UPDATE users SET photo = ? WHERE user_id = ?", (file_id, user_id))
		conn.commit()

		name = data.get('name')
		path = data.get('path')
		gender = data.get('gender')
		age = data.get('age')
		anketa_description = data.get('anketa_description')
		zodiac_sign = data.get('zodiac_sign')
		kurs = data.get('kurs')
		faculty = data.get('faculty')
		grade = data.get('grade')

		caption = (f'Что изменим в данной анкете?\n\n'
		           f"Имя: <b>{name}</b>\n"
		           f"Гендер: <b>{gender}</b>\n"
		           f"возраст: <b>{age}</b>\n"
		           f'Описание анкеты: <b>{anketa_description}</b>\n'
		           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
		           f'Курс: <b>{kurs}</b>\n'
		           f'Факультет: <b>{faculty}</b>\n'
		           f'Назначение: <b>{grade}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			photo=FSInputFile(path),
			caption=caption,
			reply_markup=redaction_inline())
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Пожалуйста, отправьте фотографию.'
		)


@router.callback_query(F.data == 'red_sign_zodiac')
async def call_redaction_zodiac(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.zodiak_sign)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="Овен"), KeyboardButton(text='Телец'), KeyboardButton(text='Близнецы'),
			 KeyboardButton(text='Рак')],
			[KeyboardButton(text='Лев'), KeyboardButton(text='Дева'), KeyboardButton(text='Весы'),
			 KeyboardButton(text='Скорпион')],
			[KeyboardButton(text='Стрелец'), KeyboardButton(text='Козерог'), KeyboardButton(text='Водолей'),
			 KeyboardButton(text='Рыбы')],
		],
		resize_keyboard=True
	)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери ЗЗ пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_mode.zodiak_sign)
async def call_redaction_zodiac(message: Message, bot: Bot, state: FSMContext):
	zodiac_sign = message.text
	await state.update_data(zodiac_sign=zodiac_sign)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET zodiac_sign = ? WHERE user_id = ?", (zodiac_sign, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_descr')
async def call_redaction_description(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_mode.anketa_description)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Описание пользователю!"
	)


@router.message(Redaction_inline_mode.anketa_description)
async def call_redaction_gender(message: Message, bot: Bot, state: FSMContext):
	anketa_description = message.text
	await state.update_data(anketa_description=anketa_description)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET anketa_description = ? WHERE user_id = ?", (anketa_description, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_kurs')
async def call_redaction_kurs(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="1"), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
			 KeyboardButton(text='5')],
		],
		resize_keyboard=True
	)
	await state.set_state(Redaction_inline_mode.kurs)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Курс пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_mode.kurs)
async def call_redaction_kurs(message: Message, bot: Bot, state: FSMContext):
	kurs = message.text
	await state.update_data(kurs=kurs)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET kurs = ? WHERE user_id = ?", (kurs, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_facultet')
async def call_redaction_facultet(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='ЮФ'), KeyboardButton(text='ГФ'), KeyboardButton(text='ФБТДиЭБ')],
			[KeyboardButton(text='ФИПМ'), KeyboardButton(text='ФСТИГ'), KeyboardButton(text='ФУ')],
		],
		resize_keyboard=True,
	)
	await state.set_state(Redaction_inline_mode.faculty)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Факультет пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_mode.faculty)
async def call_redaction_faculty(message: Message, bot: Bot, state: FSMContext):
	faculty = message.text
	await state.update_data(faculty=faculty)

	if faculty == 'ЮФ':
		faculty = 'LF'
	if faculty == 'ГФ':
		faculty = 'GF'
	if faculty == 'ФБТДиЭБ':
		faculty = 'BTB'
	if faculty == 'ФИПМ':
		faculty = 'FIPM'
	if faculty == 'ФСТИГ':
		faculty = 'FSTIG'
	if faculty == 'ФУ':
		faculty = 'FU'

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET faculty = ? WHERE user_id = ?", (faculty, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'red_naznachenie')
async def call_redaction_naznazh(callback: CallbackQuery, bot: Bot, state: FSMContext):
	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Бакалавриат')],
			[KeyboardButton(text='Магистратура')],
		],
		resize_keyboard=True,
	)
	await state.set_state(Redaction_inline_mode.grade)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Назначение пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_mode.grade)
async def call_redaction_grade(message: Message, bot: Bot, state: FSMContext):
	grade = message.text
	await state.update_data(grade=grade)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET grade = ? WHERE user_id = ?", (grade, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline())


@router.callback_query(F.data == 'blocked_inline')
async def call_blocked(callback: CallbackQuery, bot: Bot, state: FSMContext):
	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
	conn.commit()
	await state.clear()

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await bot.send_message(
		chat_id=callback.message.chat.id,
		text='Пользователь успешно удалён из базы данных!',
		reply_markup=admin_panel_for_admins()
	)


@router.callback_query(F.data == 'view_touch_to')
async def touched_user_ids(callback: CallbackQuery, bot: Bot, state: FSMContext):
	await state.set_state(Touch.touch_view)

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await bot.send_message(
		chat_id=callback.message.chat.id,
		text='Напишите никнейм или юзернейм пользователя!'
	)

@router.message(Touch.touch_view)
async def touch_view(message: Message, bot: Bot, state: FSMContext):
	nickname = message.text

	if message.text.startswith('@'):
		await bot.send_message(
			chat_id=message.chat.id,
			text='Поиск пользователя...🔎'
		)
		await asyncio.sleep(1)
		username = nickname[1:]

		cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
		result = cursor.fetchone()

		if result:
			user_id_from_call = result[0]
			await state.update_data(user_id_from_call=user_id_from_call)
			await bot.send_message(
				chat_id=message.chat.id,
				text=f"Найден пользователь с именем @<b>{username}</b>. User ID: {user_id_from_call}"
			)
			await asyncio.sleep(1)

			cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id_from_call,))
			results = cursor.fetchall()

			for row in results:
				_, _, _, name, gender, age, photo, anketa_description, zodiac_sign, kurs, faculty, grade, _ = row

				path = f'C:\\Users\\light\\PycharmProjects\\tgbotikaio3\\photos/{photo}.jpg'

				if gender == "male":
					gender = 'Мужской'
				if gender == "female":
					gender = 'Женский'
				if faculty == 'LF':
					faculty = 'ЮФ'
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

				await bot.send_photo(
					chat_id=message.chat.id,
					caption=f"Анкета пользователя:\n\n"
					        f"Имя: <b>{name}</b>\n"
					        f"Гендер: <b>{gender}</b>\n"
					        f"Возраст: <b>{age}</b>\n"
					        f"Описанин: <b>{anketa_description}</b>\n"
					        f"ЗЗ: <b>{zodiac_sign}</b>\n"
					        f"Курс: <b>{kurs}</b>\n"
					        f"Факультет: <b>{faculty}</b>\n"
					        f"Назначение: <b>{grade}</b>\n",
					photo=FSInputFile(path),
					reply_markup=user_checkout_push()
				)
				await state.update_data(path=path)
				await state.update_data(name=name)
				await state.update_data(gender=gender)
				await state.update_data(age=age)
				await state.update_data(anketa_description=anketa_description)
				await state.update_data(zodiac_sign=zodiac_sign)
				await state.update_data(kurs=kurs)
				await state.update_data(faculty=faculty)
				await state.update_data(grade=grade)
				await state.update_data(user_id_from_call=user_id_from_call)
				await state.update_data(nickname=nickname)
		else:
			await bot.send_message(
				chat_id=message.chat.id,
				text=f"Пользователь с именем {nickname} не найден."
			)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='Поиск пользователя...🔎'
		)
		await asyncio.sleep(1)
		cursor.execute("SELECT user_id FROM users WHERE nickname = ?", (nickname,))
		result = cursor.fetchone()

		if result:
			user_id_from_call = result[0]
			await state.update_data(user_id_from_call=user_id_from_call)
			await bot.send_message(
				chat_id=message.chat.id,
				text=f"Найден пользователь с именем <b>{nickname}</b>. User ID: {user_id_from_call}"
			)
			await asyncio.sleep(1)

			cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id_from_call,))
			results = cursor.fetchall()

			for row in results:
				_, _, _, name, gender, age, photo, anketa_description, zodiac_sign, kurs, faculty, grade, _ = row

				path = f'C:\\Users\\light\\PycharmProjects\\tgbotikaio3\\photos/{photo}.jpg'

				if gender == "male":
					gender = 'Мужской'
				if gender == "female":
					gender = 'Женский'
				if faculty == 'LF':
					faculty = 'ЮФ'
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

				await bot.send_photo(
					chat_id=message.chat.id,
					caption=f"Анкета пользователя:\n\n"
					        f"Имя: <b>{name}</b>\n"
					        f"Гендер: <b>{gender}</b>\n"
					        f"Возраст: <b>{age}</b>\n"
					        f"Описанин: <b>{anketa_description}</b>\n"
					        f"ЗЗ: <b>{zodiac_sign}</b>\n"
					        f"Курс: <b>{kurs}</b>\n"
					        f"Факультет: <b>{faculty}</b>\n"
					        f"Назначение: <b>{grade}</b>\n",
					photo=FSInputFile(path),
					reply_markup=user_checkout_push()
				)
				await state.update_data(path=path)
				await state.update_data(name=name)
				await state.update_data(gender=gender)
				await state.update_data(age=age)
				await state.update_data(anketa_description=anketa_description)
				await state.update_data(zodiac_sign=zodiac_sign)
				await state.update_data(kurs=kurs)
				await state.update_data(faculty=faculty)
				await state.update_data(grade=grade)
				await state.update_data(user_id_from_call=user_id_from_call)
				await state.update_data(nickname=nickname)
		else:
			await bot.send_message(
				chat_id=message.chat.id,
				text=f"Пользователь с именем {nickname} не найден."
			)


@router.callback_query(F.data == 'blocked_inline_view')
async def call_blocked_view(callback: CallbackQuery, bot: Bot, state: FSMContext):
	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
	conn.commit()
	await state.clear()

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await bot.send_message(
		chat_id=callback.message.chat.id,
		text='Пользователь успешно удалён из базы данных!',
		reply_markup=admin_panel_for_admins()
	)


@router.callback_query(F.data == 'redaction_with_inline_view')
async def call_redaction_view(callback: CallbackQuery, bot: Bot, state: FSMContext):
	data = await state.get_data()
	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.edit_message_media(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id,
		media=InputMediaPhoto(
			media=FSInputFile(path),
			caption=caption
		),
		reply_markup=redaction_inline_view()

	)


@router.callback_query(F.data == 'red_name_view')
async def call_redaction_name(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.name)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Напиши имя пользователю!"
	)


@router.message(Redaction_inline_view.name)
async def call_redaction_name(message: Message, bot: Bot, state: FSMContext):
	name = message.text
	await state.update_data(name=name)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_gender_view')
async def call_redaction_gender(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.gender)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Женский')],
			[KeyboardButton(text='Мужской')],
		],
		resize_keyboard=True,
	)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери гендер пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_view.gender)
async def call_redaction_gender(message: Message, bot: Bot, state: FSMContext):
	gender = message.text
	await state.update_data(gender=gender)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	if gender == "Мужской":
		gender = 'male'
	if gender == "Женский":
		gender = 'female'

	cursor.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_age_view')
async def call_redaction_age(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.age)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери возраст пользователю!"
	)


@router.message(Redaction_inline_view.age)
async def call_redaction_age(message: Message, bot: Bot, state: FSMContext):
	age = message.text
	await state.update_data(age=age)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET age = ? WHERE user_id = ?", (age, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_photo_view')
async def call_redaction_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.photo)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери фоточку пользователю!"
	)


@router.message(Redaction_inline_view.photo)
async def call_redaction_age(message: Message, bot: Bot, state: FSMContext):
	if message.photo:
		photo = message.photo[-1]
		file_id = photo.file_id
		file_info = await bot.get_file(file_id)
		file_path = file_info.file_path
		path = f'C:\\Users\\light\\PycharmProjects\\tgbotikaio3\\photos/{file_id}.jpg'
		await bot.download_file(file_path, path)
		await state.update_data(path=path)

		data = await state.get_data()
		user_id = data.get('user_id_from_call')

		cursor.execute("UPDATE users SET photo = ? WHERE user_id = ?", (file_id, user_id))
		conn.commit()

		name = data.get('name')
		path = data.get('path')
		gender = data.get('gender')
		age = data.get('age')
		anketa_description = data.get('anketa_description')
		zodiac_sign = data.get('zodiac_sign')
		kurs = data.get('kurs')
		faculty = data.get('faculty')
		grade = data.get('grade')

		caption = (f'Что изменим в данной анкете?\n\n'
		           f"Имя: <b>{name}</b>\n"
		           f"Гендер: <b>{gender}</b>\n"
		           f"возраст: <b>{age}</b>\n"
		           f'Описание анкеты: <b>{anketa_description}</b>\n'
		           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
		           f'Курс: <b>{kurs}</b>\n'
		           f'Факультет: <b>{faculty}</b>\n'
		           f'Назначение: <b>{grade}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			photo=FSInputFile(path),
			caption=caption,
			reply_markup=redaction_inline_view())
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Пожалуйста, отправьте фотографию.'
		)


@router.callback_query(F.data == 'red_sign_zodiac_view')
async def call_redaction_zodiac(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.zodiak_sign)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="Овен"), KeyboardButton(text='Телец'), KeyboardButton(text='Близнецы'),
			 KeyboardButton(text='Рак')],
			[KeyboardButton(text='Лев'), KeyboardButton(text='Дева'), KeyboardButton(text='Весы'),
			 KeyboardButton(text='Скорпион')],
			[KeyboardButton(text='Стрелец'), KeyboardButton(text='Козерог'), KeyboardButton(text='Водолей'),
			 KeyboardButton(text='Рыбы')],
		],
		resize_keyboard=True
	)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери ЗЗ пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_view.zodiak_sign)
async def call_redaction_zodiac(message: Message, bot: Bot, state: FSMContext):
	zodiac_sign = message.text
	await state.update_data(zodiac_sign=zodiac_sign)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET zodiac_sign = ? WHERE user_id = ?", (zodiac_sign, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_descr_view')
async def call_redaction_description(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)

	await state.set_state(Redaction_inline_view.anketa_description)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Описание пользователю!"
	)


@router.message(Redaction_inline_view.anketa_description)
async def call_redaction_gender(message: Message, bot: Bot, state: FSMContext):
	anketa_description = message.text
	await state.update_data(anketa_description=anketa_description)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET anketa_description = ? WHERE user_id = ?", (anketa_description, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_kurs_view')
async def call_redaction_kurs(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="1"), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
			 KeyboardButton(text='5')],
		],
		resize_keyboard=True
	)
	await state.set_state(Redaction_inline_view.kurs)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Курс пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_view.kurs)
async def call_redaction_kurs(message: Message, bot: Bot, state: FSMContext):
	kurs = message.text
	await state.update_data(kurs=kurs)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET kurs = ? WHERE user_id = ?", (kurs, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_facultet_view')
async def call_redaction_facultet(callback: CallbackQuery, bot: Bot, state: FSMContext):

	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='ЮФ'), KeyboardButton(text='ГФ'), KeyboardButton(text='ФБТДиЭБ')],
			[KeyboardButton(text='ФИПМ'), KeyboardButton(text='ФСТИГ'), KeyboardButton(text='ФУ')],
		],
		resize_keyboard=True,
	)
	await state.set_state(Redaction_inline_view.faculty)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Факультет пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_view.faculty)
async def call_redaction_faculty(message: Message, bot: Bot, state: FSMContext):
	faculty = message.text
	await state.update_data(faculty=faculty)

	if faculty == 'ЮФ':
		faculty = 'LF'
	if faculty == 'ГФ':
		faculty = 'GF'
	if faculty == 'ФБТДиЭБ':
		faculty = 'BTB'
	if faculty == 'ФИПМ':
		faculty = 'FIPM'
	if faculty == 'ФСТИГ':
		faculty = 'FSTIG'
	if faculty == 'ФУ':
		faculty = 'FU'

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET faculty = ? WHERE user_id = ?", (faculty, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())


@router.callback_query(F.data == 'red_naznachenie_view')
async def call_redaction_naznazh(callback: CallbackQuery, bot: Bot, state: FSMContext):
	await bot.delete_message(
		chat_id=callback.message.chat.id,
		message_id=callback.message.message_id
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Бакалавриат')],
			[KeyboardButton(text='Магистратура')],
		],
		resize_keyboard=True,
	)
	await state.set_state(Redaction_inline_view.grade)
	await bot.send_message(
		chat_id=callback.message.chat.id,
		text=f"Выбери Назначение пользователю!",
		reply_markup=keyboard
	)


@router.message(Redaction_inline_view.grade)
async def call_redaction_grade_view(message: Message, bot: Bot, state: FSMContext):
	grade = message.text
	await state.update_data(grade=grade)

	data = await state.get_data()
	user_id = data.get('user_id_from_call')

	cursor.execute("UPDATE users SET grade = ? WHERE user_id = ?", (grade, user_id))
	conn.commit()

	name = data.get('name')
	path = data.get('path')
	gender = data.get('gender')
	age = data.get('age')
	anketa_description = data.get('anketa_description')
	zodiac_sign = data.get('zodiac_sign')
	kurs = data.get('kurs')
	faculty = data.get('faculty')
	grade = data.get('grade')

	await bot.send_message(
		chat_id=message.chat.id,
		text='Отлично!',
		reply_markup=ReplyKeyboardRemove()
	)

	caption = (f'Что изменим в данной анкете?\n\n'
	           f"Имя: <b>{name}</b>\n"
	           f"Гендер: <b>{gender}</b>\n"
	           f"возраст: <b>{age}</b>\n"
	           f'Описание анкеты: <b>{anketa_description}</b>\n'
	           f'Знак зодиака: <b>{zodiac_sign}</b>\n'
	           f'Курс: <b>{kurs}</b>\n'
	           f'Факультет: <b>{faculty}</b>\n'
	           f'Назначение: <b>{grade}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		photo=FSInputFile(path),
		caption=caption,
		reply_markup=redaction_inline_view())
