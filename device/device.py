import sys
sys.path.append('../')

import config as cfg

from network import Client
from common import Message
from common import Service


class Device(Service):
    """Handles communication between a device and the dispatcher."""

    def __init__(self, name):
        Service.__init__(self, name)

        self.handlers[Message.TYPE_PARAMS] = self.handle_params
        self.handlers[Message.TYPE_JOB] = self.handle_job

        self.client = Client(self, cfg.SERVER_HOST, cfg.SERVER_PORT)
        self.protocol = None
        return

    def start(self):
        """Starts the device client."""
        self.client.run()
        return

    def stop(self):
        """Stops the device client."""
        self.client.stop()
        return

    def send(self, message):
        if self.protocol:
            self.protocol.send(message)

        return

    def connected(self, protocol):
        """Handles connection."""
        Service.connected(self, protocol)
        self.protocol = protocol

        self.send(Message(self.name, Message.TYPE_LOGIN))
        return

    def disconnected(self, protocol):
        """Handles disconnection."""
        Service.disconnected(self, protocol)
        self.protocol = None
        return

    def handle_params(self, protocol, message):
        """Handles param messages."""
        self.log().info("received params from '%s': %s", message.name,
                        message.data)

        params = message.data
        for p in params:
            self.configure_param(p)

        return

    def configure_param(self, param):
        """Processes a parameter."""
        self.log().debug(param)
        return

    def handle_job(self, protocol, message):
        """Handles job messages."""
        self.log().info('received job')
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = '/dev/null'

    logging.config.dictConfig(mylogcfg)

    Device('device').start()
