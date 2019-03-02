from common import bot, logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler
from .model import Category, Item
import time, telegram



def generate_menu_page(current_page):
    items_per_page = 5
    current_category = 1
    items = []
    item_count = 0
    for category in Category.select():
        items = Item.select().where(Item.category == category.id)
        print(len(items))
        item_count += len(items)
        if item_count >= items_per_page*current_page:
            break

    starting_item = item_count - items_per_page*current_page
    last_item = starting_item+items_per_page
    page_items = items[starting_item:last_item]
    
    text = "Category " + category.name + "\n-------------------\n"
    for item in page_items:
        text += "<b>{name}</b>\t{price}\n<i>{description}</i>\n/order_{item_id}\n\n".format(name=item.name, 
            price=item.price, description=item.description, item_id=item.id) 

    text += "-------------------" + "\n" + str(current_page)

    return text
    

def menu(bot, update):
    keyboard = [[
        InlineKeyboardButton("<<", callback_data='0'),
        InlineKeyboardButton("<", callback_data='1'),
        InlineKeyboardButton(">", callback_data='2'),
        InlineKeyboardButton(">>", callback_data='3')
    ]]

    update.message.reply_text(text=generate_menu_page(1), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=telegram.ParseMode.HTML)
    #bot.send_message(chat_id=update.message.chat_id, text=generate_menu_page(1), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=telegram.ParseMode.HTML)
    #bot.send_message(chat_id=update.message.chat_id, text="<b>bold</b> \n <i>italic</i> <a href='http://google.com'>link</a>.", parse_mode=telegram.ParseMode.HTML)


def next_page(bot, update):
    query = update.callback_query
    current_page = int(query.data)
    keyboard = [[
        InlineKeyboardButton("<<", callback_data=str(current_page-2)),
        InlineKeyboardButton("<", callback_data=str(current_page-1)),
        InlineKeyboardButton(">", callback_data=str(current_page+1)),
        InlineKeyboardButton(">>", callback_data=str(current_page+2))
    ]]
    text = "{}".format(generate_menu_page(current_page))
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


def order(bot, update):
    item_id = int(update.message.text.replace('/order_', ''))
    try:
        item = Item.get(Item.id == item_id)
        update.message.reply_text("Added {item_name} to order".format(item_name=item.name))
    except:
        update.message.reply_text("Item not found")
        

def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

bot.dispatcher.add_handler(CommandHandler('menu', menu))
bot.dispatcher.add_handler(CallbackQueryHandler(next_page))
bot.dispatcher.add_handler(RegexHandler('^/order_[\d]+$', order))
bot.dispatcher.add_handler(CommandHandler('help', help))
bot.dispatcher.add_error_handler(error)