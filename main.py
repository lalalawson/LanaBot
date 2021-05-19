from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import os
import DbAuth
from dotenv import load_dotenv

load_dotenv()

# states
CONTENT_REPLY, PHOTO_REPLY, ANSWER = range(3)

allowed_users = ["lalalawson", "linawoo"]

message_options = ["Tell me about us.. 😌", "Show me photos! 😆", "Tell me a joke! 😒", "I just wna rant... 😔"]

def start(update, context):
    global reply_keyboard 
    username = update.effective_user.username
    button_row1 = [KeyboardButton(message_options[0]), KeyboardButton(message_options[1])]
    button_row2 = [KeyboardButton(message_options[2]), KeyboardButton(message_options[3])]
    buttons = [button_row1, button_row2]

    # perform check on allowed users
    if username in allowed_users:
        reply_keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
        update.message.reply_text("Hello " + username + "!\n" + \
            "This bot was created to commerate our first year together 🥳\n" + \
            "What do you require today? 😚", reply_markup=reply_keyboard)
    else:
        update.message.reply_text("Sorry " + username + "! This is a private bot so it's not available for your viewing! 😅")

def test_upload(update, context):
    msg = update.message
    if msg.photo:
        file_id = msg.photo[-1].file_id
        msg.reply_photo(file_id)
        print(file_id)
    elif msg.video:
        file_id = msg.video.file_id
        msg.reply_video(file_id)
    elif msg.voice:
        file_id = msg.voice.file_id
        msg.reply_voice(file_id)
    elif msg.video_note:
        file_id = msg.video_note.file_id
        msg.reply_video_note(file_id)
    else:
        update.message.reply_text("Please upload a photo / video / voice or video note! You may select /cancel to exit.")

def upload(update, context):
    update.message.reply_text("Ooo!! Uploading a new memory? Send me the description of our day!")

    return CONTENT_REPLY

# def memory_message(update, context):

def memories(update, context):
    db = DbAuth.retrieveDb()
    doc_ref = db.collection(u'memories').document(u'1')
    doc = doc_ref.get().to_dict()
    
    format_date = doc['date'].strftime('%d %b %y')
    reply = "Remember " + format_date + "?\n" + doc['content'] + "\n-" + doc['author'] 
    update.message.reply_text(reply)

def cute(update, context):
    update.message.reply_text("wah cute")

def joke(update, context):
    update.message.reply_text("joke hahaha joke")

def rant(update, context):
    update.message.reply_text("time for a rant")

def illegal_user(update, context):
    username = update.effective_user.username
    update.message.reply_text("Sorry " + username + "! This is a private bot so it's not available for your viewing! 😅")

def illegal_option(update, context):
    update.message.reply_text("I'm sorry dear! There's no such option.. 😅 Select a proper one from the reply keyboard!", reply_markup=reply_keyboard)

def main():
    TOKEN = os.getenv("API_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    
    dispatcher = updater.dispatcher

    # commands handler
    dispatcher.add_handler(CommandHandler("start", start))

    # testing only
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.voice | Filters.video | Filters.video_note, test_upload))

    # message handler for invalid options
    dispatcher.add_handler(MessageHandler(~Filters.chat(username=allowed_users), illegal_user))
    dispatcher.add_handler(MessageHandler(~(Filters.regex(message_options[0]) ^ 
                                            Filters.regex(message_options[1]) ^ 
                                            Filters.regex(message_options[2]) ^ 
                                            Filters.regex(message_options[3])), illegal_option))
    
    # message handler for valid options
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[0]), memories))
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[1]), cute))
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[2]), joke))
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[3]), rant))

    # convo handlers
    # convo1 = ConversationHandler(
    #     entry_points=[CommandHandler('upload'), upload],
    #     states={
    #         CONTENT_REPLY(MessageHandler(Filters.text))
    #     },
    #     fallbacks=[],
    # )

    print("Bot polling...")
    updater.start_polling()
    updater.idle()
    print("Exiting bot...")

if __name__ == '__main__':
    main()
