import sys
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleHttpError

ADDRESS = os.environ['ADDRESS']
SHEET_ID = os.environ['SHEET_ID']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = './credentials.json'

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


def build_update(data):
    update_obj = {
        "range": "A:B",
        "majorDimension": "ROWS",
        "values": data
    }
    return update_obj


def update_sheet(address, id, data):
    try:
        sheet = sheets_service.spreadsheets()
        update = build_update(data)
        result = sheet.values().update(spreadsheetId=id,
                                       range='A:B', includeValuesInResponse=True, body=update).execute()
        return id, result.get('values', [])
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
            drive_res = permissions.create(
                fileId=id, body=permissions_obj).execute()
            return id, []


get_sheet(ADDRESS, 123)
