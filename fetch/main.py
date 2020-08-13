import os
import sys
import pika
import http.client
import json
from pymongo import MongoClient, UpdateOne
import validator
from pprint import pprint
import init_db
import crypto
from functools import reduce

HOSTNAME = os.environ['FETCH_HOSTNAME']
PATH = os.environ['FETCH_PATH']
ADDRESS = os.environ['ADDRESS']
SHEET_ID = os.environ['SHEET_ID']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
ENCODING = 'utf-8'
CHUNK_SIZE = 2000


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


def collect_insert_results(ra, rb):
    return {
        'upserted': ra['upserted'] + rb.bulk_api_result['nUpserted'],
        'modified': ra['modified'] + rb.bulk_api_result['nModified']
    }


def insert_transactions_to_db(data):
    transactions_collection = db['transactions_'+ADDRESS]
    transactions_collection.create_index('hash')

    requests = []
    for item in data:
        request = UpdateOne(
            {'hash': item['hash']},
            {'$set': item},
            upsert=True
        )
        requests.append(request)

    requests_chunks = [requests[i:i+CHUNK_SIZE]
                       for i in range(0, len(requests), CHUNK_SIZE)]
    result_list = []
    sys.stdout.write('writing chunk')
    for chunk in requests_chunks:
        sys.stdout.write('.')
        result = transactions_collection.bulk_write(chunk)
        result_list.append(result)
    sys.stdout.write('\n')
    result = reduce(collect_insert_results, result_list, {
        'upserted': 0,
        'modified': 0
    })
    return result


sys.stdout.write('started fetch service\n')

buffer = ''
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
    sys.stderr.write('received server status ' + res.status + '\n')
    exit(1)

sys.stdout.write('fetching data for address ' + ADDRESS + '\n')

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
insert_objs = map(build_object, transactions)
sys.stdout.write('processing ' + str(len(transactions)) + ' entries\n')
result = insert_transactions_to_db(insert_objs)
sys.stdout.write('processing finished\n')
sys.stdout.write('rows inserted: ' + str(result['nUpserted']) + '\n')
sys.stdout.write('rows updated: ' + str(result['nModified']) + '\n')
if True:  # if result['nUpserted'] > 0 or result['nModified'] > 0:
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
