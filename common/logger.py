import logging
import settings

if settings.DEBUG:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(loglevel)

fh = logging.FileHandler('bot.log')
fh.setLevel(loglevel)

ch = logging.StreamHandler()
ch.setLevel(loglevel)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
