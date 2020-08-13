import os
import sys
import secrets
import hashlib
from pymongo import MongoClient
import crypto

ADDRESS = os.environ['ADDRESS']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
USER_PASSWORD = '123456'
ENCODING = 'utf-8'

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def hash_password(password):
    salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', password.encode(ENCODING), salt.encode(ENCODING), 100000).hex(), salt


pubkey = crypto.gen_keys(ADDRESS)
(password_hash, salt) = hash_password(USER_PASSWORD)
default_user = {
    'username': 'client',
    'password': password_hash,
    'salt': salt,
    'addressList': [ADDRESS],
    'publicKey': pubkey
}
users_collection = db['users']
users_collection.create_index('username', unique=True)
users_collection.update_one({'username': default_user['username']}, {
                            '$set': default_user}, upsert=True)
print('DEBUG:inserted default user to db')
