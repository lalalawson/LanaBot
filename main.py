from telegram import KeyboardButton
from telegram.ext import Updater, CommandHandler
import os
from dotenv import load_dotenv
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup

load_dotenv()

allowed_users = ["lalalawson", "linawoo"]

def start(update, context):
    username = update.effective_user.username
    button_row1 = [KeyboardButton("Show me handsome guys!"), KeyboardButton("Show me something cute!")]
    button_row2 = [KeyboardButton("Tell me a joke!"), KeyboardButton("I just wna rant...")]
    buttons = [button_row1, button_row2]
    reply_keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    update.message.reply_text("Hello " + username + "!\n" + \
        "This bot was created to commerate our first year together 🥳\n What do you require today? 😚", reply_markup=reply_keyboard)


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
