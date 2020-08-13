import os
import sys
import hashlib
import math
from pymongo import MongoClient

ITEMS_PER_PAGE = 25
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
CHUNK_SIZE = 1000

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def get_transactions(address):
    transactions_collection = db['transactions_'+address]
    transactions_count = transactions_collection.count({})
    transactions_total_chunks = math.ceil(transactions_count/CHUNK_SIZE)
    results = []
    for i in range(transactions_total_chunks):
        skip = i * CHUNK_SIZE
        items = list(transactions_collection.find(
            {}, projection={'_id': 0}, limit=CHUNK_SIZE, skip=skip))
        results.extend(items)
    return results
