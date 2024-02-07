import telebot
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

bot = telebot.TeleBot('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    topbut = types.KeyboardButton('Go to website')
    markup.row(topbut)
    leftbut = types.KeyboardButton('Edit message')
    rightbut = types.KeyboardButton('Delete photo')
    markup.row(leftbut, rightbut)
    bot.send_message(message.chat.id, 'Hi', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def on_click(message):
    if message.text == 'Go to website':
        bot.send_message(message.chat.id, 'Webdite is now online')


@bot.message_handler(content_types=['text','photo', 'audio'])
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    gotowebsite = types.InlineKeyboardButton('Go to website', url='https://t.me/mcdvll')
    markup.row(gotowebsite)
    delete = types.InlineKeyboardButton('Delete', callback_data='delete')
    edit = (types.InlineKeyboardButton('Edit text', callback_data='edit'))
    markup.row(delete, edit)
    bot.reply_to(message, 'Beautiful picture!', reply_markup=markup)


bot = telebot.TeleBot('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M')

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id)

bot.polling(none_stop=True)