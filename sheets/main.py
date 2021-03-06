import db
import json
from datetime import datetime
from googleapiclient.errors import HttpError as GoogleHttpError
from googleapiclient.discovery import build
from google.oauth2 import service_account
from time import sleep
import pika
import os
import sys
import functools
import threading


SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = './credentials.json'
DEFAULT_FORMAT = '%d/%m/%Y %H:%M:%S'
CHUNK_SIZE = 2000
CHUNK_LIMIT = 10

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)


def build_sheet(title):
    sheet_obj = {
        "properties": {
            "title": title,
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 0,
                    "title": 'main',
                    "index": 0,
                },
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [[]],
                    }
                ],
            }
        ]
    }
    return sheet_obj


def build_append(data):
    row_length = len(data[0])
    sheet_col_end = chr(ord('A')+row_length)
    append_data = []

    data_chunks = [data[i:i+CHUNK_SIZE]
                   for i in range(0, len(data), CHUNK_SIZE)]
    for i, chunk in enumerate(data_chunks[-CHUNK_LIMIT:]):
        value_obj = {
            "range": 'A'+str(i*CHUNK_SIZE+1)+':'+sheet_col_end+str((i+1)*CHUNK_SIZE+1),
            "majorDimension": "ROWS",
            "values": chunk
        }
        append_data.append(value_obj)

    return append_data


def execute_append(sheet, id, data):
    append = build_append(data)
    sys.stdout.write('writing chunks\n')
    for i, query in enumerate(append):
        sys.stdout.write(str(i+1)+'/'+str(len(append))+'\n')
        sleep(2)
        sheet.values().append(spreadsheetId=id,
                              range=query['range'], valueInputOption='USER_ENTERED', includeValuesInResponse=False, insertDataOption='OVERWRITE', body=query).execute()


def update_sheet(address, id, data):
    # pylint: disable=maybe-no-member
    sheet = sheets_service.spreadsheets()
    try:
        sheet.values().clear(spreadsheetId=id, range='A1:Z').execute()
        execute_append(sheet, id, data)
        return id
    except GoogleHttpError as e:
        if e.resp.status == 404:
            init_sheet = build_sheet(address)
            sheets_res = sheet.create(body=init_sheet).execute()
            id = sheets_res['spreadsheetId']
            sys.stdout.write('ID: '+ id + '\n')
            permissions = drive_service.permissions()
            permissions_obj = {
                'type': 'anyone',
                'role': 'reader'
            }
            permissions.create(
                fileId=id, body=permissions_obj).execute()
            execute_append(sheet, id, data)
            return id
        print(e)
        exit(1)


def json_date_handler(o):
    if isinstance(o, datetime):
        return o.strftime(DEFAULT_FORMAT)


def update_routine(address, sheet_id, connection, ch, method):
    sys.stdout.write('starting sheet update\n')
    transactions = db.get_transactions(address)
    rows = [[]]
    if len(transactions) == 0:
        sys.stdout.write('no transacctions for address ' + 'ADDRESS' + '\n')
        exit(0)
    for key in transactions[0]:
        rows[0].append(key)
    for transaction in transactions:
        cols = []
        for _, value in transaction.items():
            if type(value) == datetime:
                value = value.strftime(DEFAULT_FORMAT)
            if type(value) == dict or type(value) == list:
                value = json.dumps(value, default=json_date_handler)
                if len(value) > 50000:
                    message = ' - VALUE TRUNCATED'
                    value = value[0:(50000-len(message))]
            if value is None:
                value = ''
            cols.append(value)
        rows.append(cols)
    update_sheet(address, sheet_id, rows)
    sys.stdout.write('updated address '+address+'\n')
    connection.add_callback_threadsafe(functools.partial(
        ch.basic_ack, delivery_tag=method.delivery_tag))


def process_message(ch, method, properties, body, args):
    (connection, threads) = args
    sys.stdout.write('received message\n')
    try:
        message = json.loads(body)
    except:
        sys.stderr.write('malformed message\n')
        sys.stderr.write('message:\n')
        sys.stderr.write(repr(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if 'action' not in message:
        print(repr(message)+'')
    elif message['action'] == 'update':
        address = message['address']
        sheet_id = message['sheet_id']
        t = threading.Thread(target=update_routine, args=(
            address, sheet_id, connection, ch, method))
        t.start()
        threads.append(t)
    else:
        sys.stdout.write('unrecognized action "' + message['action'] + '"\n')


threads = []
sys.stdout.write('started sheets service\n')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='queue'))
channel = connection.channel()
channel.queue_declare(queue='sheets')
channel.basic_qos(prefetch_count=1)
process_message_callback = functools.partial(
    process_message, args=(connection, threads))
channel.basic_consume(
    queue='sheets', on_message_callback=process_message_callback)
channel.start_consuming()
