from datetime import datetime

def baseTransactions_middleware(data):
    for item in data:
        if 'amount' in item and item['amount'] is not None:
            item['amount'] = float(item['amount'])
        if 'createTime' in item and item['createTime'] is not None:
            item['createTime'] = datetime.fromtimestamp(item['createTime'])
        if 'originalAmount' in item and item['originalAmount'] is not None:
            item['originalAmount'] = float(item['originalAmount'])
    return data

WHITELIST = {
    'hash': {
        'type': str,
        'required': True
    },
    'amount': {
        'middleware': float,
        'required': True
    },
    'type': {
        'type': str,
        'required': True
    },
    'baseTransactions': {
        'type': list,
        'middleware': baseTransactions_middleware
    },
    'leftParentHash': {
        'type': str,
        'encrypt': True
    },
    'rightParentHash': {
        'type': str
    },
    'trustChainConsensus': {
        'type': bool
    },
    'trustChainTrustScore': {
        'type': float
    },
    'transactionConsensusUpdateTime': {
        'type': float,
        'middleware': datetime.fromtimestamp
    },
    'createTime': {
        'type': float,
        'middleware': datetime.fromtimestamp
    },
    'attachmentTime': {
        'type': float,
        'middleware': datetime.fromtimestamp
    },
    'senderTrustScore': {
        'type': float,
    },
    'childrenTransactionHashes': {
        'type': list
    },
    'isValid': {},
    'transactionDescription': {
        'type': str
    }
}
