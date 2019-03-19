from database import BaseModel
from peewee import CharField, IntegerField, FloatField, DateTimeField, ForeignKeyField, BooleanField
from database import database_proxy
import datetime


class Restaurant(BaseModel):
    name = CharField(unique=True)
    slug = CharField(unique=True)
    address = CharField()
    selected = BooleanField(default=False)


class Category(BaseModel):
    restaurant = ForeignKeyField(Restaurant, on_delete='CASCADE')
    name = CharField()
    slug = CharField()

    class Meta:
        indexes = (
            (('name', 'restaurant'), True),
            (('slug', 'restaurant'), True),
        )


class Item(BaseModel):
    category = ForeignKeyField(Category, on_delete='CASCADE')
    name = CharField()
    slug = CharField()
    description = CharField(null=True)
    price = FloatField()

    class Meta:
        indexes = (
            (('name', 'category'), True),
            (('slug', 'category'), True),
        )


class Order(BaseModel):
    name = CharField()
    username = CharField()
    user_id = CharField()
    chat_id = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    modified_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
            (('user_id', 'chat_id'), True),
        )

    def save(self, *args, **kwargs):
        self.modified_date = datetime.datetime.now()
        return super(Order, self).save(*args, **kwargs)


class OrderItem(BaseModel):
    order = ForeignKeyField(Order, on_delete='CASCADE')
    item = ForeignKeyField(Item)
    quantity = IntegerField()

    class Meta:
        indexes = (
            (('order', 'item'), True),
        )


models = [Restaurant, Category, Item, Order, OrderItem]
database_proxy.create_tables(models, safe=True)
