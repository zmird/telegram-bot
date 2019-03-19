import os, importlib
from peewee import SqliteDatabase
from settings import APPLICATIONS, DEBUG
from common import logger
from .base_model import database_proxy, BaseModel

database = SqliteDatabase('database.db',  pragmas={'foreign_keys': 1})
database.connect()
database_proxy.initialize(database)
logger.debug("Database ready")
