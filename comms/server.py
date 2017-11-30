import cPickle as pickle

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import NetstringReceiver
from twisted.protocols.policies import TimeoutMixin
from twisted.internet import reactor

import sys
sys.path.append('../')

import config as cfg
from myobject import MyObject


class ServerProtocol(MyObject, NetstringReceiver, TimeoutMixin):
    """Server protocol for Twisted framework."""

    def __init__(self, factory):
        self.MAX_LENGTH = cfg.MAX_DATA_SIZE

        self.service = factory.service
        return

    def connectionMade(self):
        self.log().info('connection made')
        self.transport.setTcpNoDelay(True)      # Disable Nagle's algorithm
        #self.setTimeout()
        self.service.connected(self)
        return

    def stringReceived(self, data):
        self.log().debug('received %d bytes', len(data))
        self.resetTimeout()
        message = pickle.loads(data)
        self.service.handle(self, message)
        return

    def connectionLost(self, reason):
        self.log().info('connection lost: %s', reason.getErrorMessage())
        self.service.disconnected(self)
        return

    def timeoutConnection(self):
        self.log().info('connection timeout')
        self.transport.abortConnection()
        return

    def send(self, data):
        message = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        self.log().debug('sending %s (%d bytes)', data, len(message))
        self.sendString(message)


class ServerFactory(MyObject, Factory):
    """Server protocol factory for Twisted framework."""

    protocol = ServerProtocol

    def __init__(self, service):
        self.service = service
        return

    def buildProtocol(self, addr):
        self.log().info('connection from %s:%s', addr.host, addr.port)
        return self.protocol(self)


class Server():

    def __init__(self, service, port, interface=''):
        endpoint = TCP4ServerEndpoint(reactor, port,
                                      interface=interface)
        endpoint.listen(ServerFactory(service))

    def run(self):
        reactor.run()

    def stop(self):
        reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'server_output.log'

    logging.config.dictConfig(mylogcfg)

    class Service(MyObject):

        def connected(self, protocol):
            self.log().info('connected()')

            reactor.callFromThread(protocol.send, 'Hello')

        def handle(self, protocol, message):
            self.log().debug('handling message: %s', message)

        def disconnected(self, protocol):
            self.log().info('disconnection()')

    Server(Service(), cfg.SERVER_PORT).run()
