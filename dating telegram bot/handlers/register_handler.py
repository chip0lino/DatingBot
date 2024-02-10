from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile

from database.database import cursor, conn
from state.register_state import Register_anketa


router = Router()


@router.message(CommandStart())
async def start_function(message: Message, bot: Bot):
    user_id: int = message.from_user.id
    nickname = message.from_user.full_name
    user_link = f'<a href="tg://user?id={user_id}">{nickname}</a>'

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        db_user_id = user_data[0]
        keyboard = ReplyKeyboardMarkup(
	        keyboard=[
		        [KeyboardButton(text='Мой профиль')],
		        [KeyboardButton(text='Смотреть анкеты')]
	        ],
	        resize_keyboard=True
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=f'''<b>{user_link}</b>, Добро пожаловать!\n
Ваша сессия активна в базе данных, продолжим?''',
	        reply_markup=keyboard
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f'''<b>{user_link}</b>, Добро пожаловать в бота\n
Вашей анкеты ещё нет в базе данных.
Пожалуйста, зарегистрируйтесь.\n
Для заполнения анкеты напишите /anketa.
            ''',
            reply_to_message_id=message.message_id
        )


@router.message(F.text.lower() == '/cancel')
async def anketa(message: Message, bot: Bot, state: FSMContext):
	await state.clear()
	await bot.send_message(
		chat_id=message.chat.id,
		text='Вы отменили создание анкеты!\n'
		     'Для создания новой напишите /start',
		reply_markup=ReplyKeyboardRemove())


@router.message(Command('anketa'))
async def anketa(message: Message, bot: Bot, state: FSMContext):
	user_id: int = message.from_user.id
	nickname = message.from_user.full_name
	# ссылка на пользователя в телеге
	user_link = f'<a href="tg://user?id={user_id}">{nickname}</a>'

	await state.set_state(Register_anketa.name)
	await bot.send_message(
		chat_id=message.chat.id,
		text=f'''<b>{user_link}</b>, начнем с заполнения вашего имени.\n
Как тебя зовут?'''
	)


@router.message(Register_anketa.name)
async def name_state(message: Message, bot: Bot, state: FSMContext):
	name = message.text

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
		await state.update_data(name=name)
		await state.set_state(Register_anketa.age)
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Так держать!\n'
			     f'Теперь определимся в возрастом:'
		)



@router.message(Register_anketa.age)
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
			await state.update_data(age=age)
			await state.set_state(Register_anketa.gender)
			keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='Женский')],
					[KeyboardButton(text='Мужской')],
				],
				resize_keyboard=True,
			)

			await bot.send_message(
				chat_id=message.chat.id,
				text='Успешно!\nКакой ваш пол?',
				reply_markup=keyboard
			)


@router.message(Register_anketa.gender)
async def gender_state(message: Message, bot: Bot, state: FSMContext):
	gender = message.text

	if gender in ['Мужской', 'Женский']:
		await state.update_data(gender=gender)
		await state.set_state(Register_anketa.photo)
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'Так держать!\n'
			     f'Теперь cкинь свою фоточку!',
			reply_markup=ReplyKeyboardRemove()
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Такого гендера не существует!'
		)



@router.message(Register_anketa.photo)
async def photo_state(message: Message, bot: Bot, state: FSMContext):
	if message.photo:
		photo = message.photo[-1]
		file_id = photo.file_id
		file_info = await bot.get_file(file_id)
		file_path = file_info.file_path
		destination = f'/home/sapsan/Projects/DatingBot/dating telegram bot/photos/{file_id}.jpg' #C:\\Users\\Egor\\Documents\\projects\\dating telegram bot\\photos/{file_id}.jpg
		await bot.download_file(file_path, destination)
		await state.update_data(file_id=file_id)
		await state.update_data(destination=destination)

		await state.set_state(Register_anketa.anketa_description)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Фотография успешно загружена! 🌟\n'
			     'Теперь напиши описание для своей анкеты!'
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Пожалуйста, отправьте фотографию.'
		)


@router.message(Register_anketa.anketa_description)
async def description_state(message: Message, bot: Bot, state: FSMContext):
	description = message.text

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
		await state.update_data(description=description)
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
		await state.set_state(Register_anketa.zodiak_sign)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Отличное описание!\n'
			     'Какой твой знак зодиака?',
			reply_markup=keyboard
		)


@router.message(Register_anketa.zodiak_sign)
async def zodiak_state(message: Message, bot: Bot, state: FSMContext):
	znak_zodiaka = message.text

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
		await state.update_data(znak_zodiaka=znak_zodiaka)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Бакалавриат')],
				[KeyboardButton(text='Магистратура')],
			],
			resize_keyboard=True,
		)

		await state.set_state(Register_anketa.grade)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Мы почти у цели!\n'
			     'Вопрос: Бакалавриат или Магистратура?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Такого знака не существует!'
		)


@router.message(Register_anketa.grade)
async def grade_state(message: Message, bot: Bot, state: FSMContext):
	grade = message.text

	if grade in ['Бакалавриат', 'Магистратура']:
		await state.update_data(grade=grade)
		await state.set_state(Register_anketa.faculty)
		keyboard = ReplyKeyboardMarkup(
			keyboard = [
				[KeyboardButton(text='ЮФ'), KeyboardButton(text='ГФ'), KeyboardButton(text='ФБТДиЭБ')],
				[KeyboardButton(text='ФИПМ'), KeyboardButton(text='ФСТИГ'), KeyboardButton(text='ФУ')],
			],
			resize_keyboard=True,
		)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Отлично!\n'
			     'На каком вы факультете?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)


@router.message(Register_anketa.faculty)
async def faculty_state(message: Message, bot: Bot, state: FSMContext):
	faculty = message.text

	if faculty not in ["ЮФ", "ГФ", "ФБТДиЭБ", "ФИПМ", "ФСТИГ", "ФУ"]:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)
	else:
		data = await state.get_data()
		grade = data.get("grade")

		if grade in ['Бакалавриат']:
			keyboard1 = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text="1"), KeyboardButton(text='2'), KeyboardButton(text='3'), KeyboardButton(text='4'),
					 KeyboardButton(text='5')],
				],
				resize_keyboard=True
			)
			await state.update_data(faculty=faculty)
			await state.set_state(Register_anketa.kurs)
			await bot.send_message(
				chat_id=message.chat.id,
				text='На каком вы курсе??',
				reply_markup=keyboard1
			)
		elif grade in ['Магистратура']:
			keyboard2 = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text="1"), KeyboardButton(text='2')],
				],
				resize_keyboard=True
			)
			await state.update_data(faculty=faculty)
			await state.set_state(Register_anketa.kurs)
			await bot.send_message(
				chat_id=message.chat.id,
				text='На каком вы курсе??',
				reply_markup=keyboard2
			)


@router.message(Register_anketa.kurs)
async def kurs_state(message: Message, bot: Bot, state: FSMContext):
	kurs = message.text

	if kurs in [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]:
		await state.update_data(kurs=kurs)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Успешно!\n'
			     'Вот ваша анкета:',
			reply_markup=ReplyKeyboardRemove()
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Неверный курс!'
		)
		return

	data = await state.get_data()
	name = data.get("name")
	gender = data.get("gender")
	age = data.get("age")
	anketa_description = data.get("description")
	znak_zodiaka = data.get("znak_zodiaka")
	kurs = data.get("kurs")
	faculty = data.get("faculty")
	grade_user = data.get("grade")
	photion = data.get("destination")

	text = (f'🪄 Имя: <b>{name}</b>\n'
	        f'Ваш пол: <b>{gender}</b>\n'
	        f'Ваш возраст: <b>{age}</b>\n'
	        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
	        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
	        f'Курс: <b>{kurs}</b>\n'
	        f'Факультет: <b>{faculty}</b>\n'
	        f'Назначение: <b>{grade_user}</b>')

	await bot.send_photo(
		chat_id=message.chat.id,
		caption=text,
		photo=FSInputFile(photion)
	)
	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[KeyboardButton(text='Подтвердить')],
			[KeyboardButton(text='Редактировать')]
		],
		resize_keyboard=True
	)
	await state.set_state(Register_anketa.final)
	await bot.send_message(
		chat_id=message.chat.id,
		text='Сохранить анкету?',
		reply_markup=keyboard
	)


@router.message(Register_anketa.final)
async def finally_state(message: Message, bot: Bot, state: FSMContext):
	user_id: int = message.from_user.id
	username = message.from_user.username
	nickname = message.from_user.full_name
	final = message.text

	if final not in ["Подтвердить", "Редактировать"]:
		await bot.send_message(
			chat_id=message.chat.id,
			text='Выберите существующий вариант'
		)
	else:
		if final in ["Подтвердить"]:
			data = await state.get_data()
			name = data.get("name")
			gender = data.get("gender")
			age = data.get("age")
			anketa_description = data.get("description")
			znak_zodiaka = data.get("znak_zodiaka")
			kurs = data.get("kurs")
			faculty = data.get("faculty")
			grade_user = data.get("grade")
			photion = data.get("file_id")

			if gender == "Мужской":
				gender = 'male'
			if gender == "Женский":
				gender = 'female'
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
			cursor.execute('''
			        INSERT INTO users (
			            user_id,
			            username,
			            nickname,
			            name,
			            gender,
			            age,
			            photo,
			            anketa_description,
			            zodiac_sign,
			            kurs,
			            faculty,
			            grade
			        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			    ''', (user_id, username, nickname, name, gender, age, photion, anketa_description, znak_zodiaka, kurs, faculty, grade_user))
			cursor.execute('''
				  INSERT INTO like (
				  	user_id,
					hidden
				  ) VALUES (?, ?)
				  ''', (user_id, user_id))
			await state.clear()
			conn.commit()

			keyboard1 = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='Мой профиль')],
					[KeyboardButton(text='Смотреть анкеты')]
				],
				resize_keyboard=True
			)

			await bot.send_message(
				chat_id=message.chat.id,
				text='Успешно сохранено\n'
				     'Выберете желаемый вариант:',
				reply_markup=keyboard1
			)
		elif final in ["Редактировать"]:
			await state.set_state(Register_anketa.redaction)
			keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='Имя'), KeyboardButton(text='Возраст'), KeyboardButton(text='Пол')],
					[KeyboardButton(text='Фото'), KeyboardButton(text='Описание'), KeyboardButton(text='Знак Зодиака')],
					[KeyboardButton(text="Магистр/Бакалавр"), KeyboardButton(text='Факультет'),
					 KeyboardButton(text='Курс')]
				],
				resize_keyboard=True
			)
			await bot.send_message(
				chat_id=message.chat.id,
				text="С какого пункта начнём редактирование?",
				reply_markup=keyboard
			)


@router.message(Register_anketa.redaction)
async def redaction(message: Message, bot: Bot, state: FSMContext):
	red = message.text

	if red == "Имя":
		await state.set_state(Register_anketa.name_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Как тебя зовут?"
		)
	elif red == "Возраст":
		await state.set_state(Register_anketa.age_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Сколько тебе лет?"
		)
	elif red == "Пол":
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Женский')],
				[KeyboardButton(text='Мужской')],
			],
			resize_keyboard=True,
		)
		await state.set_state(Register_anketa.gender_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Какой у тебя пол?",
			reply_markup=keyboard
		)
	elif red == "Фото":
		await state.set_state(Register_anketa.photo_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Скинь ка новую фоточку!"
		)
	elif red == "Описание":
		await state.set_state(Register_anketa.anketa_description_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Напиши новое описание!"
		)
	elif red == "Знак Зодиака":
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
		await state.set_state(Register_anketa.zodiak_sign_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Каков твой знак зодиака?",
			reply_markup=keyboard
		)
	elif red == "Магистр/Бакалавр":
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Бакалавриат')],
				[KeyboardButton(text='Магистратура')],
			],
			resize_keyboard=True,
		)
		await state.set_state(Register_anketa.grade_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Магистратура или Бакалавриат??",
			reply_markup=keyboard
		)
	elif red == 'Факультет':
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='ЮФ'), KeyboardButton(text='ГФ'), KeyboardButton(text='ФБТДиЭБ')],
				[KeyboardButton(text='ФИПМ'), KeyboardButton(text='ФСТИГ'), KeyboardButton(text='ФУ')],
			],
			resize_keyboard=True,
		)
		await state.set_state(Register_anketa.faculty_red)
		await bot.send_message(
			chat_id=message.chat.id,
			text="Какой твой факультет?",
			reply_markup=keyboard
		)
	elif red == "Курс":
		data = await state.get_data()
		grade = data.get("grade")

		if grade in ['Бакалавриат']:
			await state.set_state(Register_anketa.kurs_red)
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
				text='На каком вы курсе??',
				reply_markup=keyboard1
			)
		elif grade in ['Магистратура']:
			keyboard2 = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text="1"), KeyboardButton(text='2')],
				],
				resize_keyboard=True
			)
			await state.set_state(Register_anketa.kurs_red)
			await bot.send_message(
				chat_id=message.chat.id,
				text="Каков твой курс?",
				reply_markup=keyboard2
			)


@router.message(Register_anketa.name_red)
async def name_state(message: Message, bot: Bot, state: FSMContext):
	name = message.text

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
		await state.update_data(name=name)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)


@router.message(Register_anketa.age_red)
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
			await state.update_data(age=age)
			data = await state.get_data()
			name = data.get("name")
			gender = data.get("gender")
			age = data.get("age")
			anketa_description = data.get("description")
			znak_zodiaka = data.get("znak_zodiaka")
			kurs = data.get("kurs")
			faculty = data.get("faculty")
			grade_user = data.get("grade")
			photion = data.get("destination")

			text = (f'🪄 Имя: <b>{name}</b>\n'
			        f'Ваш пол: <b>{gender}</b>\n'
			        f'Ваш возраст: <b>{age}</b>\n'
			        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
			        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
			        f'Курс: <b>{kurs}</b>\n'
			        f'Факультет: <b>{faculty}</b>\n'
			        f'Назначение: <b>{grade_user}</b>')

			await bot.send_photo(
				chat_id=message.chat.id,
				caption=text,
				photo=FSInputFile(photion)
			)
			keyboard = ReplyKeyboardMarkup(
				keyboard=[
					[KeyboardButton(text='Подтвердить')],
					[KeyboardButton(text='Редактировать')]
				],
				resize_keyboard=True
			)
			await state.set_state(Register_anketa.final)
			await bot.send_message(
				chat_id=message.chat.id,
				text='Сохранить анкету?',
				reply_markup=keyboard
			)


@router.message(Register_anketa.gender_red)
async def gender_state(message: Message, bot: Bot, state: FSMContext):
	gender = message.text

	if gender in ['Мужской', 'Женский']:
		await state.update_data(gender=gender)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text=f'❌ Такого гендера не существует!'
		)


@router.message(Register_anketa.photo_red)
async def photo_state(message: Message, bot: Bot, state: FSMContext):
	if message.photo:
		photo = message.photo[-1]
		file_id = photo.file_id
		file_info = await bot.get_file(file_id)
		file_path = file_info.file_path
		destination = f'C:\\Users\\Egor\\Documents\\projects\\dating telegram bot\\photos/{file_id}.jpg'
		await bot.download_file(file_path, destination)
		await state.update_data(file_id=file_id)
		await state.update_data(destination=destination)

		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Пожалуйста, отправьте фотографию.'
		)


@router.message(Register_anketa.anketa_description_red)
async def description_state(message: Message, bot: Bot, state: FSMContext):
	description = message.text

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
		await state.update_data(description=description)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)


@router.message(Register_anketa.zodiak_sign_red)
async def zodiak_state(message: Message, bot: Bot, state: FSMContext):
	znak_zodiaka = message.text

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
		await state.update_data(znak_zodiaka=znak_zodiaka)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Такого знака не существует!'
		)


@router.message(Register_anketa.grade_red)
async def grade_state(message: Message, bot: Bot, state: FSMContext):
	grade = message.text

	if grade in ['Бакалавриат', 'Магистратура']:
		await state.update_data(grade=grade)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)


@router.message(Register_anketa.faculty_red)
async def faculty_state(message: Message, bot: Bot, state: FSMContext):
	faculty = message.text

	if faculty not in ["ЮФ", "ГФ", "ФБТДиЭБ", "ФИПМ", "ФСТИГ", "ФУ"]:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Укажите корректные данные'
		)
	else:
		await state.update_data(faculty=faculty)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)


@router.message(Register_anketa.kurs_red)
async def kurs_state(message: Message, bot: Bot, state: FSMContext):
	kurs = message.text

	if kurs in [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]:
		await state.update_data(kurs=kurs)
		data = await state.get_data()
		name = data.get("name")
		gender = data.get("gender")
		age = data.get("age")
		anketa_description = data.get("description")
		znak_zodiaka = data.get("znak_zodiaka")
		kurs = data.get("kurs")
		faculty = data.get("faculty")
		grade_user = data.get("grade")
		photion = data.get("destination")

		text = (f'🪄 Имя: <b>{name}</b>\n'
		        f'Ваш пол: <b>{gender}</b>\n'
		        f'Ваш возраст: <b>{age}</b>\n'
		        f'Описание вашей анкеты: <b>{anketa_description}</b>\n'
		        f'Знак зодиака: <b>{znak_zodiaka}</b>\n'
		        f'Курс: <b>{kurs}</b>\n'
		        f'Факультет: <b>{faculty}</b>\n'
		        f'Назначение: <b>{grade_user}</b>')

		await bot.send_photo(
			chat_id=message.chat.id,
			caption=text,
			photo=FSInputFile(photion)
		)
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[KeyboardButton(text='Подтвердить')],
				[KeyboardButton(text='Редактировать')]
			],
			resize_keyboard=True
		)
		await state.set_state(Register_anketa.final)
		await bot.send_message(
			chat_id=message.chat.id,
			text='Сохранить анкету?',
			reply_markup=keyboard
		)
	else:
		await bot.send_message(
			chat_id=message.chat.id,
			text='❌ Неверный курс!'
		)
