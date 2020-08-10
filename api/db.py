import os
import sys
import hashlib
from pymongo import MongoClient

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]

def get_transactions(address, filter):
    transactions_collection = db['transactions_'+address]
    params = {}

    if 'transaction' in filter:
        params['hash'] = filter['transaction']
    if '' in filter:
        params['hash'] = filter['transaction']

    transactions_collection.find()
