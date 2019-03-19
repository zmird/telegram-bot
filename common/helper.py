import settings, importlib
from .logger import logger


def help_message():
    help_text = ""
    for application in settings.APPLICATIONS:
        try:
            module = importlib.import_module(application)  # Dinamic import
            help_text += module.help_text()
        except Exception as e:
            logger.error("Dynamic import of help text function failed")
            logger.error(e)

    if help_text == "":
        help_text = "This bot does nothing"

    return help_text
