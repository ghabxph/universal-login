from pymongo import MongoClient as mongo_client
from lib.util import config


class Mongo:

    __conn__ = None

    @staticmethod
    def conn():
        if Mongo.__conn__ is None:
            conn = mongo_client(host=config('UL_DB_HOST'))
            conn[config('UL_DB_NAME')].authenticate(name=config('UL_DB_USER'), password=config('UL_DB_PASS'))
            Mongo.__conn__ = conn

        return Mongo.__conn__

    @staticmethod
    def db():
        return Mongo.conn()[config('UL_DB_NAME')]


def mongo():
    return Mongo.conn()


def db():
    return Mongo.db()
