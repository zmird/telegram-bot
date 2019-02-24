from common import bot, logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from .model import Category, Item
import time


default_category = 1
item_range = 10
category_range = 4


def generate_text(category=default_category):
    items = Item.select().where(Item.category == category)
    text = ""
    for item in items[0:item_range]:
        text += item.name + '\n'

    return text


def generate_buttons(category=default_category):
    keyboard = [[
        InlineKeyboardButton("<", callback_data='left'),
        InlineKeyboardButton(">", callback_data='right')
    ]]
    for category in Category.select().where(default_category <= Category.id <= (default_category+category_range)):
        keyboard.append([InlineKeyboardButton(category.name, callback_data=str(category.id))])
    
    keyboard.append([
        InlineKeyboardButton("<", callback_data='category_left'),
        InlineKeyboardButton(">", callback_data='category_right')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
    

def start(bot, update):
    keyboard = []
    for category in Category.select():
        keyboard.append([InlineKeyboardButton(category.name, callback_data=str(category.id))])

    update.message.reply_text(generate_text(), reply_markup=generate_buttons())


def press_button(bot, update):
    query = update.callback_query
    category = Category.select().where(Category.id == query.data).get()

    query.edit_message_text(text="Categoria {}:\n{}".format(category.name, generate_text(category)), reply_markup=generate_buttons())


def echo(bot, update):
    # Any send_* methods return the sent message object
    msg = update.message.reply_text("Sorry, you're on your own, kiddo.")
    time.sleep(5)
    # you can explicitly enter the details
    bot.edit_message_text(chat_id=update.message.chat_id, 
                          message_id=msg.message_id,
                          text="Seriously, you're on your own, kiddo.")
    # or use the shortcut (which pre-enters the chat_id and message_id behind)
    msg.edit_text("Seriously, you're on your own, kiddo.")


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

bot.dispatcher.add_handler(CommandHandler('start', start))
bot.dispatcher.add_handler(CallbackQueryHandler(press_button))
bot.dispatcher.add_handler(CommandHandler('help', echo))
bot.dispatcher.add_error_handler(error)