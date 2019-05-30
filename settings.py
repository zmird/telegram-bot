import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = False
TOKEN = config('TOKEN')

APPLICATIONS = [
    "food"
]