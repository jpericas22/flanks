import os
from quart import Quart, websocket

PORT = os.environ['PORT']
app = Quart(__name__)

@app.route('/')
async def hello():
    return 'hello'

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('hello')

app.run(host="0.0.0.0", port=PORT, debug=True)