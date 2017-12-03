import cv2

import sys
sys.path.append('../')

import config as cfg

from car import Dashboard
from common import Message
from common import Monitor
from common import Service
from network import Server

class Dispatcher(Service):
    """Handles communication from drone and devices."""

    ITEM_FPS = 'FPS'

    def __init__(self, controller=None):
        Service.__init__(self, 'dispatcher')

        self.handlers[Message.TYPE_LOGIN] = self.handle_login
        self.handlers[Message.TYPE_IMAGE] = self.handle_image

        self.server = Server(self, cfg.SERVER_PORT)
        self.protocols = {}

        if True:
            self.dashboard = Dashboard()
            self.dashboard.start()

        else:
            self.dashboard = None

        self.monitor = Monitor(self.process_measurements, cfg.MEASURE_PERIOD)
        self.monitor.register_item(self.ITEM_FPS, Monitor.ITEM_RATE)

        self.controller = controller
        self.controller.dashboard = self.dashboard
        self.controller.dispatcher = self
        return

    def handle_login(self, protocol, msg):
        """Handles device logins."""
        name = msg.name
        self.log().info("'%s' login", name)

        protocol.name = name
        self.protocols[name] = protocol

        if not self.controller is None:
            self.controller.logon(name)

        return

    def handle_image(self, protocol, msg):
        """Handles images."""

        if self.monitor:
            self.monitor.update_item(self.ITEM_FPS, 1)

        if self.dashboard:
            image = cv2.imdecode(msg.data, cv2.IMREAD_UNCHANGED)
            self.dashboard.put_image(image)

        #controller
        return

    def process_measurements(self, values):
        """Handles measurements from a Monitor."""
        self.log().debug('measurements: %s', values)

        if self.dashboard:
            self.dashboard.put_values(values)

        return

    def start(self):
        """Starts the dispatcher server."""
        self.log().info('starting dispatcher')

        if self.monitor:
            self.monitor.start()

        if self.controller:
            self.controller.start()

        self.server.run()   # Blocking call
        return

    def stop(self):
        """Stops the dispatcher server."""
        self.log().info('stopping dispatcher')

        if self.monitor:
            self.monitor.stop()

        if self.dashboard:
            self.dashboard.stop()

        if self.controller:
            self.controller.stop()

        self.server.stop()
        return

    def disconnected(self, protocol):
        """Handles device disconnections."""
        name = protocol.name
        del self.protocols[name]
        self.log().info("'%s' disconnected", name)

        if not self.controller is None:
            self.controller.logoff(name)

        return

    def send_params(self, name, params):
        """Sends settings to 'name' client."""

        protocol = self.protocols.get(name)
        if not protocol is None:
            msg = Message(self.name, Message.TYPE_PARAMS, params)
            protocol.send(msg)

        else:
            self.log().warn("protocol '%s' not found", name)

        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Dispatcher().start()
