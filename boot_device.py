#!/usr/bin/env python

import argparse
import copy
import logging.config

import config as cfg

from device import Device

if __name__ == '__main__':
    # Command-line arguments
    parser = argparse.ArgumentParser(description='Device boot script')
    parser.add_argument('name', type=str, help='device name')
    parser.add_argument('-l', '--loglevel', default='INFO',
                        help='log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)')
    args = parser.parse_args()

    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = args.loglevel.upper()
    mylogcfg['handlers']['file']['filename'] = 'device_output.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_device')

    name = args.name
    device = Device(name)

    log.info('booting device %s...', name)
    device.start()
