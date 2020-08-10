import os
from quart import Quart, websocket

PORT = os.environ['PORT']
app = Quart(__name__)


@app.route('/address/<address>/transaction', defaults={'transaction': None})
@app.route('/address/<address>/transaction/<transaction>')
async def get_transaction(address, transaction):
    return 'address' + ' - ' + transaction

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('hello')

app.run(host="0.0.0.0", port=PORT, debug=True)
