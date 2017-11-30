import config as cfg
import cPickle as pickle

from myobject import MyObject

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor

class ClientProtocol(MyObject, NetstringReceiver):
    """Client protocol for Twisted framework."""

    def __init__(self, factory):
        self.MAX_LENGTH = cfg.MAX_DATA_SIZE

        self.client = factory.client

    def connectionMade(self):
        self.log().info('connected')
        self.transport.setTcpNoDelay(True)      # Disable Nagle's algorithm
        self.client.connected(self)
        return

    def stringReceived(self, data):
        self.log().debug('received %d bytes', len(data))
        message = pickle.loads(data)
        self.client.handle(self, message)
        return

    def connectionLost(self, reason):
        self.log().info('connection lost: %s', reason)
        self.client.connection_lost(self)
        return

    def send(self, data):
        message = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        self.sendString(message)


class ClientProtocolFactory(MyObject, ReconnectingClientFactory):
    """Protocol factory for Twisted framework."""

    protocol =  ClientProtocol

    def __init__(self, client):
        self.client = client
        self.maxDelay = 1

    def startedConnecting(self, connector):
        self.log().info('connecting to %s:%s', connector.host, connector.port)

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.protocol(self)

    def clientConnectionLost(self, connector, reason):
        self.log().info('connect lost: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector,
                                                         reason)
        return

    def clientConnectionFailed(self, connector, reason):
        self.log().warn('connect failed: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
        return


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'server_output.log'

    logging.config.dictConfig(mylogcfg)

    class Client(MyObject):

        def connected(self, protocol):
            self.log().info('connected()')

        def handle(self, protocol, message):
            self.log().debug('handling message: %s', message)

            reactor.callFromThread(protocol.send, 'Hi')

        def connection_lost(self, protocol):
            self.log().info('connection_lost()')

    reactor.connectTCP(cfg.SERVER_HOST, cfg.SERVER_PORT,
                       ClientProtocolFactory(Client()))
    reactor.run()
