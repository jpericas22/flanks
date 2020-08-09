import os
import logging
import http.client
import json
from pymongo import MongoClient, UpdateOne
import gnupg
import validator

SERVER = os.environ['SERVER']
ROUTE = os.environ['ROUTE']
ADDRESS = os.environ['ADDRESS']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client.flanks

logging.info('starting fetcher')

def fetch():
    buffer = ''
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }
    req = {
        "address": ADDRESS
    }
    conn = http.client.HTTPSConnection(SERVER)
    conn.request('POST', ROUTE, json.dumps(req), headers)
    res = conn.getresponse()

    if(res.status != 200):
        logging.error('server did not respond with STATUS 200, received status ' + res.status)
        exit(1)
    
    print('receiving data for address ' + ADDRESS)
    while chunk := res.read(200):
        buffer += str(chunk, 'utf-8')
    
    data = {}
    try:
        data = json.loads(buffer)
    except:
        logging.error('error parsing JSON')
        exit(1)
    
    status = data['status']

    if data['status'] != 'Success':
        logging.error('server returned status "' + status)
        exit(1)

    transactions = data['transactionsData']
    insert_objs = map(build_object, transactions)
    result = insert_transactions_to_db(insert_objs)
    print(repr(result))
    


def build_object(data):
    transaction_hash = data['hash']
    final = {}
    for key in validator.WHITELIST:
        key_settings = validator.WHITELIST[key]
        if 'required' in key_settings and key_settings['required'] and key not in data:
            logging.error('missing parameter "' + key + '" for hash ' + transaction_hash)
            exit(1)
        if 'type' in key_settings and type(data[key]) != key_settings['type']:
            logging.error('invalid type for parameter "' + key + '"')
            exit(1)
        if 'middleware' in key_settings:
            try:
                data[key] = key_settings['middleware'](data[key])
            except Exception as error:
                logging.error('error in "' + key + '" middleware')
                logging.error(error)
                exit(1)
        final[key] = data[key]
    return final

def insert_transactions_to_db(data):
    requests = []
    for item in data:
        request = UpdateOne(
            {'hash': item['hash']},
            data,
            upsert=True
        )
        requests.append(request)
    transactions_collection = db['transactions_'+ADDRESS]
    result = transactions_collection.bulk_write(requests)
    return result
