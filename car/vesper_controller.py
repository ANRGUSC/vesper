import sys
sys.path.append('../')

import config as cfg

from common import Controller
from common import AvgItem
from dispatcher import Dispatcher


class VesperController(Controller):

    EWMA_ALPHA   = 0.8

    VAL_AVG_FPS = 'FPS.avg'

    def __init__(self):
        Controller.__init__(self)

        self.avg_fps = AvgItem(self.EWMA_ALPHA)

        self.metrics = {}

        self.values = {}
        self.values['T_o'] = cfg.T_o
        self.values['M_o'] = cfg.M_o
        self.values[self.VAL_AVG_FPS] = 0.0

        return

    def logon(self, name):
        """Handles device logon."""
        Controller.logon(self, name)

        if name == 'drone':
            params = [
                ('frame_rate', 1.0),
                ('camera', True)
            ]
            self.send_params(name, params)

        return

    def start(self):
        """Starts controller thread."""
        Controller.start(self)
        return

    def put_metrics(self, metrics):
        """Process system metrics."""
        self.metrics = metrics

        if Dispatcher.ITEM_FPS in metrics:
            fps = metrics[Dispatcher.ITEM_FPS]
            self.avg_fps.add(fps)
            self.values[self.VAL_AVG_FPS] = self.avg_fps.pull()

        return

    def get_values(self):
        """Retrieves controller's data."""
        return self.values
