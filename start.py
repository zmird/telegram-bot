import settings, importlib
from common import bot, logger, help_text
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import database


def help(bot, update):
    update.message.reply_text(help_text)


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
            logger.debug("Importing {application_name} handlers".format(application_name=application))
            importlib.import_module(application + ".handlers") # Dinamic import
        except Exception as e:
            logger.debug(e)
            continue

    updater.dispatcher.add_handler(CommandHandler("help", help))

    # Start the Bot
    bot.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    bot.idle()


if __name__ == '__main__':
    main()