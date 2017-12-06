import sys
sys.path.append('../')

import config as cfg

from common import AvgItem
from common import MyObject

class Node(MyObject):

    def __init__(self, name):
        self.name = name

        self.processing_rate = AvgItem(cfg.EWMA_ALPHA)
        self.rtt = AvgItem(cfg.EWMA_ALPHA)
        return

    def __repr__(self):
        return "<Device '%s'>" % (self.name)
