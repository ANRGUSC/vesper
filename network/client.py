import cPickle as pickle

from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.protocols.policies import TimeoutMixin

import sys
sys.path.append('../')

import config as cfg

from common import MyObject


class ClientProtocol(MyObject, NetstringReceiver, TimeoutMixin):
    """Client protocol for Twisted framework."""

    def __init__(self, factory):
        self.MAX_LENGTH = cfg.MAX_DATA_SIZE

        self.heartbeat = task.LoopingCall(self.sendHeartbeat)
        self.client = factory.client
        return

    def connectionMade(self):
        self.log().info('connected')
        self.transport.setTcpNoDelay(True)      # Disable Nagle's algorithm

        self.setTimeout(cfg.TIMEOUT)            # Timeout
        self.heartbeat.start(0.5 * cfg.TIMEOUT)

        self.client.connected(self)
        return

    def stringReceived(self, data):
        self.resetTimeout()

        # Ignore heartbeats
        if not data:
            return

        self.log().debug('received %d bytes', len(data))

        message = pickle.loads(data)
        self.client.handle(self, message)
        return

    def connectionLost(self, reason):
        self.log().info('connection lost: %s', reason.getErrorMessage())
        self.client.disconnected(self)
        return

    def timeoutConnection(self):
        self.log().info('connection timeout')
        self.transport.abortConnection()
        return

    def send(self, data):
        message = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        self.log().debug('sending %s (%d bytes)', data, len(message))
        reactor.callFromThread(reactor.callLater, 0, self.sendString, message)

        self.heartbeat.reset()
        return

    def sendHeartbeat(self):
        reactor.callFromThread(reactor.callLater, 0, self.sendString, '')
        return


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
        #self.log().info('connection lost: %s', reason.getErrorMessage())
        ReconnectingClientFactory.clientConnectionLost(self, connector,
                                                         reason)
        return

    def clientConnectionFailed(self, connector, reason):
        self.log().warn('connection failed: %s', reason.getErrorMessage())
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
        return


class Client():

    def __init__(self, service_client, host, port):
        reactor.connectTCP(cfg.SERVER_HOST, cfg.SERVER_PORT,
                           ClientProtocolFactory(service_client))

    def run(self):
        reactor.run()

    def stop(self):
        reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    import copy
    import logging.config

    mylogcfg = copy.deepcopy(cfg.LOGCFG)
    mylogcfg['handlers']['file']['filename'] = 'client_output.log'

    logging.config.dictConfig(mylogcfg)

    class ServiceClient(MyObject):

        def connected(self, protocol):
            self.log().info('connected()')

        def handle(self, protocol, message):
            self.log().debug('handling message: %s', message)

            reactor.callFromThread(protocol.send, 'Hi')

        def disconnected(self, protocol):
            self.log().info('disconnected()')

    Client(ServiceClient(), cfg.SERVER_HOST, cfg.SERVER_PORT).run()
