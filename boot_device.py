#!/usr/bin/env python

import copy
import logging.config

import config as cfg

from device import Device

if __name__ == '__main__':
    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = 'DEBUG'
    mylogcfg['handlers']['file']['filename'] = 'drone_output.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_device')

    name = 'device'
    device = Device(name)

    log.info('booting device %s...', name)
    device.start()
