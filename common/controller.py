import threading

import sys
sys.path.append('../')

from myobject import MyObject


class Controller(MyObject, threading.Thread):
    """Controller base class."""

    def __init__(self, name='Controller'):
        threading.Thread.__init__(self, name=name)
        self.dashboard = None
        self.dispatcher = None
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
        """Controller thread target."""
        self.log().info('running controller')
        self.log().info('controller finished')
        return

    def logon(self, name):
        """Handles device logon."""
        self.log().info("'%s' logged on", name)
        return

    def logoff(self, name):
        """Handles device logoff."""
        self.log().info("'%s' logged off", name)
        return

    def send_params(self, name, params):
        """Sends parameters."""
        if not self.dispatcher is None:
            self.dispatcher.send_params(name, params)

        return

    def get_values(self):
        """Retrieves controller's data."""
        return {}
