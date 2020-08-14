import json
from time import time

ENCODING = 'unicode_escape'
CONNECT = r'["CONNECT\naccept-version:1.2\nheart-beat:10000,10000\n\n\u0000"]'


def parse(message):
    message = message.replace(r'a["MESSAGE\n', '').replace(r'\u0000"]', '')
    message = message.split(r'\n\n')
    metadata = message[0].split(r'\n')
    response = {}
    for item in metadata:
        item = item.split(':')
        response[item[0]] = item[1]

    print(message[1].encode().decode(ENCODING))
    response['data'] = json.loads(message[1].encode().decode(ENCODING))
    return response


def subscribe(address):
    # pylint: disable=unused-variable
    timestamp = str(int(time()*1000))
    timestamp_extra = str(int(timestamp[:3]) - 30)
    return r'["SUBSCRIBE\nid:sub-' + timestamp + r'-' + timestamp_extra + r'\ndestination:/topic/addressTransactions/{address}\n\n\u0000"]'
