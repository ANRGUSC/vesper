#!/usr/bin/env python

import argparse
import copy
import datetime
import logging.config
import sys

import config as cfg

from car import Dispatcher
from car import StaticController
from car import VesperController

if __name__ == '__main__':
    dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Command-line arguments
    parser = argparse.ArgumentParser(description='Car boot script')
    parser.add_argument('controller', nargs='?', default='vesper',
                        help='controller to use for scheduling '
                        '(vesper, static)')
    parser.add_argument('option', nargs='?', default=None,
                        help='controller option (static controller only)')
    parser.add_argument('-l', '--loglevel', default='WARNING',
                        help='log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)')
    args = parser.parse_args()

    # Logging setup
    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['default']['level'] = args.loglevel.upper()
    mylogcfg['handlers']['file']['filename'] = 'car_output.' + dt + '.log'
    logging.config.dictConfig(mylogcfg)

    log = logging.getLogger('boot_car')

    c = args.controller.lower()
    if c == 'vesper':
        controller = VesperController()
        log.info('Controller: %s', 'VESPER')

    elif c == 'static':
        if args.option == None:
            log.error('missing static controller option')
            sys.exit(1)

        option = int(args.option)
        if (option < 0) or (option > len(cfg.PIPELINES)):
            log.error('invalid pipeline %d', option)
            sys.exit(2)

        log.info('Controller: Static(%d)', option)
        controller = StaticController(option)


    log.info('T_o: %0.2f', cfg.T_o)
    log.info('M_o: %0.2f', cfg.M_o)
    log.info('CONTROLLER_LOOP_TIME: %d', cfg.CONTROLLER_LOOP_TIME)


    dispatcher = Dispatcher(controller)

    log.info('booting car...')
    dispatcher.start()
    dispatcher.stop()
