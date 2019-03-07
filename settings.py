import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
LOG_LEVEL_DEBUG = True
TOKEN = config('TOKEN')

APPLICATIONS = [
    "food"
]

RESTAURANT_DEFAULT = ""