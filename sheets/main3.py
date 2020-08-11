import http.client
import json
import sys
import os

GOOGLE_API_KEY = 'AIzaSyA9NvIvy86s0TtqEf3CBX4MVPdJPTJdkgY'
SERVER = 'sheets.googleapis.com'
PATH = '/v4/spreadsheets?key='+GOOGLE_API_KEY


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

data = json.dumps(build_sheet('test', [[1, '2', False]]))
conn = http.client.HTTPSConnection(SERVER)
print(PATH)
conn.request('POST', PATH, data, {})
res = conn.getresponse()
response = res.read()
print(response)
