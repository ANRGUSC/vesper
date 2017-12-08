#!/usr/bin/env python

import copy
import logging.config

import config as cfg

from car import Dispatcher
from car import VesperController

if __name__ == '__main__':
    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = 'DEBUG'
    mylogcfg['handlers']['file']['filename'] = 'car_output.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_car')

    log.info('T_o: %0.2f', cfg.T_o)
    log.info('M_o: %0.2f', cfg.M_o)

    controller = VesperController()
    log.info('Controller: %s', 'VESPER')

    dispatcher = Dispatcher(controller)

    log.info('booting car...')
    dispatcher.start()
    dispatcher.stop()
