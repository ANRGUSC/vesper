import cv2

import sys
sys.path.append('../')

import config as cfg

from car import Dashboard
from common import Message
from common import Service
from network import Server

class Dispatcher(Service):
    """Handles communication from drone and devices."""

    def __init__(self, controller=None):
        Service.__init__(self, 'dispatcher')

        self.handlers[Message.TYPE_LOGIN] = self.handle_login
        self.handlers[Message.TYPE_IMAGE] = self.handle_image

        self.server = Server(self, cfg.SERVER_PORT)
        self.protocols = {}

        self.dashboard = Dashboard()
        self.dashboard.start()

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

        if not self.dashboard is None:
            image = cv2.imdecode(msg.data, cv2.IMREAD_UNCHANGED)
            self.dashboard.put_image(image)

        #controller
        return

    def start(self):
        """Starts the dispatcher server."""
        self.log().info('starting dispatcher')
        self.start_controller()
        self.server.run()   # Blocking call
        return

    def stop(self):
        """Stops the dispatcher server."""
        self.log().info('stopping dispatcher')
        self.dashboard.stop()
        self.stop_controller()
        self.server.stop()
        return

    def start_controller(self):
        """Starts the controller."""
        if self.controller:
            self.controller.start()

        return

    def stop_controller(self):
        """Stops the controller."""
        if self.controller:
            self.controller.stop()

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
