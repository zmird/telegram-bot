import settings, importlib
from common import bot_proxy, job_queue_proxy, logger, help_message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import database


def help(bot, update):
    update.message.reply_text(help_message())


def main():
    logger.info("Bot starting...")

    # Initialize bot
    updater = Updater(settings.TOKEN)
    bot_proxy.initialize(updater)
    job_queue_proxy.initialize(updater.job_queue)

    """Dynamically imports all applications"""
    for application in settings.APPLICATIONS:
        try:
            logger.info("Importing application " + application)
            importlib.import_module(application)  # Dinamic import
        except Exception as e:
            logger.error(e)
            logger.error("Failed to import application {application} ".format(application=application))
            raise

    updater.dispatcher.add_handler(CommandHandler("help", help))

    # Start the Bot
    bot_proxy.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # bot_proxy.idle()


if __name__ == '__main__':
    main()
