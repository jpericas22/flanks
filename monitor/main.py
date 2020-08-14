import os
import sys
import asyncio
import websockets
import cotio_commands
from pprint import pprint

HOSTNAME = 'mainnet-fullnode1.coti.io'#os.environ['MONITOR_HOSTNAME']
PATH = '/websocket/140/dv52lpw4/websocket'#os.environ['MONITOR_PATH']
ADDRESS = '51dbd2feecb8c9e3b5c88129da88156d738d00d57bf4524cc780221c4e414ffc9372b00ad7d75679032d928776b044d40d5febb783d8ac9b241b7c0b1cad77de9b699c23'

async def hello():
    uri = "wss://" + HOSTNAME + PATH
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
            try:
                parsed = cotio_commands.parse(message)
                pprint(parsed)
            except:
                if(message == 'h'):
                    print('hearthbeat')
                else:
                    print('unknown response:\n')
                    print(message)
        

asyncio.get_event_loop().run_until_complete(hello())
