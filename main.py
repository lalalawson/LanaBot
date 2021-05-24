from datetime import datetime
import time
import Joke
from logging import Filter
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.message import Message
from DbHelper import DbHelper
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import os
from dotenv import load_dotenv

load_dotenv()

# states
CONTENT_REPLY, FILE_REPLY, DATE_REPLY, CHECK = range(4)
SETUP_REPLY, DELIVERY_REPLY, CONFIRM = range(4, 7)

allowed_users = ["lalalawson", "linawoo"]

message_options = ["Tell me about us.. 😌", "Show me photos! 😆", "Tell me a joke! 😒", "I just wna rant... 😔"]

button_row1 = [KeyboardButton(message_options[0]), KeyboardButton(message_options[1])]
button_row2 = [KeyboardButton(message_options[2]), KeyboardButton(message_options[3])]
buttons = [button_row1, button_row2]
reply_keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)

last_memories_id =  []
last_joke_id = []

def start(update, context):
    username = update.effective_user.username

    # perform check on allowed users
    if username in allowed_users:
        update.message.reply_text("Hello " + username + "!\n" + \
            "This bot was created to commemorate our first year together 🥳\n" + \
            "What do you require today? 😚\n" + \
            "(P.S., you can also upload your own memory via /upload)", reply_markup=reply_keyboard)
    else:
        update.message.reply_text("Sorry " + username + "! This is a private bot so it's not available for your viewing! 😅")

def upload(update, context):
    update.message.reply_text("Ooo!! Uploading a new memory? 😋 Send me the description of our memory!\n" + \
        "/cancel anytime you want to quit!")
    return CONTENT_REPLY

def content_upload(update, context):
    user_info = context.user_data
    user_info.pop('content_upload', "")
    user_info['content_upload'] = update.message.text
    update.message.reply_text("Ok! 👌🏼 Now send me an image/video/voice/video note to remember!")
    return FILE_REPLY

def content_checker(update, context):
    update.message.reply_text("This is invalid right now! Please submit a text only description! To quit upload, /cancel")
    return CONTENT_REPLY

def file_upload(update, context):
    msg = update.message
    if msg.photo:
        file_id = msg.photo[-1].file_id
        file_type = 'photo'
    elif msg.video:
        file_id = msg.video.file_id
        file_type = 'video'
    elif msg.voice:
        file_id = msg.voice.file_id
        file_type = 'voice'
    elif msg.video_note:
        file_id = msg.video_note.file_id
        file_type = 'video_note'
    user_info = context.user_data
    user_info.pop('file_upload', "")
    user_info.pop('file_type', "")
    user_info['file_upload'] = file_id
    user_info['file_type'] = file_type
    # resend_to_check(update, context)
    calendar, step = DetailedTelegramCalendar().build()
    update.message.reply_text(f"Select {LSTEP[step]}", reply_markup=calendar)
    return DATE_REPLY

def file_checker(update, context):
    update.message.reply_text("This is invalid right now! Please only upload an image/video/voice note/video note!")
    return FILE_REPLY

def calendar(update, context):
    DetailedTelegramCalendar.func()
    query = update.callback_query
    query.answer()
    msg = query.message
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        msg.edit_text(f"Select {LSTEP[step]}",
                              reply_markup=key)
    elif result:
        context.user_data['date'] = result
        resend_to_check(query, context)
        return CHECK

def date_checker(update, context):
    update.message.reply_text("This is invalid right now! Please select the date, or /cancel to quit!")
    return DATE_REPLY

def resend_to_check(update, context):
    inline_keyboard = [[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]]
    update.message.reply_text("Ok! 👌🏼 Is this what you want to upload?")
    pointer = update.message
    file = context.user_data['file_upload']
    file_type = context.user_data['file_type']
    if (file_type == "photo"):
        pointer.reply_photo(file)
    elif (file_type == "video"):
        pointer.reply_video(file)
    elif (file_type == "voice"):
        pointer.reply_voice(file)
    elif (file_type == "video_note"):
        pointer.reply_video_note(file)
    pointer.reply_text("Date: " + str(context.user_data['date']) + "\n" + context.user_data['content_upload'], reply_markup=InlineKeyboardMarkup(inline_keyboard))
    
def confirm_upload(update, context):
    query = update.callback_query
    query.answer()
    msg = query.message
    msg.reply_chat_action("upload_document")
    author = update.effective_user.first_name
    db = DbHelper(os.getenv("DATABASE_URL"))
    db.uploadMemory(author=author, 
                    content=context.user_data['content_upload'], 
                    file_id=context.user_data['file_upload'], 
                    post_date=context.user_data['date'], 
                    file_type=context.user_data['file_type'])
    msg.reply_text("Memory uploaded successfully! 😉")
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
    while (memory[0] in last_memories_id):
        print("just shared recently, picking another memory")
        memory = db.retrieveMemory()
    else:
        print(memory)
        if (len(last_memories_id) > 2):
            last_memories_id.pop(0)
        last_memories_id.append(memory[0])
        format_date = memory[4].strftime('%d %b %y')
        file_type = memory[5]
        reply = "Remember " + format_date + "?\n" + memory[2] + "\n-" + memory[1]
        if (file_type == "photo"):
            pointer.reply_photo(memory[3])
        elif (file_type == "video"):
            pointer.reply_video(memory[3])
        elif (file_type == "voice"):
            pointer.reply_voice(memory[3])
        elif (file_type == "video_note"):
            pointer.reply_video_note(memory[3])
        pointer.reply_text(reply, reply_markup=InlineKeyboardMarkup(inline_keyboard))


def cute(update, context):
    update.message.reply_text("wah cute")

def joke(update, context):
    inline_keyboard = [[InlineKeyboardButton("Lawson's joke! 👍🏼", callback_data="lawson_joke")], [InlineKeyboardButton("Random joke.. 👎🏼", callback_data="random_joke")]]
    update.message.reply_text("Seems like you could use a laugh! Shall I hit you up with a joke from Lawson's joke archive or a random joke?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard))
    
def lawson_joke(update, context):
    query = update.callback_query
    query.answer()
    pointer = query.message
    pointer.reply_chat_action("typing")
    db = DbHelper(os.getenv("DATABASE_URL"))
    setup, delivery = db.retrieveJoke()
    pointer.reply_text(setup)
    time.sleep(1)
    replied = pointer.reply_text("▪️")
    time.sleep(1)   
    replied.edit_text("▪️▪️")    
    time.sleep(1)   
    replied.edit_text("▪️▪️▪️")
    time.sleep(0.7)   
    pointer.reply_text(delivery) 

def random_joke(update, context):
    query = update.callback_query
    query.answer()
    pointer = query.message
    pointer.reply_chat_action("typing")
    setup, delivery = Joke.random_joke()
    pointer.reply_text(setup)
    time.sleep(1)
    replied = pointer.reply_text("▪️")
    time.sleep(1)   
    replied.edit_text("▪️▪️")    
    time.sleep(1)   
    replied.edit_text("▪️▪️▪️")
    time.sleep(0.7)   
    pointer.reply_text(delivery)

def start_joke_upload(update, context):
    update.message.reply_text("Think you are funny? 😋 Ok! Share with me your joke! Start with the question!\n" + \
        "/cancel anytime you want to quit!")
    return SETUP_REPLY

def setup_upload(update, context):
    user_info = context.user_data
    user_info.pop('joke_setup', "")
    user_info['joke_setup'] = update.message.text
    update.message.reply_text("Ok! 👌🏼 Now send me the answer to joke!")
    return DELIVERY_REPLY

def setup_checker(update, context):
    update.message.reply_text("This is invalid right now! Please submit text only! To quit sharing, /cancel")
    return SETUP_REPLY

def delivery_upload(update, context):
    user_info = context.user_data
    user_info.pop('joke_delivery', "")
    user_info['joke_delivery'] = update.message.text
    update.message.reply_text("Wah funny leh....")
    joke_to_check(update, context)
    return CONFIRM

def delivery_checker(update, context):
    update.message.reply_text("This is invalid right now! Please submit text only! To quit sharing, /cancel")
    return DELIVERY_REPLY

def joke_to_check(update, context):
    inline_keyboard = [[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]]
    update.message.reply_text("Ok! 👌🏼 Is this the joke you wna add to our archive?")
    pointer = update.message
    setup = context.user_data['joke_setup']
    delivery = context.user_data['joke_delivery']
    pointer.reply_text('Q: ' + setup)
    pointer.reply_text('A: ' + delivery, reply_markup=InlineKeyboardMarkup(inline_keyboard))

def upload_joke(update, context):
    query = update.callback_query
    query.answer()
    msg = query.message
    msg.reply_chat_action("upload_document")
    db = DbHelper(os.getenv("DATABASE_URL"))
    db.uploadJoke(setup=context.user_data['joke_setup'], delivery=context.user_data['joke_delivery'])
    msg.reply_text("Joke uploaded successfully! 😉")
    return ConversationHandler.END


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
    msg.reply_text("Upload cancelled!")
    return ConversationHandler.END

def button_flag(update, context):
    update.message.reply_text("Hey! Please only press the yes or no buttons!")
    return CHECK

def main():
    TOKEN = os.getenv("API_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    
    dispatcher = updater.dispatcher

    # commands handler
    dispatcher.add_handler(CommandHandler("start", start))

    # message handler for illegal users
    dispatcher.add_handler(MessageHandler(~Filters.chat(username=allowed_users), illegal_user))
    
    # convo handlers
    ## uploading memory convo handler
    upload_convo = ConversationHandler(
        entry_points=[CommandHandler("upload", upload)],
        states={
            CONTENT_REPLY: [MessageHandler(Filters.text & ~Filters.command, content_upload), 
                            MessageHandler(Filters.all & ~Filters.regex('/cancel'), content_checker)],
            FILE_REPLY: [MessageHandler((Filters.photo | Filters.voice | Filters.video | Filters.video_note) & ~Filters.command, file_upload), 
                        MessageHandler(Filters.all & ~(Filters.photo & Filters.voice & Filters.video & Filters.video_note) & ~Filters.regex('/cancel'), file_checker)],
            DATE_REPLY: [CallbackQueryHandler(calendar), 
                        MessageHandler(Filters.all & ~Filters.regex('/cancel'), date_checker)],
            CHECK: [CallbackQueryHandler(confirm_upload, pattern="yes"), CallbackQueryHandler(cancel, pattern="no"), MessageHandler(Filters.all & ~Filters.regex('/cancel'), button_flag)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dispatcher.add_handler(upload_convo)

    ## upload joke convo handler
    joke_convo = ConversationHandler(
        entry_points=[CommandHandler("share_joke", start_joke_upload)],
        states={
            SETUP_REPLY: [MessageHandler(Filters.text & ~Filters.command, setup_upload), 
                            MessageHandler(Filters.all & ~Filters.regex('/cancel'), setup_checker)],
            DELIVERY_REPLY: [MessageHandler(Filters.text & ~Filters.command, delivery_upload), 
                            MessageHandler(Filters.all & ~Filters.regex('/cancel'), delivery_checker)],
            CONFIRM: [CallbackQueryHandler(upload_joke, pattern="yes"), CallbackQueryHandler(cancel, pattern="no"), MessageHandler(Filters.all & ~Filters.regex('/cancel'), button_flag)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(joke_convo)
    # message handler for valid options
    ## message handler for sharing of memories
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[0]), memories))
    dispatcher.add_handler(CallbackQueryHandler(memories, pattern="another"))

    ## message handler for sharing of random photos
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[1]), cute))

    ## message handler for sharing of jokes
    dispatcher.add_handler(MessageHandler(Filters.regex(message_options[2]), joke))
    dispatcher.add_handler(CallbackQueryHandler(lawson_joke, pattern="lawson_joke"))
    dispatcher.add_handler(CallbackQueryHandler(random_joke, pattern="random_joke"))

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
