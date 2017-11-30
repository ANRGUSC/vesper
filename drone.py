#import sys
#sys.path.append('../')

import config as cfg

from comms import Client
from message import Message
from service import Service


class Drone(Service):
    """Handles communication between the drone and the dispatcher."""
    #Client(ServiceClient(), cfg.SERVER_HOST, cfg.SERVER_PORT).run()

    def __init__(self):
        Service.__init__(self, 'drone')

        self.client = Client(self, cfg.SERVER_HOST, cfg.SERVER_PORT)
        return

    def start(self):
        """Starts the drone client."""
        self.client.run()
        return

    def stop(self):
        """Stops the drone client."""
        self.client.stop()
        return

    def connected(self, protocol):
        """Handles connection."""
        Service.connected(self, protocol)
        self.protocol = protocol

        self.protocol.send(Message(self.name, Message.TYPE_LOGIN))
        return

    def disconnected(self, protocol):
        """Handles disconnection."""
        Service.disconnected(self, protocol)
        self.protocol = None
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Drone().start()
