from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, ReplyKeyboardRemove

from database.database import cursor, conn
from state.register_state import Register_profile

router = Router()

# Меня оценили Редактировать профиль Назад в меню'
@router.message(F.text == 'Мой профиль')
async def my_profile(message: Message, bot: Bot):
	user_id: int = message.from_user.id
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="Меня оценили")],
			[KeyboardButton(text="Редактировать профиль"),
			KeyboardButton(text="Назад в меню")]
		],
		resize_keyboard=True

	)


	cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
	user_data = cursor.fetchone()

	if not user_data:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Зарегистрируйтесь! /anketa',
		)
	else:
		db_user_id = user_data[0] 
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Добро пожаловать в ваш профиль!',
			reply_markup=keyboard
		)
	cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
	row = cursor.fetchone()

	if row:
		user_id, name, gender, age, photo, anketa_description, zodiac_sign, kurs, faculty, grade_user = row

		destination = f'C:\\Users\\Egor\\Documents\\projects\\dating telegram bot\\photos/{photo}.jpg'

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

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{zodiac_sign}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')


		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(destination)
		)


@router.message(F.text == 'Редактировать профиль')
async def my_profile_redaction(message: Message, bot: Bot):
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[
				KeyboardButton(text='Имя'),
				KeyboardButton(text='Возраст'),
				KeyboardButton(text='Пол')
			],
			[
				KeyboardButton(text='Фото'),
				KeyboardButton(text='Описание'),
				KeyboardButton(text='Знак Зодиака')
			],
			[
				KeyboardButton(text="Магистр/Бакалавр"),
				KeyboardButton(text='Факультет'),
				KeyboardButton(text='Курс')
			],
			[
				KeyboardButton(text='Мой профиль')
			]
		],
		resize_keyboard=True
	)

	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Что мы хотим редактировать?',
		reply_markup=keyboard
	)


@router.message(F.text == 'Имя')
async def my_profile_redaction_name(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.name)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Как тебя зовут?',
		reply_markup=ReplyKeyboardRemove()
	)


@router.message(Register_profile.name)
async def name_state(message: Message, bot: Bot, state: FSMContext):
	name = message.text
	user_id: int = message.from_user.id

	if len(name) <= 1 or len(name) > 16:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Вы должны ввести корректное имя'
		)

	elif len(name.split()) > 1:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Имя не должно содержать пробелов'
		)

	elif not name.isalpha():
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Имя не должно содержать цифры'
		)

	else:
		cursor.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)


@router.message(F.text == 'Возраст')
async def my_profile_redaction_name(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.age)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Сколько тебе лет?',
		reply_markup=ReplyKeyboardRemove()
	)

@router.message(Register_profile.age)
async def age_state(message: Message, bot: Bot, state: FSMContext):
	age = message.text
	user_id: int = message.from_user.id

	if not age.isdigit():
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Введите корректное число'
		)
	else:
		age_value = int(age)
		if age_value > 100 or age_value < 5:
			await bot.send_message(
				chat_id=message.chat.id,
				text='❌ Введите корректное число'
			)
		else:
			cursor.execute("UPDATE users SET age = ? WHERE user_id = ?", (age, user_id))
			conn.commit()
			keyboard1 = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='Мой профиль')],
					[KeyboardButton(text='Искать людей')]
				],
				resize_keyboard=True,
			)
			await state.clear()
			await bot.send_message(
				chat_id=message.chat.id,
				text=f'Отлично! Что выберем?',
				reply_markup=keyboard1
			)


@router.message(F.text == 'Пол')
async def my_profile_redaction_gender(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.gender)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Женский')],
			[KeyboardButton(text='Мужской')],
		],
		resize_keyboard=True,
	)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Какой твой гендер?',
		reply_markup=keyboard
	)


@router.message(Register_profile.gender)
async def gender_state(message: Message, bot: Bot, state: FSMContext):
	gender = message.text
	user_id: int = message.from_user.id

	if gender not in ['Мужской', 'Женский']:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Такого пола нет! выберете коректный'
		)
	else:
		cursor.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)


@router.message(F.text == 'Фото')
async def my_profile_redaction_photo(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.photo)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Скинь свою фоточку!',
		reply_markup=ReplyKeyboardRemove()
	)


@router.message(Register_profile.photo)
async def photo_state(message: Message, bot: Bot, state: FSMContext):
	user_id: int = message.from_user.id
	if message.photo:
		photo = message.photo[-1]
		file_id = photo.file_id
		file_info = await bot.get_file(file_id)
		file_path = file_info.file_path
		destination = f'C:\\Users\\Egor\\Documents\\projects\\dating telegram bot\\photos/{file_id}.jpg'
		await bot.download_file(file_path, destination)

		cursor.execute("UPDATE users SET photo = ? WHERE user_id = ?", (file_id, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)

	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Это разве фото?!',
			reply_markup=ReplyKeyboardRemove()
		)


@router.message(F.text == 'Описание')
async def my_profile_redaction_descriotion(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.anketa_description)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Напиши новое описание!',
		reply_markup=ReplyKeyboardRemove()
	)


@router.message(Register_profile.anketa_description)
async def description_state(message: Message, bot: Bot, state: FSMContext):
	description = message.text
	user_id: int = message.from_user.id

	if len(description) > 200:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Слишком длинное описание!'
		)
	elif len(description) < 10:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Слишком короткое описание!'
		)
	else:
		cursor.execute("UPDATE users SET anketa_description = ? WHERE user_id = ?", (description, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)


@router.message(F.text == 'Знак Зодиака')
async def my_profile_redaction_sign_zodiak(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.zodiak_sign)
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
		chat_id=message.chat.id,
		text=f'Каков твой знак зодиака?',
		reply_markup=keyboard
	)


@router.message(Register_profile.zodiak_sign)
async def zodiak_state(message: Message, bot: Bot, state: FSMContext):
	znak_zodiaka = message.text
	user_id: int = message.from_user.id

	if znak_zodiaka in ["Овен",
	                "Телец",
	                "Близнецы",
	                "Рак",
	                "Лев",
	                "Дева",
	                "Весы",
	                "Скорпион",
	                "Стрелец",
	                "Козерог",
	                "Водолей",
	                "Рыбы"]:
		cursor.execute("UPDATE users SET zodiac_sign = ? WHERE user_id = ?", (znak_zodiaka, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Такого знака не существует!'
		)


@router.message(F.text == "Магистр/Бакалавр")
async def my_profile_redaction_grade(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.grade)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Бакалавр')],
			[KeyboardButton(text='Магистр')],
		],
		resize_keyboard=True,
	)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Выбирай!',
		reply_markup=keyboard
	)


@router.message(Register_profile.grade)
async def grade_state(message: Message, bot: Bot, state: FSMContext):
	grade = message.text
	user_id: int = message.from_user.id

	if grade in ['Бакалавр', 'Магистр']:
		cursor.execute("UPDATE users SET grade = ? WHERE user_id = ?", (grade, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)

	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)


@router.message(F.text == 'Факультет')
async def my_profile_redaction_facultet(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.faculty)
	keyboard = ReplyKeyboardMarkup(
					keyboard=[
						[KeyboardButton(text='ЮФ'), KeyboardButton(text='ГФ'), KeyboardButton(text='ФБТДиЭБ')],
						[KeyboardButton(text='ФИПМ'), KeyboardButton(text='ФСТИГ'), KeyboardButton(text='ФУ')],
					],
					resize_keyboard=True,
				)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Выбирай!',
		reply_markup=keyboard
	)

@router.message(Register_profile.faculty)
async def faculty_state(message: Message, bot: Bot, state: FSMContext):
	faculty = message.text
	user_id: int = message.from_user.id

	if faculty not in ["ЮФ", "ГФ", "ФБТДиЭБ", "ФИПМ", "ФСТИГ", "ФУ"]:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)
	else:
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
		cursor.execute("UPDATE users SET faculty = ? WHERE user_id = ?", (faculty, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)


@router.message(F.text == 'Курс')
async def my_profile_redaction_kurs(message: Message, bot: Bot, state: FSMContext):
	await state.set_state(Register_profile.kurs)
	keyboard1 = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text="1"), KeyboardButton(text='2'), KeyboardButton(text='3'),
			 KeyboardButton(text='4'),
			 KeyboardButton(text='5')],
		],
		resize_keyboard=True
	)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'Выбирай!',
		reply_markup=keyboard1
	)


@router.message(Register_profile.kurs)
async def kurs_state(message: Message, bot: Bot, state: FSMContext):
	kurs = message.text
	user_id: int = message.from_user.id

	if kurs in [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]:
		cursor.execute("UPDATE users SET kurs = ? WHERE user_id = ?", (kurs, user_id))
		conn.commit()
		keyboard1 = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Мой профиль')],
				[KeyboardButton(text='Искать людей')]
			],
			resize_keyboard=True,
		)
		await state.clear()
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Отлично! Что выберем?',
			reply_markup=keyboard1
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Неверный курс!'
		)