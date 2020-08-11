import os
import sys
import jwt
import hashlib
import time
from bson.objectid import ObjectId
from pymongo import MongoClient

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
JWT_SECRET = os.environ['JWT_SECRET']
ENCODING = 'utf-8'
EXPIRE_TIME = 322 #5min

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]

def build_token(id):
    jwt_data = {
        'id': id,
        'expires': int(time.time()) + EXPIRE_TIME
    }
    jwt_token = jwt.encode(jwt_data,
                           JWT_SECRET, algorithm='HS256')
    return jwt_token.decode(ENCODING)

def login(username, password):
    users_collection = db['users']
    user_data = users_collection.find_one({'username': username})
    hashed_password_db = user_data['password']
    hashed_password_input = hashlib.pbkdf2_hmac(
        'sha256', password.encode(ENCODING), user_data['salt'].encode(ENCODING), 100000).hex()
    if hashed_password_db == hashed_password_input:
        return build_token(str(user_data['_id']))
    else:
        raise Exception()

def renew_token(token):
    token_data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    expires = int(token_data['expires'])
    if(expires < int(time.time())):
        raise Exception()
    return build_token(token_data['id'])

def check_permissions(token, address):
    token_data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    users_collection = db['users']
    user_data = users_collection.find_one({'_id': ObjectId(token_data['id'])})
    if user_data is None or address not in user_data['addressList']:
        raise Exception()
