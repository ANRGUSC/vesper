#!/usr/bin/env python

import copy
import logging.config

import config as cfg

from drone import Camera
from drone import Drone

if __name__ == '__main__':
    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = 'INFO'
    mylogcfg['handlers']['file']['filename'] = 'drone_output.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_drone')

    drone = Drone(Camera)

    log.info('booting drone...')
    drone.start()
