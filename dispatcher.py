#import sys
#sys.path.append('../')

import config as cfg

from comms import Server
from message import Message
from service import Service


class Dispatcher(Service):
    """Handles communication from drone and devices."""

    def __init__(self):
        Service.__init__(self, 'dispatcher')

        self.handlers[Message.TYPE_LOGIN] = self.handle_login

        self.server = Server(self, cfg.SERVER_PORT)
        return

    def handle_login(self, protocol, msg):
        """Handles device logins."""
        name = msg.name
        self.log().info("'%s' logged in", name)
        return

    def start(self):
        """Starts the dispatcher server."""
        self.server.run()   # Blocking call
        return

    def stop(self):
        """Stops the dispatcher server."""
        self.server.stop()
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Dispatcher().start()
