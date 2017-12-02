import sys
sys.path.append('../')

import config as cfg

from network import Client
from common import Message
from common import Service


class Drone(Service):
    """Handles communication between the drone and the dispatcher."""

    def __init__(self, camera_factory=None):
        Service.__init__(self, 'drone')

        self.camera_factory = camera_factory
        self.camera = None

        self.client = Client(self, cfg.SERVER_HOST, cfg.SERVER_PORT)
        self.protocol = None
        return

    def start(self):
        """Starts the drone client."""
        self.client.run()
        return

    def stop(self):
        """Stops the drone client."""
        self.client.stop()
        return

    def start_camera(self):
        """Start capturing images."""
        if self.camera_factory:
            self.camera = self.camera_factory()
            self.camera.callback = self.send_image
            self.camera.start()

        return

    def stop_camera(self):
        """Stop capturing images."""
        if self.camera:
            self.camera.stop()
            self.camera = None

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
        #self.start_camera()
        return

    def disconnected(self, protocol):
        """Handles disconnection."""
        Service.disconnected(self, protocol)
        self.protocol = None
        self.stop_camera()
        return

    def send_image(self, image_data):
        """Sends JPEG-encoded images."""
        #self.log().debug('sending image')
        msg = Message(self.name, Message.TYPE_IMAGE, image_data)
        self.send(msg)
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'dispatcher_output.log'

    logging.config.dictConfig(mylogcfg)

    Drone().start()
