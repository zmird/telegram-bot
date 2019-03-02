from common import bot, logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler
from .model import Category, Item
import time, telegram, math


CATEGORIES_PER_PAGE = 4
ITEMS_PER_PAGE = 5


def navigation_buttons(prefix, current_page, last_page):
    next_page = current_page+1 if current_page+1 <= last_page else last_page
    previous_page = current_page-1 if current_page-1 >= 1 else 1
    
    buttons = []
    if previous_page != 1 :
        buttons.append(InlineKeyboardButton("<<", callback_data="{prefix}_{page}".format(prefix=prefix, page=1)))
    if current_page != 1:
        buttons.append(InlineKeyboardButton("<", callback_data="{prefix}_{page}".format(prefix=prefix, page=str(previous_page))))
    if current_page != last_page:
        buttons.append(InlineKeyboardButton(">", callback_data="{prefix}_{page}".format(prefix=prefix, page=str(next_page))))
    if next_page != last_page:
        buttons.append(InlineKeyboardButton(">>", callback_data="{prefix}_{page}".format(prefix=prefix, page=str(last_page))))

    return buttons


def category(bot, update):
    category_id = int(update.callback_query.data.split("_")[1]) if update.callback_query else 1
    current_page = int(update.callback_query.data.split("_")[2]) if update.callback_query else 1

    category = Category.select().where(Category.id == category_id).get()
    all_items = Item.select().where(Item.category == category)
    total_pages = math.ceil(len(all_items)/ITEMS_PER_PAGE)

    if total_pages > 1:
        from_item = (current_page*ITEMS_PER_PAGE) - ITEMS_PER_PAGE
        to_item = current_page*ITEMS_PER_PAGE
        
        text = "Category '{name}'\n-------------------\n".format(name=category.name)
        for item in all_items[from_item:to_item]:
            text += "<b>{name}</b>\t{price}\n<i>{description}</i>\n/order_{item_id}\n\n".format(name=item.name, 
                price=item.price, description=item.description, item_id=item.id) 

        text += "-------------------\n{current}/{total}".format(current=current_page, total=total_pages)
        keyboard = [navigation_buttons("category_{}".format(category_id), current_page, total_pages)]
        keyboard.append([InlineKeyboardButton("Categories", callback_data="categories_1")])
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=telegram.ParseMode.HTML)
    else:
        text = "Category '{name}'\n-------------------\n".format(name=category.name)
        for item in all_items:
            text += "<b>{name}</b>\t{price}\n<i>{description}</i>\n/order_{item_id}\n\n".format(name=item.name, 
                price=item.price, description=item.description, item_id=item.id) 

        text += "-------------------\n1/1"
        keyboard = [[InlineKeyboardButton("Categories", callback_data="categories_1")]]
        update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))  


def categories(bot, update):
    current_page = int(update.callback_query.data.split("_")[1]) if update.callback_query else 1

    all_categories = Category.select()
    total_pages = math.ceil(len(all_categories)/CATEGORIES_PER_PAGE)
    
    if total_pages > 1:
        from_item = (current_page*CATEGORIES_PER_PAGE) - CATEGORIES_PER_PAGE
        to_item = current_page*CATEGORIES_PER_PAGE
        keyboard = []
        for c in all_categories[from_item:to_item]:
            keyboard.append(
                [InlineKeyboardButton(c.name, callback_data="category_{}_1".format(c.id))]
            )

        keyboard.append(navigation_buttons("categories", current_page, total_pages))
    else:
        keyboard = []
        for c in all_categories:
            keyboard.append(
                [InlineKeyboardButton(c.name, callback_data="category_{}_1".format(c.id))]
            )

    if update.callback_query:
        update.callback_query.edit_message_text(text="Seleziona una categoria:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text(text="Seleziona una categoria:", reply_markup=InlineKeyboardMarkup(keyboard))

def order(bot, update):
    pass


bot.dispatcher.add_handler(CommandHandler('menu', categories))
bot.dispatcher.add_handler(CallbackQueryHandler(categories, pattern="^categories_[\d]+$"))
bot.dispatcher.add_handler(CallbackQueryHandler(category, pattern="^category_[\d]+_[\d]+$"))

