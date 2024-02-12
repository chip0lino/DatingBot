from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import cursor


def admin_panel_for_admins():
    buttons = [
	    [
		    types.InlineKeyboardButton(text='🛠 Просмотр анкет', callback_data='anket_admin_view')
	    ],
	    [
		    types.InlineKeyboardButton(text='🩸 Точечный поиск', callback_data='view_touch_to')
	    ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_keyboard(page=1, page_size=4):
    offset = (page - 1) * page_size
    cursor.execute('''SELECT user_id, nickname, faculty FROM users LIMIT ? OFFSET ?''', (page_size, offset))
    data = cursor.fetchall()

    inline = []
    user_dict = {}
    row = []
    for user_id, nickname, faculty in data:
        button = InlineKeyboardButton(text=str(nickname), callback_data=f"user_call_{int(user_id)}")
        row.append(button)
        if len(row) == 2:
            inline.append(row)
            row = []
        if nickname is None:
            nickname = 'Отсутствует'
        if faculty is None:
            faculty = 'Отсутствует'

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

        user_dict[str(user_id)] = {'nickname': nickname, 'faculty': faculty}

    if page > 1:
        prev_button = InlineKeyboardButton(text="<< Предыдущие", callback_data=f"prev_{page-1}")
        inline.append([prev_button])
    if len(data) == page_size:
        next_button = InlineKeyboardButton(text="Следующие >>>", callback_data=f"next_{page+1}")
        inline.append([next_button])

    ikb = InlineKeyboardMarkup(inline_keyboard=inline)
    return ikb, user_dict


def user_checkout():
    buttons = [
	    [
		    types.InlineKeyboardButton(text='🌀 Редактировать', callback_data='redaction_with_inline')
	    ],
	    [
		    types.InlineKeyboardButton(text='🔸 Блокировать', callback_data='blocked_inline')
	    ],
	    [
		    types.InlineKeyboardButton(text='↩️ Назад', callback_data='anket_admin_view')
	    ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def redaction_inline():
    buttons = [
        [
	        types.InlineKeyboardButton(text='Имя', callback_data='red_name'),
	        types.InlineKeyboardButton(text='Пол', callback_data='red_gender'),
	        types.InlineKeyboardButton(text='Возраст', callback_data='red_age'),
	        types.InlineKeyboardButton(text='Фото', callback_data='red_photo'),
	        types.InlineKeyboardButton(text='ЗЗ', callback_data='red_sign_zodiac'),
        ],
	    [
		    types.InlineKeyboardButton(text='Описание', callback_data='red_descr'),
		    types.InlineKeyboardButton(text='Курс', callback_data='red_kurs'),
		    types.InlineKeyboardButton(text='Факультет', callback_data='red_facultet'),
		    types.InlineKeyboardButton(text='Назначение', callback_data='red_naznachenie'),
	    ],
	    [
		    types.InlineKeyboardButton(text='🔸 Блокировать', callback_data='blocked_inline')
	    ],
	    [
		    types.InlineKeyboardButton(text='↩️ В меню поиска', callback_data='anket_admin_view')
	    ],
	]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def user_checkout_push():
    buttons = [
	    [
		    types.InlineKeyboardButton(text='🌀 Редактировать', callback_data='redaction_with_inline_view')
	    ],
	    [
		    types.InlineKeyboardButton(text='🔸 Блокировать', callback_data='blocked_inline_view')
	    ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def redaction_inline_view():
    buttons = [
        [
	        types.InlineKeyboardButton(text='Имя', callback_data='red_name_view'),
	        types.InlineKeyboardButton(text='Пол', callback_data='red_gender_view'),
	        types.InlineKeyboardButton(text='Возраст', callback_data='red_age_view'),
	        types.InlineKeyboardButton(text='Фото', callback_data='red_photo_view'),
	        types.InlineKeyboardButton(text='ЗЗ', callback_data='red_sign_zodiac_view'),
        ],
	    [
		    types.InlineKeyboardButton(text='Описание', callback_data='red_descr_view'),
		    types.InlineKeyboardButton(text='Курс', callback_data='red_kurs_view'),
		    types.InlineKeyboardButton(text='Факультет', callback_data='red_facultet_view'),
		    types.InlineKeyboardButton(text='Назначение', callback_data='red_naznachenie_view'),
	    ],
	    [
		    types.InlineKeyboardButton(text='🔸 Блокировать', callback_data='blocked_inline_view')
	    ],
	]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
