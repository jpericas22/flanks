import os
import sys
import asyncio
import websockets
import cotio_commands
import random
import string
from pprint import pprint
from json import JSONDecodeError

HOSTNAME = os.environ['MONITOR_HOSTNAME']
ADDRESS = os.environ['ADDRESS']

async def monitor():
    random_id = ''.join(random.choice(string.ascii_lowercase + string.digits)
            for _ in range(8))
    uri = "wss://" + HOSTNAME + '/websocket/140/' + random_id + '/websocket'
    async with websockets.connect(uri, ssl=True) as websocket:
        await websocket.recv()
        await websocket.send(cotio_commands.CONNECT)
        message = await websocket.recv()
        sys.stdout.write('connected\n')
        await websocket.send(cotio_commands.subscribe(ADDRESS))
        sys.stdout.write('subscribed\n')     
        while True:   
            message = await websocket.recv()
            sys.stdout.write('received message\n')
            if(message == 'h'):
                print('hearthbeat')
            else:
                try:
                    parsed = cotio_commands.parse(message)
                    pprint(parsed)
                except JSONDecodeError:
                    print('malformed body')
                    print(message)
        
try:
    asyncio.run(monitor())
except KeyboardInterrupt:
    sys.stdout.write('\nexiting\n')
    exit(0)
