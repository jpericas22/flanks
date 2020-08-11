import os
import sys
import hashlib
import math
from pymongo import MongoClient

ITEMS_PER_PAGE = 25
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def get_transactions(address):
    transactions_collection = db['transactions_'+address]
    results = list(transactions_collection.find(
        {}, projection={'_id': 0}))
    return results
