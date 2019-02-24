import settings, importlib
from common import bot, logger
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def main():
    logger.info("Bot starting...")
    """Imports all applications"""
    for application in settings.APPLICATIONS:
        try:
            logger.info("Importing application " + application)
            importlib.import_module(application) # Dinamic import
        except Exception as e:
            logger.error(e)
            logger.error("Failed to import application {application} ".format(application=application))
            raise

    # Initialize bot
    updater = Updater(settings.TOKEN)
    bot.initialize(updater)

    # Imports all handlers inside listed apps
    for application in settings.APPLICATIONS:
        try:
            logger.debug("Importing " + application + " handlers")
            importlib.import_module(application + ".handlers") # Dinamic import
        except Exception as e:
            logger.debug(e)
            continue

    # Start the Bot
    bot.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    bot.idle()


if __name__ == '__main__':
    main()