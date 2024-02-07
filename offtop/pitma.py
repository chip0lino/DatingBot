import telebot

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CommandHandler,CallbackContext, MessageHandler, ContextTypes, ApplicationBuilder, filters, CallbackQueryHandler

from notion_client import Client
from pprint import pprint

from datetime import datetime, date, time

time_now = datetime.today().strftime("%d/%m/%y %H:%M")

notion_page_id = 'b35bcb219c1c4a4c926d10bed127eedc'
notion_token = 'secret_WqnwLe5xmzfYJ8YhMsd2EEUxocvIuXKNXWcX8BvyQVb'

client = Client(auth=notion_token)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "Hi! Ask me a relevant question")

async def reply(update: Update, context: CallbackContext) -> None:
    query = update.message.text.lower()
    user_name = update.effective_user.first_name
    
def write_text(client, page_id, text):
    client.blocks.children.append(
        block_id=page_id,
        children=[
            {
                "type": "divider",
                # // ...other keys excluded
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f'Заметка от {time_now}',

                        }
                    }]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": text,

                        }
                    }]
                }
            },
        ]
    )

async def reply(update: Update, context: CallbackContext) -> None:
    query = update.message.text.lower()
    user_name = update.effective_user.first_name

    write_text(client, notion_page_id, query)

    await update.message.reply_text(f"Thank you, {user_name}! I've already posted new note", message)

def main():
    api = "6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M"

    application = ApplicationBuilder().token(api).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    start_handler = CommandHandler('start', start_command)
    application.add_handler(start_handler)
    application.run_polling()

main()