from peewee import Model, Proxy

database_proxy = Proxy()  # This proxy allow to instantiate database later

# Base model to extend by all models


class BaseModel(Model):
    class Meta:
        database = database_proxy
