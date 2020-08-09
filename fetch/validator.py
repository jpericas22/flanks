from datetime import datetime

def parseTime(timestamp):
    return datetime.fromtimestamp(timestamp)

WHITELIST = {
    'hash': {
        'type': str,
        'required': True
    },
    'amount': {
        'type': float,
        'required': True
    },
    'type': {
        'type': str,
        'required': True
    },
    'baseTransactions': {
        'type': list
    },
    'leftParentHash': {
        'type': str
    },
    'leftParentHash': {
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
        'middleware': parseTime
    },
    'createTime': {
        'type': float,
        'middleware': parseTime
    },
    'attachmentTime': {
        'type': float,
        'middleware': parseTime
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
