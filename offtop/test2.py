import telebot
from telebot import types # для указание типов

bot = telebot.TeleBot('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Создать анкету")
    btn2 = types.KeyboardButton("❓ Информация")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я — чатбот знакомств для студентов СПбГЭУ «ГэуДейт»".format(message.from_user), reply_markup=markup)
    
@bot.message_handler(content_types=['text'])
def func(message):
    if(message.text == "❓ Информация"):
        bot.send_message(message.chat.id, text="Я — чатбот знакомств для студентов СПбГЭУ «ГэуДейт»\n\nПолная информация о боте")
    elif(message.text == "👋 Создать анкету"):
        bot.send_message(message.chat.id, text="Отлично! Приступим. Как тебя зовут?")
        
    

bot.polling(none_stop=True)