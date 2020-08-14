import os
import sys
import pika
import http.client
import json
import math
from pymongo import MongoClient, UpdateOne, InsertOne
import validator
import crypto
from functools import reduce, partial

HOSTNAME = os.environ['FETCH_HOSTNAME']
PATH = os.environ['FETCH_PATH']
ADDRESS = os.environ['ADDRESS']
SHEET_ID = os.environ['SHEET_ID']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
ENCODING = 'utf-8'
CHUNK_SIZE = 1000


mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def build_object(data):
    transaction_hash = data['hash']
    final = {}

    for key in validator.WHITELIST:
        key_settings = validator.WHITELIST[key]
        if 'required' in key_settings and key_settings['required'] and (key not in data or data[key] is None):
            sys.stderr.write('missing parameter "' + key +
                             '" for hash ' + transaction_hash + '\n')
            exit(1)
        if key not in data or data[key] is None:
            data[key] = None
        else:
            if 'type' in key_settings and type(data[key]) != key_settings['type']:
                sys.stderr.write('invalid type for parameter "' + key + '"\n')
                sys.stderr.write(
                    'received "' + str(data[key]) + '" ' + str(type(data[key])) + '\n')
                exit(1)
            if 'middleware' in key_settings:
                try:
                    data[key] = key_settings['middleware'](data[key])
                except Exception as error:
                    sys.stderr.write('error in "' + key + '" middleware\n')
                    sys.stderr.write(error)
                    exit(1)
            if 'encrypt' in key_settings and key_settings['encrypt']:
                data[key] = crypto.encrypt(data[key], ADDRESS)

        final[key] = data[key]
    return final


def find_transaction(full_list, transaction):
    for item in full_list:
        if transaction['hash'] == item['hash']:
            return item
    return None


def classify_transaction_ops(qa, qb, db_transactions):
    try:
        filter_result = find_transaction(db_transactions, qb)
        if filter_result is None:
            return {
                'insert': qa['insert']+[qb],
                'update': qa['update']
            }
        if not filter_result['trustChainConsensus']:
            request = UpdateOne(
                {'hash': qb['hash']},
                {'$set': qb},
                upsert=True
            )
            return {
                'insert': qa['insert'],
                'update': qa['update']+[request]
            }
        return {
            'insert': qa['insert'],
            'update': qa['update']
        }
    except ValueError:
        return {
            'insert': qa['insert']+[qb],
            'update': qa['update']
        }


def insert_transactions_to_db(data):
    stats = {
        'inserted': 0,
        'upserted': 0,
        'modified': 0
    }
    transactions_collection = db['transactions_' + ADDRESS]
    transactions_collection.create_index(
        'hash', background=False, name='hash_index')

    db_transactions = list(transactions_collection.find(
        {}, {'_id': 0, 'hash': 1, 'trustChainConsensus': 1}, hint='hash_index'))
    if len(db_transactions) == 0:
        result = transactions_collection.insert_many(data, ordered=False)
        stats['inserted'] = len(result.inserted_ids)
        return stats

    db_queries = reduce(partial(classify_transaction_ops, db_transactions=db_transactions), data, {
        'insert': [],
        'update': []
    })
    if len(db_queries['insert']) > 0:
        result = transactions_collection.insert_many(
            db_queries['insert'], ordered=False)
        stats['inserted'] = len(result.inserted_ids)
    if len(db_queries['update']) > 0:
        result = transactions_collection.bulk_write(
            db_queries['update'], ordered=False)
        result_stats = result.bulk_api_result
        stats['upserted'] = result_stats['nUpserted']
        stats['modified'] = result_stats['nModified']
    return stats


sys.stdout.write('started fetch service\n')

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}
req = {
    'address': ADDRESS
}
conn = http.client.HTTPSConnection(HOSTNAME)
conn.request('POST', PATH, json.dumps(req), headers)
res = conn.getresponse()

if res.status != 200:
    sys.stderr.write('received server status ' + str(res.status) + '\n')
    exit(1)

sys.stdout.write('fetching data for address ' + ADDRESS + '\n')

buffer = ''
while chunk := res.read(200):
    buffer += str(chunk, ENCODING)
data = {}
try:
    data = json.loads(buffer)
except:
    sys.stderr.write('error parsing JSON\n')
    exit(1)

status = data['status']
if data['status'] != 'Success':
    sys.stderr.write('server returned status "' + status + '"\n')
    exit(1)

transactions = data['transactionsData']
sys.stdout.write('processing ' + str(len(transactions)) + ' entries\n')
insert_objs = list(map(build_object, transactions))
stats = insert_transactions_to_db(insert_objs)
sys.stdout.write('processing finished\n')
sys.stdout.write('rows inserted: ' + str(stats['inserted']) + '\n')
sys.stdout.write('rows upserted: ' + str(stats['upserted']) + '\n')
sys.stdout.write('rows modified: ' + str(stats['modified']) + '\n')

if stats['inserted'] > 0 or stats['upserted'] > 0 or stats['modified'] > 0:
    sys.stdout.write('received updates\n')
    message = {
        'action': 'update',
        'address': ADDRESS,
        'sheet_id': SHEET_ID
    }
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('queue'))
    channel = connection.channel()
    channel.queue_declare(queue='sheets')
    channel.basic_publish(exchange='',
                          routing_key='sheets',
                          body=json.dumps(message))
    connection.close()
