from pymongo import MongoClient
from dotenv import load_dotenv
from os import environ
from contextlib import contextmanager

load_dotenv()
HOST = environ.get("BOOKS_MONGODB_HOST")
PORT = int(environ.get("BOOKS_MONGODB_PORT", 0))


@contextmanager
def connect_to_mongo():
    if not HOST:
        raise KeyError("MongoDB host and port must both be passed")
    client = get_mongo_client()
    yield client
    client.close()


def get_mongo_client():
    return MongoClient(host=HOST, port=PORT)
