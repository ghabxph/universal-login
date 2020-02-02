from pymongo import MongoClient as mongo_client
import os


class Mongo:

    __conn__ = None

    @staticmethod
    def conn():
        if Mongo.__conn__ is None:
            conn = mongo_client(host=os.environ.get('UL_DB_HOST'))
            conn[os.environ.get('UL_DB_NAME')].authenticate(name=os.environ.get('UL_DB_USER'), password=os.environ.get('UL_DB_PASS'))
            Mongo.__conn__ = conn

        return Mongo.__conn__

    @staticmethod
    def db():
        return Mongo.conn()[os.environ.get('UL_DB_NAME')]


def mongo():
    return Mongo.conn()


def db():
    return Mongo.db()
