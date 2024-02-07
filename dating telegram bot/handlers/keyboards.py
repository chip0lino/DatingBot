from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# меню
main_kb = [
    [KeyboardButton(text='Смотреть анкеты'),
     KeyboardButton(text='Профиль')],
]
main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

# при просмотре анкет
view_kb = [
    [KeyboardButton(text='Нравится'),
     KeyboardButton(text='Пропустить')],
    [KeyboardButton(text='Назад в меню')],
]
view = ReplyKeyboardMarkup(keyboard=view_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

# при просмотре анкет
last_kb = [
    [KeyboardButton(text='Назад в меню')],
]
last = ReplyKeyboardMarkup(keyboard=last_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')