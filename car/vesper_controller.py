import sys
sys.path.append('../')

from common import Controller


class VesperController(Controller):

    def __init__(self):
        Controller.__init__(self)
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

