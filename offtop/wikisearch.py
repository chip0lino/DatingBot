import telebot
import wikipedia
bot = telebot.TeleBot('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M')
@bot.message_handler(content_types=['text'])

def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Введите поисковой запрос")
    else:
        get_text_messages(message)

def get_text_messages(message):
    try:
        wikipedia.set_lang('ru')
        bot.send_message(message.from_user.id, wikipedia.summary(str(message.text)))
    except:
        bot.send_message(message.from_user.id, "Запрос не найден")

        
bot.polling(none_stop=True, interval=0)