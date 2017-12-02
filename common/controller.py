import threading

import sys
sys.path.append('../')

from myobject import MyObject


class Controller(MyObject, threading.Thread):
    """Controller base class."""

    def __init__(self, name='Controller'):
        threading.Thread.__init__(self, name=name)
        return

    def start(self):
        """Starts controller thread."""
        self.log().info('starting controller')
        threading.Thread.start(self)
        return

    def stop(self):
        """Stops controller thread."""
        self.log().info('stopping controller')
        return

    def run(self):
        self.log().info('running controller')
        #raise NotImplementedError
        return

    def logon(self, name):
        self.log().info("'%s' logged on", name)
        return

    def logoff(self, name):
        self.log().info("'%s' logged off", name)
        return
