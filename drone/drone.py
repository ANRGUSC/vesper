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

        self.handlers[Message.TYPE_PARAMS] = self.handle_params

        self.client = Client(self, cfg.SERVER_HOST, cfg.SERVER_PORT)
        self.protocol = None

        self.frame_rate = 1.0
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
        if (self.camera is None) and (not self.camera_factory is None):
            self.camera = self.camera_factory(self.send_image)
            self.camera.frame_rate = self.frame_rate
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
        return

    def disconnected(self, protocol):
        """Handles disconnection."""
        Service.disconnected(self, protocol)
        self.protocol = None
        self.stop_camera()
        return

    def send_image(self, image_data):
        """Sends JPEG-encoded images."""
        msg = Message(self.name, Message.TYPE_IMAGE, image_data)
        self.send(msg)
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

        if param[0] == 'frame_rate':
            self.frame_rate = param[1]

            if not self.camera is None:
                self.camera.frame_rate = self.frame_rate

        if param[0] == 'camera':
            if param[1]:
                self.start_camera()

            else:
                self.stop_camera()


        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = '/dev/null'

    logging.config.dictConfig(mylogcfg)

    Drone().start()
