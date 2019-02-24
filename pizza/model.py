from database import BaseModel
from peewee import CharField, ForeignKeyField
from database import database_proxy

class Restaurant(BaseModel):
    name = CharField()
    address = CharField()


class Category(BaseModel):
    name = CharField()
    restaurant = ForeignKeyField(Restaurant)


class Item(BaseModel):
    name = CharField()
    description = CharField()
    price = CharField()
    category = ForeignKeyField(Category)


models = [Restaurant, Category, Item]
database_proxy.create_tables(models, safe=True)