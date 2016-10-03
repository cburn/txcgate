from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory
from twisted.logger import Logger

from message import CGateVisitor, ParseError


log = Logger(namespace='txcgate')

class CGateStatusFactory(Factory):
    def __init__(self):
        self._onMessage = None
        self.protocol = CGateStatusProtocol

    def setMessageHandler(self, callback):
        self._onMessage = callback

class CGateStatusProtocol(LineOnlyReceiver):
    def __init__(self, ignore_parse_errors=True):
        self.visitor = CGateVisitor()
        self.ignore_parse_errors = ignore_parse_errors

    def lineReceived(self, data):
        try:
            command = self.visitor.parse(data)
            if self.factory._onMessage:
                self.factory._onMessage(command)
        except ParseError:
            if self.ignore_parse_errors: pass
            else: raise

    def connectionMade(self):
        log.info('Connected to cgate status port  : {remote}', remote=self.transport.getPeer())

class CGateCommandFactory(Factory):
    def __init__(self):
        self._onMessage = None
        self.protocol = CGateCommandProtocol

    def setMessageHandler(self, callback):
        self._onMessage = callback

class CGateCommandProtocol(LineOnlyReceiver):
    def __init__(self, ignore_parse_errors=True):
        self.visitor = CGateVisitor()

    def connectionMade(self):
        log.info('Connected to cgate command port : {remote}', remote=self.transport.getPeer())

    def lineReceived(self, data):
        if self.factory._onMessage:
            self.factory._onMessage(data)

    def send(self, data):
        # command = self.visitor.parse(data)
        # self.sendLine(str(command))
        self.sendLine(data)
