# Server Parameters
SERVER_HOST = 'localhost'
SERVER_PORT = 12345

MAX_DATA_SIZE = 1e6

# Camera settings
IMAGE_COMPRESSION = 50

# Logging
LOGCFG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(relativeCreated)-14s|%(levelname)-8s|%(name)s|%(threadName)s|%(message)s',
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'output.log',
            'mode': 'w'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
