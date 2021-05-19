import telegram
from telegram.ext import Updater, CommandHandler
import os
from dotenv import load_dotenv

load_dotenv()

allowed_users = ["lalalawson", "linawoo"]

def start(update, context):
    username = update.effective_user.username
    update.message.reply_text("Hello " + username)


def main():
    TOKEN = os.getenv("API_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    
    dispatcher = updater.dispatcher

    # commands
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
