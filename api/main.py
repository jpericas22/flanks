import os
from quart import Quart, request
import db
import validator

PORT = os.environ['PORT']
app = Quart(__name__)


@app.route('/address/<address>/transaction', defaults={'transaction': None}, methods=['POST'])
@app.route('/address/<address>/transaction/<transaction>', methods=['POST'])
async def get_transaction(address, transaction):
    received_params = await request.get_json()
    params = {}

    for key in validator.WHITELIST:
        key_settings = validator.WHITELIST[key]
        if key in received_params and received_params[key] is not None:
            if 'type' in key_settings and type(received_params[key]) != key_settings['type']:
                res = {
                    'error': 'invalid type for parameter "' + key + '"'
                }
                return res, 400
            if 'middleware' in key_settings:
                try:
                    received_params[key] = key_settings['middleware'](
                        received_params[key])
                except Exception as e:
                    print(repr(e))
                    res = {
                        'error': 'error processing parameter "' + key + '"'
                    }
                    return res, 500
            params[key] = received_params[key]

    if transaction is not None:
        params['transaction'] = transaction

    result = db.get_transactions(address, params)
    return result, 200

app.run(host="0.0.0.0", port=PORT, debug=True)
