""" import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler
from pymongo import MongoClient """

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import mysql.connector

# Настройки логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Подключение к базе данных MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bot_db']
users_collection = db['users']

# Обработчик команды /start
def start(update: Update, context):
    user_id = update.message.chat_id
    user_data = users_collection.find_one({'user_id': user_id})
    if user_data:
        update.message.reply_text('С возвращением! Что хотите сделать?')
    else:
        update.message.reply_text('Привет! Я бот знакомств. Давайте познакомимся. Как вас зовут?')
        users_collection.insert_one({'user_id': user_id, 'step': 'name'})

# Обработчик сообщений с именем пользователя
def name(update: Update, context):
    user_id = update.message.chat_id
    name = update.message.text
    users_collection.update_one({'user_id': user_id}, {'$set': {'name': name, 'step': 'gender'}})
    update.message.reply_text('Какой у вас пол? (Мужской/Женский)')

# Обработчик сообщений с полом пользователя
def gender(update: Update, context):
    user_id = update.message.chat_id
    gender = update.message.text.lower()
    if gender == 'мужской' or gender == 'женский':
        users_collection.update_one({'user_id': user_id}, {'$set': {'gender': gender, 'step': 'age'}})
        update.message.reply_text('Сколько вам лет?')
    else:
        update.message.reply_text('Некорректный ввод. Попробуйте еще раз. Какой у вас пол? (Мужской/Женский)')

# Обработчик сообщений с возрастом пользователя
def age(update: Update, context):
    user_id = update.message.chat_id
    age = update.message.text
    if age.isdigit():
        users_collection.update_one({'user_id': user_id}, {'$set': {'age': age, 'step': 'city'}})
        update.message.reply_text('В каком городе вы живете?')
    else:
        update.message.reply_text('Некорректный ввод. Попробуйте еще раз. Сколько вам лет?')

# Обработчик сообщений с городом пользователя
def city(update: Update, context):
    user_id = update.message.chat_id
    city = update.message.text
    users_collection.update_one({'user_id': user_id}, {'$set': {'city': city, 'step': 'photo'}})
    update.message.reply_text('Пришлите ваше фото')

# Обработчик сообщений с фото пользователя
def photo(update: Update, context):
    user_id = update.message.chat_id
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('photos/{}.jpg'.format(user_id))
    users_collection.update_one({'user_id': user_id}, {'$set': {'photo': 'photos/{}.jpg'.format(user_id), 'step': 'description'}})
    update.message.reply_text('Напишите немного о себе')

# Обработчик сообщений с описанием пользователя
def description(update: Update, context):
    user_id = update.message.chat_id
    description = update.message.text
    users_collection.update_one({'user_id': user_id}, {'$set': {'description': description, 'step': 'looking_for'}})
    update.message.reply_text('Кого вы ищете? (Мужчину/Женщину)')

# Обработчик сообщений с тем, кого ищет пользователь
def looking_for(update: Update, context):
    user_id = update.message.chat_id
    looking_for = update.message.text.lower()
    if looking_for == 'мужчину' or looking_for == 'женщину':
        users_collection.update_one({'user_id': user_id}, {'$set': {'looking_for': looking_for, 'step': 'find_match'}})
        update.message.reply_text('Ищем подходящие анкеты...')
        show_matches(update, context)
    else:
        update.message.reply_text('Некорректный ввод. Попробуйте еще раз. Кого вы ищете? (Мужчину/Женщину)')

# Обработчик нажатия на кнопку "Нравится" или "Не нравится"
def button(update: Update, context):
    query = update.callback_query
    user_id = query.message.chat_id
    match_id = int(query.data.split('_')[1])
    if query.data.startswith('like'):
        users_collection.update_one({'user_id': user_id}, {'$push': {'likes': match_id}})
        match_data = users_collection.find_one({'user_id': match_id})
        if user_id in match_data.get('likes', []):
            context.bot.send_message(chat_id=user_id, text='Поздравляем! Вы нашли совпадение. Ссылка на профиль: t.me/{}'.format(match_data['username']))
            context.bot.send_message(chat_id=match_id, text='Поздравляем! Вы нашли совпадение. Ссылка на профиль: t.me/{}'.format(users_collection.find_one({'user_id': user_id})['username']))
    users_collection.update_one({'user_id': user_id}, {'$push': {'seen': match_id}})
    show_matches(update, context)

# Обработчик текстовых сообщений
def text(update: Update, context):
    user_id = update.message.chat_id
    user_data = users_collection.find_one({'user_id': user_id})
    if user_data['step'] == 'find_match':
        show_matches(update, context)

# Функция для показа анкет пользователю
def show_matches(update: Update, context):
    user_id = update.message.chat_id
    user_data = users_collection.find_one({'user_id': user_id})
    matches = users_collection.find({'gender': user_data['looking_for'], 'looking_for': user_data['gender'], 'user_id': {'$ne': user_id}, 'user_id': {'$nin': user_data.get('seen', [])}})
    if matches.count() == 0:
        update.message.reply_text('К сожалению, мы не нашли подходящих анкет. Попробуйте позже.')
    else:
        keyboard = []
        for match in matches:
            keyboard.append([InlineKeyboardButton('Нравится', callback_data='like_{}'.format(match['user_id'])), InlineKeyboardButton('Не нравится', callback_data='dislike_{}'.format(match['user_id']))])
            update.message.reply_photo(photo=open(match['photo'], 'rb'), caption='Имя: {}\nГород: {}\nОписание: {}'.format(match['name'], match['city'], match['description']), reply_markup=InlineKeyboardMarkup(keyboard))

# Обработчик ошибок
def error(update: Update, context):
    logging.error('Update "%s" caused error "%s"', update, context.error)

# Создание и запуск бота
def main():
    updater = Updater('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text))
    dp.add_handler(MessageHandler(Filters.regex('^(Мужской|Женский)$'), gender))
    dp.add_handler(MessageHandler(Filters.regex('^\d+$'), age))
    dp.add_handler(MessageHandler(Filters.photo, photo))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex('^[^/].*$'), description))
    dp.add_handler(MessageHandler(Filters.regex('^(Мужчину|Женщину)$'), looking_for))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()