import os
import sys
from quart import Quart, request
import db
import auth
import validator

PORT = os.environ['PORT']
app = Quart(__name__)
ENCODING = 'utf-8'


class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if 'path' not in scope or scope['path'] == '/auth':
            return await self.app(scope, receive, send)
        if 'headers' in scope:
            for header, value in scope['headers']:
                header = header.decode(ENCODING)
                if header == 'authorization':
                    value = value.decode(ENCODING).split()
                    if len(value) != 2 or value[0] != 'Bearer':
                        return await self.sendMiddlewareError(
                            'invalid authorization header', 400, send)
                    try:
                        auth.renew_token(value[1])
                        return await self.app(scope, receive, send)
                    except Exception as e:
                        print(e)
                        return await self.sendMiddlewareError(
                            'invalid token', 400, send)
        return await self.sendMiddlewareError(
            'missing authorization header', 400, send)

    async def sendMiddlewareError(self, error, code, send):
        body = str('{"error":"'+error+'"}').encode(ENCODING)
        content_lenght = str(len(body)).encode(ENCODING)
        await send({
            'type': 'http.response.start',
            'status': code,
            'headers': [(b'content-length', content_lenght)],
        })
        await send({
            'type': 'http.response.body',
            'body': body,
            'more_body': False,
        })


app.asgi_app = AuthMiddleware(app.asgi_app)


def get_token(input_request):
   token = input_request.headers['Authorization'].split()[1]
   return token

@app.route('/auth', methods=['POST'])
async def login():
    received_params = await request.get_json()
    if received_params is None or 'username' not in received_params or 'password' not in received_params:
        return {'error': 'invalid login'}, 400
    try:
        token = auth.login(
            received_params['username'], received_params['password'])
        return {'token': token}, 200
    except Exception as e:
        print(e)
        return {'error': 'invalid login'}, 400


@app.route('/renew', methods=['POST'])
async def renew():
    token = get_token(request)
    return {'token': auth.renew_token(token)}, 200


@app.route('/address/<address>/transaction', defaults={'transaction': None}, methods=['POST'])
@app.route('/address/<address>/transaction/<transaction>', methods=['POST'])
async def get_transaction(address, transaction):
    token = get_token(request)
    try:
        auth.check_permissions(token, address)
    except:
        return {'error': 'user is not authorized for this address'}, 403

    received_params = await request.get_json()
    if received_params is None:
        return {'error': 'invalid request'}, 400

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

sys.stdout.write('started api service\n')
app.run(host="localhost", port=PORT, debug=True)
