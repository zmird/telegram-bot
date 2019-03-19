from common import job_queue_proxy, logger
from .model import Order
from peewee import fn
import datetime

# 5 HOURS = 18000 SECONDS
ORDER_EXPIRES_AFTER = 18000


def delete_orders_periodically(bot, job):
    logger.debug("Periodical deletion of orders")
    orders = Order.select(Order.id, Order.chat_id, Order.modified_date, fn.Max(Order.modified_date))

    for order in orders:
        if (datetime.datetime.now() - order.modified_date).total_seconds() > ORDER_EXPIRES_AFTER:
            order.delete().execute()
            logger.info("Order  from chat {chat_id} has been deleted".format(chat_id=order.chat_id))


# 30 MINUTES = 1800 SECONDS
job_queue_proxy.run_repeating(delete_orders_periodically, interval=1800, first=0)
