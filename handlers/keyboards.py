from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# меню
main_kb = [
    [KeyboardButton(text='Смотреть анкеты')],
     [KeyboardButton(text='Мой профиль')]
]
main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

# при просмотре анкет
view_kb = [
    [KeyboardButton(text='Нравится'),
     KeyboardButton(text='Пропустить')],
    [KeyboardButton(text='Назад в меню'),
     KeyboardButton(text='Пожаловаться')], 
]
view = ReplyKeyboardMarkup(keyboard=view_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

# при просмотре анкет в конце
last_kb = [
    [KeyboardButton(text='Назад в меню')],
]
last = ReplyKeyboardMarkup(keyboard=last_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

who_like_kb = [
    [KeyboardButton(text = "Оценить ответно")],
    [KeyboardButton(text = "Следующая анкета")]
]
who_like = ReplyKeyboardMarkup(keyboard=who_like_kb,
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт ниже')

