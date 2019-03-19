from common import job_queue_proxy, logger
from .model import Order


def delete_orders_periodically(bot, job):
    logger.debug("Periodical deletion of orders")
    Order.delete().execute()


job_queue_proxy.run_repeating(delete_orders_periodically, interval=3600, first=0)
