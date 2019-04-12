from common import bot_proxy, logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, RegexHandler
from .model import Category, Item, Order, OrderItem, Restaurant
import telegram
import math
import datetime

RESTAURANT_PER_PAGE = 4
CATEGORIES_PER_PAGE = 4
ITEMS_PER_PAGE = 5
ORDER_TIMEOUT = 2  # seconds


def navigation_buttons(prefix, current_page, last_page):
    # Calculate next page
    next_page = current_page+1 if current_page+1 <= last_page else last_page
    previous_page = current_page-1 if current_page-1 >= 1 else 1

    # Add buttons only if needed
    buttons = []
    if previous_page != 1:
        buttons.append(InlineKeyboardButton(
            "<<", callback_data="{prefix}_{page}".format(prefix=prefix, page=1)))
    if current_page != 1:
        buttons.append(InlineKeyboardButton("<", callback_data="{prefix}_{page}".format(
            prefix=prefix, page=str(previous_page))))
    if current_page != last_page:
        buttons.append(InlineKeyboardButton(
            ">", callback_data="{prefix}_{page}".format(prefix=prefix, page=str(next_page))))
    if next_page != last_page:
        buttons.append(InlineKeyboardButton(
            ">>", callback_data="{prefix}_{page}".format(prefix=prefix, page=str(last_page))))

    return buttons


def restaurants(bot, update):
    # Get current page
    current_page = int(update.callback_query.data.split("_")
                       [1]) if update.callback_query else 1

    # Retrieve restaurants from database
    all_restaurants = Restaurant.select()

    # Get page
    restaurant_page = all_restaurants.paginate(
        page=current_page, paginate_by=RESTAURANT_PER_PAGE)

    # Calculate max number of pages
    total_pages = math.ceil(len(all_restaurants)/RESTAURANT_PER_PAGE)

    keyboard = []

    # Create list of buttons, each containg the id of a restaurant
    # The format of the callback on the button is:
    # 'restaurant_1' for a a restaurant with id 1
    for r in restaurant_page:
        keyboard.append(
            [InlineKeyboardButton(
                r.name, callback_data="restaurant_{restaurant_id}".format(restaurant_id=r.id))]
        )

    # If the number of total pages is higher than 1 then we need navigation buttons
    if total_pages > 1:
        keyboard.append(navigation_buttons(
            "restaurants", current_page, total_pages))

    # If 'callback_query' is defined means that we are responding to a click on an already existing message that
    # needs to be edit
    if update.callback_query:
        update.callback_query.edit_message_text(
            text="Seleziona un ristorante:", reply_markup=InlineKeyboardMarkup(keyboard))
    # Sends a new message
    else:
        update.message.reply_text(
            text="Seleziona un ristorante:", reply_markup=InlineKeyboardMarkup(keyboard))


"""TODO: this call let the user choose which restaurant to want they order from"""


def select_restaurant(bot, update):
    pass


# Menu alias
def categories(bot, update):
    # Parse current page argument
    current_page = int(update.callback_query.data.split("_")
                       [1]) if update.callback_query else 1

    # Retrieve current active restaurant for next query
    restaurant_selected = Restaurant.select().where(
        Restaurant.selected == True).get()

    # Retrieve restaurant menu
    all_categories = Category.select().where(
        Category.restaurant == restaurant_selected)

    # Get page
    category_page = all_categories.paginate(
        page=current_page, paginate_by=CATEGORIES_PER_PAGE)

    # Retrieve total page number
    total_pages = math.ceil(len(all_categories) / CATEGORIES_PER_PAGE)

    # List category page
    keyboard = []
    for c in category_page:
        keyboard.append(
            [InlineKeyboardButton(
                c.name, callback_data="category_{}_1".format(c.id))]
        )

    # If there is more than one page then navigation buttons are needed
    if total_pages > 1:
        keyboard.append(navigation_buttons(
            "categories", current_page, total_pages))

    # If 'callback_query' is defined means that we are responding to a click on an already existing message that
    # needs to be edit
    if update.callback_query:
        update.callback_query.edit_message_text(text="Seleziona una categoria:",
                                                reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        update.message.reply_text(
            text="Seleziona una categoria:", reply_markup=InlineKeyboardMarkup(keyboard))


def category(bot, update):
    # Retrieve arguments: category and current page
    category_selected = int(update.callback_query.data.split("_")[
                            1]) if update.callback_query else 1
    current_page = int(update.callback_query.data.split("_")
                       [2]) if update.callback_query else 1

    # Retrieve category from database
    category = Category.select().where(Category.id == category_selected).get()

    # Retrieve items in category
    all_items = Item.select().where(Item.category == category)

    item_page = all_items.paginate(
        page=current_page, paginate_by=ITEMS_PER_PAGE)

    # Calculate total possible pages
    total_pages = math.ceil(len(all_items)/ITEMS_PER_PAGE)

    # Message containing items in selected category
    text = "Category '{name}'\npage {current}/{total}\n-------------------\n" \
        .format(name=category.name, current=current_page, total=total_pages)
    for item in item_page:
        text += "<b>{name}</b>  {price:.2f} €\n<i>{description}</i>\n/order_{item_id}\n\n" \
            .format(name=item.name, price=item.price, description=item.description, item_id=item.id)

    # Control buttons
    keyboard = []

    # If there is more than one page then navigation buttons are needed
    if total_pages > 1:
        keyboard.append(navigation_buttons("category_{}".format(
            category_selected), current_page, total_pages))

    # Button to return to category list
    keyboard.append([InlineKeyboardButton(
        "Categories", callback_data="categories_1")])

    update.callback_query.edit_message_text(text=text, parse_mode=telegram.ParseMode.HTML,
                                            reply_markup=InlineKeyboardMarkup(keyboard))


def order(bot, update):
    try:
        # Argument: selected item
        item_id = int(update.message.text.replace('/order_', '').split('@')[0])
    except:
        logger.info("Food order handler: Failed to parse {} as an item id".format(
            update.message.text))
        return

    try:
        # Selected item
        item = (Item
                .select()
                .join(Category)
                .join(Restaurant)
                .where((Category.id == Item.category)
                       & (Restaurant.id == Category.restaurant)
                       & (Restaurant.selected == True)
                       & (Item.id == item_id))
                .get())

        # User informations
        username = update.message.from_user.username
        name = update.message.from_user.first_name
        user_id = update.message.from_user.id

        # Chat where the order is coming from
        chat_id = update.message.chat.id

        # Retrieve order created by the user
        order = Order.select().where((Order.user_id == user_id) & (Order.chat_id == chat_id))

        # If the order does not exist, create a new one
        if not order.exists():
            order = Order.create(
                chat_id=chat_id, user_id=user_id, username=username, name=name)
            order.save()
        elif (datetime.datetime.now() - order.get().modified_date).total_seconds() < ORDER_TIMEOUT:
            logger.info("Food order handler: timeout for user {}, two orders is less than {}.".format(
                username, ORDER_TIMEOUT))
            return

        # If the item was already ordered then increase quantity
        order_item = OrderItem.select().where(
            (OrderItem.order == order) & (OrderItem.item == item))
        if not order_item.exists():
            OrderItem.insert(
                order=order,
                item=item,
                quantity=1
            ).execute()
            # Disable response because chat flooding
            # update.message.reply_text("Added {item_name} to order".format(item_name=item.name))
        else:
            OrderItem \
                .update({OrderItem.quantity: OrderItem.quantity+1}) \
                .where(OrderItem.order == order and OrderItem.item == item) \
                .execute()
            # Disable response because chat flooding
            # update.message.reply_text("Added another {item_name} to order".format(item_name=item.name))
    except Exception as e:
        logger.debug(e)
        update.message.reply_text("Error: failed to create make order.")


def delete_order(bot, update):
    # user that requested the item
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    # Delete order, 'OrderItem' associated will be deleted too
    Order.delete().where((Order.user_id == user_id) &
                         (Order.chat_id == chat_id)).execute()
    update.message.reply_text("Deleted order")


def myorder(bot, update):
    # Source user and chat
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    # Retrieve order
    order = Order.select().where((Order.user_id == user_id) & (Order.chat_id == chat_id))

    if not order.exists():
        update.message.reply_text("You order is empty")
        return

    total_price = 0
    text = ""
    for order_item in OrderItem.select().where(OrderItem.order == order):
        text += "{item_name}  <b>x{quantity}</b>\n".format(
            item_name=order_item.item.name, quantity=order_item.quantity)
        total_price += order_item.item.price * order_item.quantity

    text += "\nTotal price: {total:.2f} €".format(total=total_price)
    update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML)


def summary(bot, update):
    # Source chat
    chat_id = update.message.chat.id

    # Retrieve all items
    items = {}
    for order_item in OrderItem.select(OrderItem, Order).join(Order).where(OrderItem.order.chat_id == chat_id):
        item = order_item.item
        if item in items:
            items[item] += order_item.quantity
        else:
            items[item] = order_item.quantity

    if len(items) == 0:
        update.message.reply_text("No order created yet")
        return

    total_price = 0
    text = ""
    for item in items.keys():
        text += "<b>x{quantity}</b>  <i>{item_name}</i>\n".format(
            item_name=item.name, quantity=items[item])
        total_price += item.price * items[item]

    text += "\nTotal price: {total:.2f} €".format(total=total_price)
    update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML)


def listorders(bot, update):
    # Source chat
    chat_id = update.message.chat.id

    # Retrieve all orders
    orders = Order.select().where(Order.chat_id == chat_id)

    if orders.count() == 0:
        update.message.reply_text(
            text="No order has been made yet.", parse_mode=telegram.ParseMode.HTML)
        return

    # List order by user
    text = ""
    for order in orders:
        user_first_name = order.name
        total_price = 0
        text += "<b>{name}</b>:\n".format(name=user_first_name)
        for order_item in OrderItem.select().where(OrderItem.order == order):
            text += "<i>{name}</i> <b>x{quantity}</b>  ".format(
                name=order_item.item.name, quantity=order_item.quantity)
            total_price += order_item.item.price * order_item.quantity

        text += "\n<b>{total:.2f}</b> €\n\n".format(total=total_price)

    update.message.reply_text(text=text, parse_mode=telegram.ParseMode.HTML)


# bot_proxy.dispatcher.add_handler(CallbackQueryHandler(restaurants, pattern="^restaurants_[\d]+$"))
# bot_proxy.dispatcher.add_handler(CallbackQueryHandler(select_restaurant, pattern="^restaurant_[\d]+_[\d]+$"))
# bot_proxy.dispatcher.add_handler(CommandHandler('restaurants', restaurants))
bot_proxy.dispatcher.add_handler(CommandHandler('menu', categories))
bot_proxy.dispatcher.add_handler(CallbackQueryHandler(
    categories, pattern="^categories_[\d]+$"))
bot_proxy.dispatcher.add_handler(CallbackQueryHandler(
    category, pattern="^category_[\d]+_[\d]+$"))
bot_proxy.dispatcher.add_handler(RegexHandler('^/order_[\d]+$', order))
bot_proxy.dispatcher.add_handler(RegexHandler(
    '^/order_[\d]+@[a-zA-Z0-9_-]+$', order))
bot_proxy.dispatcher.add_handler(CommandHandler('deleteorder', delete_order))
bot_proxy.dispatcher.add_handler(CommandHandler('myorder', myorder))
bot_proxy.dispatcher.add_handler(CommandHandler('summary', summary))
bot_proxy.dispatcher.add_handler(CommandHandler('listorders', listorders))
