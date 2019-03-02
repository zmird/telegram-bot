import os, importlib
from peewee import SqliteDatabase
from settings import APPLICATIONS, DEBUG
from common import logger
from .base_model import database_proxy, BaseModel

# If debug starts an in-memory database
"""
if DEBUG:
    database = SqliteDatabase(':memory:')
else:
    database = SqliteDatabase('database.db')
"""

database = SqliteDatabase('database.db')
database.connect()
database_proxy.initialize(database)

# Imports all models inside listed app
"""
for application in filter(lambda x: x is not "database", APPLICATIONS):
    try:
        application_model = importlib.import_module(application + ".model") # Dinamic import
        logger.info("Imported {application} model".format(application=application))
    except Exception as e:
        logger.error(e)
        logger.error("Failed to import {application} model".format(application=application))
        continue
>"""


logger.debug("Database ready")