import sys
sys.path.append('../')

from common import MyObject


class Node(MyObject):

    def __init__(self, name):
        self.name = name
        return

    def __repr__(self):
        return "<Device '%s'>" % (self.name)
