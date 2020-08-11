import os
from pymongo import MongoClient
import rsa

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
KEY_BYTES = 512
CHUNK_SIZE = 53

mongo_client = MongoClient(
    'mongodb://'+DB_USER+':'+DB_PASSWORD+'@database:27017')
db = mongo_client[DB_NAME]


def get_public_key(address):
    user_collection = db['users']
    user_data = user_collection.find_one({'addressList': address})
    return user_data['publicKey']


def encrypt(data, address):
    key_hex = get_public_key(address)
    key = rsa.PublicKey.load_pkcs1(bytes.fromhex(key_hex), format='DER')
    data_bytes = data.encode('utf-8')
    data_chunks = [data_bytes[i:i+53]
                   for i in range(0, len(data_bytes), CHUNK_SIZE)]
    encrypted_chunks = []
    for chunk in data_chunks:
        encrypted_chunks.append(rsa.encrypt(chunk, key).hex())
    return encrypted_chunks


def gen_keys():
    (pubkey, privkey) = rsa.newkeys(KEY_BYTES)
    file = open('./keys/priv.pem', 'w')
    file.write(privkey.save_pkcs1().decode('utf-8'))
    file.close()
    return pubkey.save_pkcs1(format='DER').hex()
