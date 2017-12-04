import sys
sys.path.append('../')

import config as cfg

from common import AvgItem
from common import Controller
from common import bounded
from dispatcher import Dispatcher


class VesperController(Controller):

    EWMA_ALPHA   = 0.8

    VAL_AVG_FPS = 'FPS.avg'
    VAL_FRAME_RATE = 'Frame Rate'
    VAL_T_0 = 'T_o'
    VAL_M_0 = 'M_o'

    DRONE_NAME = 'drone'

    def __init__(self):
        Controller.__init__(self)

        self.avg_fps = AvgItem(self.EWMA_ALPHA)

        self.metrics = {}

        self.values = {}
        self.values[self.VAL_T_0] = cfg.T_o
        self.values[self.VAL_M_0] = cfg.M_o
        self.values[self.VAL_AVG_FPS] = 0.0

        self.connected = set()

        return

    def start(self):
        """Starts controller thread."""
        Controller.start(self)
        return

    def loop(self):
        """Controller action loop."""
        self.log().info('controller loop')

        if self.DRONE_NAME in self.connected:
            # Adjust frame rate
            avg_fps = self.values[self.VAL_AVG_FPS]
            t0 = self.values[self.VAL_T_0]
            ratio = float(t0)/avg_fps

            rate = bounded(t0*ratio, 0.8 * t0, 1.2 * t0)
            self.set_frame_rate(t0 * ratio)

        return

    def logon(self, name):
        """Handles device logon."""
        Controller.logon(self, name)
        self.connected.add(name)

        if name == self.DRONE_NAME:
            self.set_frame_rate(self.values[self.VAL_T_0])

        return

    def logoff(self, name):
        """Handles device logoff."""
        Controller.logoff(self, name)
        self.connected.discard(name)
        return

    def put_metrics(self, metrics):
        """Process system metrics."""
        self.metrics = metrics

        if Dispatcher.ITEM_FPS in metrics:
            fps = metrics[Dispatcher.ITEM_FPS]
            self.avg_fps.add(fps)
            self.values[self.VAL_AVG_FPS] = self.avg_fps.pull()

        self.log().debug('values: %s', self.values)
        return

    def get_values(self):
        """Retrieves controller's data."""
        return self.values

    def set_frame_rate(self, rate):
        """Sets frame rate."""
        params = [
            ('frame_rate', rate),
            ('camera', True)
        ]
        self.send_params(self.DRONE_NAME, params)

        self.values[self.VAL_FRAME_RATE] = rate
        return
