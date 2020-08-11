import http.client
import json
import sys
import os

GOOGLE_API_KEY = 'AIzaSyA9NvIvy86s0TtqEf3CBX4MVPdJPTJdkgY'
test = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
SERVER = 'www.googleapis.com'
PATH = '/upload/drive/v3/files?uploadType=multipart'
BOUNDARY = 'drive-flanks-csv-boundary'
CHUNK_SIZE = 64  # str
ENCODING = 'utf-8'


def build_request(name, data):
    buffer = ''
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    buffer += '--'+BOUNDARY+'\n'
    buffer += 'Content-Type: application/json; charset=UTF-8\n'
    buffer += 'Content-Disposition: form-data; name="metadata"\n'
    buffer += '\n'
    buffer += json.dumps(metadata) + '\n'

    data_chunks = [data[i:i+CHUNK_SIZE]
                   for i in range(0, len(data), CHUNK_SIZE)]
    for chunk in data_chunks:
        buffer += '--'+BOUNDARY+'\n'
        buffer += 'Content-Type: text/plain; charset=UTF-8\n'
        buffer += 'Content-Disposition: form-data; name="file"\n'
        buffer += '\n'
        buffer += chunk + '\n'

    buffer += '--'+BOUNDARY+'--\n'
    return len(buffer.encode(ENCODING)), buffer


(size, data) = build_request('test', test)
headers = {
    'Content-type': 'multipart/related; boundary=' + BOUNDARY,
    'Content-Length': size
}
print(data)
print(json.dumps(headers))

conn = http.client.HTTPSConnection(SERVER)
conn.request('POST', PATH+'&'+GOOGLE_API_KEY, data, headers)
res = conn.getresponse()

#if res.status != 200:
#    sys.stderr.write('received server status ' + res.status + '\n')
#    exit(1)

response = res.read()
print(response)
