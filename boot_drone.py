#!/usr/bin/env python

import argparse
import copy
import logging.config

import config as cfg

from drone import Camera
from drone import Drone

if __name__ == '__main__':
    # Command-line arguments
    parser = argparse.ArgumentParser(description='Drone boot script')
    parser.add_argument('-l', '--loglevel', default='INFO',
                        help='log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)')
    args = parser.parse_args()

    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = args.loglevel.upper()
    mylogcfg['handlers']['file']['filename'] = 'drone_output.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_drone')

    drone = Drone(Camera)

    log.info('booting drone...')
    drone.start()
