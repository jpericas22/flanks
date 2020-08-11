import sys
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleHttpError
from datetime import datetime
import json
import db

# SHEET_URL = https://docs.google.com/spreadsheets/d/1I6kQHV-UVrseq1FMK66hB_pRrph0p-P0i1oPTmGwrlM/edit
ADDRESS = os.environ['ADDRESS']
SHEET_ID = os.environ['SHEET_ID']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = './credentials.json'
DEFAULT_FORMAT = '%d/%m/%Y %H:%M:%S'


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)


def build_sheet(title, data):
    rows = []
    for row in data:
        current_row = []
        for col in row:
            if type(col) == int or type(col) == float:
                current_row.append({
                    'userEnteredValue': {
                        'numberValue': col
                    }
                })
            elif type(col) == bool:
                current_row.append({
                    'userEnteredValue': {
                        'boolValue': col
                    }
                })
            else:
                current_row.append({
                    'userEnteredValue': {
                        'stringValue': str(col)
                    }
                })
        rows.append({
            'values': current_row
        })
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
                        "rowData": rows,
                    }
                ],
            }
        ]
    }
    return sheet_obj


def build_update(data, sheet_range):
    update_obj = {
        "range": sheet_range,
        "majorDimension": "ROWS",
        "values": data
    }
    return update_obj


def update_sheet(address, id, data):
    try:
        row_length = len(data[0])
        sheet_range = 'A:'+chr(ord('A')+row_length)
        sheet = sheets_service.spreadsheets()
        update = build_update(data, sheet_range)
        sheet.values().update(spreadsheetId=id,
                              range=sheet_range, valueInputOption='USER_ENTERED', includeValuesInResponse=False, body=update).execute()
        return id, data
    except GoogleHttpError as e:
        if e.resp.status == 404:
            init_sheet = build_sheet(address, data)
            sheets_res = sheet.create(body=init_sheet).execute()
            print(sheets_res)
            id = sheets_res['spreadsheetId']
            permissions = drive_service.permissions()
            permissions_obj = {
                'type': 'anyone',
                'role': 'writer'
            }
            permissions.create(
                fileId=id, body=permissions_obj).execute()
            return id, []
        print(e)
        exit(1)


def json_date_handler(o):
    if isinstance(o, datetime):
        return o.strftime(DEFAULT_FORMAT)


sys.stdout.write('starting sheet update')
transactions = db.get_transactions(ADDRESS)
rows = [[]]
for key in transactions[0]:
    rows[0].append(key)
for transaction in transactions:
    cols = []
    for _, value in transaction.items():
        if type(value) == datetime:
            value = value.strftime(DEFAULT_FORMAT)
        if type(value) == dict or type(value) == list:
            value = json.dumps(value, default=json_date_handler)
        if value is None:
            value = ''
        cols.append(value)
    rows.append(cols)
sys.stdout.write('sheet update finished')


update_sheet(ADDRESS, SHEET_ID, rows)
