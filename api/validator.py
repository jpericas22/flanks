from datetime import datetime

def date_middleware(input):
    DEFAULT_FORMAT = '%Y-%m-%d %H:%M'
    return datetime.strptime(input, DEFAULT_FORMAT)

WHITELIST = {
    'page': {
        'type': int,
    },
    'from': {
        'type': str
    },
    'to': {
        'type': str
    },
    'date_from': {
        'type': str,
        'middleware': date_middleware
    },
    'date_to': {
        'type': str,
        'middleware': date_middleware
    }
}
