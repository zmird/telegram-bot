from database import BaseModel
from peewee import CharField, ForeignKeyField
from database import database_proxy

class Restaurant(BaseModel):
    name = CharField(unique=True)
    slug = CharField(unique=True)
    address = CharField()


class Category(BaseModel):
    restaurant = ForeignKeyField(Restaurant)
    name = CharField()
    slug = CharField()

    class Meta:
        indexes = (
            (('name', 'restaurant'), True),
            (('slug', 'restaurant'), True),
        )


class Item(BaseModel):
    category = ForeignKeyField(Category)
    name = CharField()
    slug = CharField()
    description = CharField(null=True)
    price = CharField()

    class Meta:
        indexes = (
            (('name', 'category'), True),
            (('slug', 'category'), True),
        )

models = [Restaurant, Category, Item]
database_proxy.create_tables(models, safe=True)