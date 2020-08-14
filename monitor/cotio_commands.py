import json
from time import time

CONNECT = r'["CONNECT\naccept-version:1.2\nheart-beat:10000,10000\n\n\u0000"]'


def parse(message):
    message = message.replace(r'a["MESSAGE\n', '').replace(r'\u0000"]','')
    message = message.split('\n\n')
    metadata = message[0].split('\n')
    response = {}
    print(metadata)
    for item in enumerate(metadata):
        item = item.split(':')
        response[item[0]] = item[1]

    response['data'] = json.loads(message[1])
    return response


def subscribe(address):
    # pylint: disable=unused-variable
    timestamp = str(int(time()*1000))
    extra_timestamp = str(int(timestamp[:3]) - 30)
    return r'["SUBSCRIBE\nid:sub-${timestamp}-{extra_timestamp}\ndestination:/topic/addressTransactions/{address}\n\n\u0000"]'
