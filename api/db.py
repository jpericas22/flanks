import os
import sys
import math
from pymongo import MongoClient

ITEMS_PER_PAGE = 25
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
ENCODING = 'utf-8'

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def get_transactions(address, filter):
    transactions_collection = db['transactions_' + address]
    params = {}
    skip = 0
    page = 0
    if 'page' in filter:
        page = filter['page']
        skip = page * ITEMS_PER_PAGE
    if 'transaction' in filter:
        params['hash'] = filter['transaction']
    if 'from' in filter:
        params['baseTransactions.0.addressHash'] = filter['from']
    if 'to' in filter:
        params['$expr'] = {
            '$eq': [{'$arrayElemAt': ["$baseTransactions.addressHash", -1]}, filter['to']]}
    if 'date_from' in filter:
        if 'createTime' not in params:
            params['createTime'] = {}
        params['createTime']['$gte'] = filter['date_from']
    if 'date_to' in filter:
        if 'createTime' not in params:
            params['createTime'] = {}
        params['createTime']['$lte'] = filter['date_to']

    count = transactions_collection.count_documents(params)
    if(skip > count):
        skip = 0
        page = 0

    results = list(transactions_collection.find(
        params, skip=skip, limit=ITEMS_PER_PAGE, projection={'_id': 0}))
    return {
        'count': len(results),
        'countTotal': count,
        'page': page,
        'pageTotal': max([0, math.ceil(count/ITEMS_PER_PAGE - 1)]),
        'results': results
    }
