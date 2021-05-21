from datetime import datetime
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.message import Message
from DbHelper import DbHelper
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import os
from dotenv import load_dotenv

load_dotenv()

# states
CONTENT_REPLY, FILE_REPLY, CHECK = range(3)

allowed_users = ["lalalawson", "linawoo"]

message_options = ["Tell me about us.. 😌", "Show me photos! 😆", "Tell me a joke! 😒", "I just wna rant... 😔"]

button_row1 = [KeyboardButton(message_options[0]), KeyboardButton(message_options[1])]
button_row2 = [KeyboardButton(message_options[2]), KeyboardButton(message_options[3])]
buttons = [button_row1, button_row2]
reply_keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

def start(update, context):
    username = update.effective_user.username

    # perform check on allowed users
    if username in allowed_users:
        update.message.reply_text("Hello " + username + "!\n" + \
            "This bot was created to commerate our first year together 🥳\n" + \
            "What do you require today? 😚", reply_markup=reply_keyboard)
    else:
        update.message.reply_text("Sorry " + username + "! This is a private bot so it's not available for your viewing! 😅")

# def test_upload(update, context):
#     msg = update.message
#     if msg.photo:
#         file_id = msg.photo[-1].file_id
#         msg.reply_photo(file_id)
#         print(file_id)
#     elif msg.video:
#         file_id = msg.video.file_id
#         msg.reply_video(file_id)
#     elif msg.voice:
#         file_id = msg.voice.file_id
#         msg.reply_voice(file_id)
#     elif msg.video_note:
#         file_id = msg.video_note.file_id
#         msg.reply_video_note(file_id)
#     else:
#         update.message.reply_text("Please upload a photo / video / voice or video note! You may select /cancel to exit.")

def upload(update, context):
    update.message.reply_text("Ooo!! Uploading a new memory? Send me the description of our memory!")
    return CONTENT_REPLY

def content_upload(update, context):
    user_info = context.user_data
    user_info.pop('content_upload', "")
    user_info['content_upload'] = update.message.text
    update.message.reply_text("Ok! Now send me an image to remember!")
    return FILE_REPLY

def file_upload(update, context):
    msg = update.message
    if msg.photo:
        file_id = msg.photo[-1].file_id
        print(file_id)
    elif msg.video:
        file_id = msg.video.file_id
    elif msg.voice:
        file_id = msg.voice.file_id
    elif msg.video_note:
        file_id = msg.video_note.file_id
    user_info = context.user_data
    user_info.pop('file_upload', "")
    user_info['file_upload'] = file_id
    resend_to_check(update, context)
    return CHECK

def resend_to_check(update, context):
    inline_keyboard = [[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]]
    update.message.reply_text("Ok! Is this what you want to upload?")
    update.message.reply_text(context.user_data['content_upload'])
    update.message.reply_photo(context.user_data['file_upload'], reply_markup=InlineKeyboardMarkup(inline_keyboard))
    

def confirm_upload(update, context):
    query = update.callback_query
    query.answer()
    msg = query.message
    author = update.effective_user.first_name
    db = DbHelper(os.getenv("DATABASE_URL"))
    db.uploadMemory(author=author, content=context.user_data['content_upload'], file_id=context.user_data['file_upload'], post_date=datetime.now().date(), file_type='photo')
    msg.reply_text("Memory uploaded successfully!")
    return ConversationHandler.END

def memories(update, context):
    pointer = update.message
    if (pointer == None):
        query = update.callback_query
        query.answer()
        pointer = query.message
    inline_keyboard = [[InlineKeyboardButton("Share another one!", callback_data="another")]]
    pointer.reply_chat_action("typing")
    db = DbHelper(os.getenv("DATABASE_URL"))
    memory = db.retrieveMemory()
    print(memory)
    format_date = memory[4].strftime('%d %b %y')
    reply = "Remember " + format_date + "?\n" + memory[2] + "\n-" + memory[1]
    pointer.reply_photo(memory[3])
    pointer.reply_text(reply, reply_markup=InlineKeyboardMarkup(inline_keyboard))

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

def cancel(update, context):
    if update.callback_query:
        query = update.callback_query
        query.answer()
        msg = query.message
    else:
        msg = update.message
    msg.reply_text("cancelling upload")
    return ConversationHandler.END

def main():
    TOKEN = os.getenv("API_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    
    dispatcher = updater.dispatcher

    # commands handler
    dispatcher.add_handler(CommandHandler("start", start))

    # testing only
    # dispatcher.add_handler(MessageHandler(Filters.photo | Filters.voice | Filters.video | Filters.video_note, test_upload))

    # message handler for invalid options
    dispatcher.add_handler(MessageHandler(~Filters.chat(username=allowed_users), illegal_user))
    
    # convo handlers
    ## uploading memory convo handler
    upload_convo = ConversationHandler(
        entry_points=[CommandHandler("upload", upload)],
        states={
            CONTENT_REPLY: [MessageHandler(Filters.text & ~Filters.command, content_upload)],
            FILE_REPLY: [MessageHandler((Filters.photo | Filters.voice | Filters.video | Filters.video_note) & ~Filters.command, file_upload)],
            CHECK: [CallbackQueryHandler(confirm_upload, pattern="yes"), CallbackQueryHandler(cancel, pattern="no")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(upload_convo)

    # message handler for valid options
    ## message handler for sharing of memories
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[0]), memories))
    dispatcher.add_handler(CallbackQueryHandler(memories, pattern="another"))

    ## message handler for sharing of random photos
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[1]), cute))

    ## message handler for sharing of jokes
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[2]), joke))

    ## message handler for rants
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[3]), rant))

    dispatcher.add_handler(MessageHandler(~(Filters.regex(message_options[0]) ^ 
                                        Filters.regex(message_options[1]) ^ 
                                        Filters.regex(message_options[2]) ^ 
                                        Filters.regex(message_options[3]) ^
                                        Filters.regex('/upload')), illegal_option))

    print("Bot polling...")
    updater.start_polling()
    updater.idle()
    print("Exiting bot...")

if __name__ == '__main__':
    main()
