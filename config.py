"""System configuration."""

# Constraints
T_o = 1.0     # Throughput (FPS)
M_o = 1.0     # Makespan (s)

# Server Parameters
SERVER_HOST = 'localhost'
SERVER_PORT = 12345

MAX_DATA_SIZE = 1e6
TIMEOUT = 1     # Seconds

CONTROLLER_LOOP_TIME = 6
MEASURES_PER_LOOP    = 3

EWMA_ALPHA = 0.8

DASHBOARD = True

# Camera settings
CAMERA_NAME = 'drone'
IMAGE_COMPRESSION = 50

# Dashboard settings
DASH_IMAGE_WIDTH  = 640
DASH_IMAGE_HEIGHT = 480
DASH_REFRESH_RATE = 10

# Device settings
PIPELINES = [
    ('ssd_mobilenet_v1_coco_2017_11_17', 0.303, 0.21),
    ('ssd_inception_v2_coco_2017_11_17', 0.409, 0.24)
]

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
