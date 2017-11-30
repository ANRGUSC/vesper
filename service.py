import collections

from myobject import MyObject

class Service(MyObject):
    """Base class for Services."""

    def __init__(self, name):
        assert(type(name) == str)

        self.name = name

        self.handlers = collections.defaultdict(
            lambda: self.default_handler
        )
        return

    def default_handler(self, protocol, message):
        """Default message handler."""
        self.log().warn('unhandled message: %s', message)
        return

    def connected(self, protocol):
        """Handles successful connection."""
        self.log().debug('connected')
        #self.protocol = protocol
        return

    def handle(self, protocol, message):
        """Routes message to its corresponding handler."""
        self.log().debug('handling %s', message)
        self.handlers[message.type](protocol, message)
        return

    def disconnected(self, protocol):
        """Handles connection loss."""
        self.log().debug('disconnected')
        #self.protocol = None
        return
