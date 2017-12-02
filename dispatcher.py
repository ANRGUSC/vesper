#import sys
#sys.path.append('../')

import config as cfg

from network import Server
from common import Message
from common import Service


class Dispatcher(Service):
    """Handles communication from drone and devices."""

    def __init__(self, controller=None):
        Service.__init__(self, 'dispatcher')
        self.controller = controller

        self.handlers[Message.TYPE_LOGIN] = self.handle_login

        self.server = Server(self, cfg.SERVER_PORT)
        self.protocols = {}
        return

    def handle_login(self, protocol, msg):
        """Handles device logins."""
        name = msg.name
        self.log().info("'%s' logged in", name)

        protocol.name = name
        self.protocols[name] = protocol

        if not controller is None:
            controller.logon(name)

        return

    def start(self):
        """Starts the dispatcher server."""
        self.server.run()   # Blocking call
        return

    def stop(self):
        """Stops the dispatcher server."""
        self.server.stop()
        return

    def disconnected(self, protocol):
        """Handles device disconnections."""
        del self.protocols[protocol.name]
        self.log().info("'%s' disconnected", protocol.name)

        if not controller is None:
            controller.logoff(name)

        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Dispatcher().start()
