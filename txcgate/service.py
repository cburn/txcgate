from twisted.logger import Logger
from twisted.application.internet import ClientService
from twisted.application.service import MultiService
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import clientFromString

from protocol import CGateStatusFactory, CGateCommandProtocol


log = Logger(namespace='txcgate')

STATUS_EP = clientFromString(reactor, "tcp:localhost:20025")
COMMAND_EP = clientFromString(reactor, "tcp:localhost:20023")


class CGateStatusService(ClientService):
    def __init__(self, endpoint=STATUS_EP):
        self._factory = CGateStatusFactory()
        ClientService.__init__(self, endpoint, self._factory)

    def setMessageHandler(self, callback):
        self._factory.setMessageHandler(callback)

class CGateCommandService(ClientService):
    def __init__(self, endpoint=COMMAND_EP):
        self.protocol = None
        self._factory = Factory.forProtocol(CGateCommandProtocol)
        ClientService.__init__(self, endpoint, self._factory)

    def startService(self):
        def retry():
            self.whenConnected().addCallback(clientConnect)
        def clientConnect(protocol):
            self.protocol = protocol
            self._lostDeferred.addCallback(clientDisconnect)
        def clientDisconnect(reason):
            self.protocol = None
            reactor.callLater(2, retry)
        ClientService.startService(self)
        retry()

    def send(self, message):
        if self.protocol:
            self.protocol.send(message)

class CGateService(MultiService):
    def __init__(self, status_endpoint=STATUS_EP, command_endpoint=COMMAND_EP):
        MultiService.__init__(self)

        self.cs = CGateStatusService(status_endpoint)
        self.cs.setName('status_service')
        self.cs.setServiceParent(self)

        self.cc = CGateCommandService(command_endpoint)
        self.cc.setName('command_service')
        self.cc.setServiceParent(self)

    def setMessageHandler(self, callback):
        self.cs.setMessageHandler(callback)

    def send(self, message):
        self.cc.send(message)
