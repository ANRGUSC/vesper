import threading

import sys
sys.path.append('../')

import config as cfg

from common import AvgItem
from common import MyObject

class Node(MyObject):

    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()    # access lock

        self.processing_rate = AvgItem(cfg.EWMA_ALPHA)
        self.rtt = AvgItem(cfg.EWMA_ALPHA)
        return

    def __repr__(self):
        return "<Node '%s' P_RATE: %0.6f, RTT: %0.6f'>" % \
                (self.name, self.processing_rate.get(), self.rtt.get())
