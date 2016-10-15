from twisted.logger import Logger
from twisted.application.internet import ClientService
from twisted.application.service import MultiService
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import clientFromString

from protocol import CGateStatusFactory, CGateCommandFactory
import command

import re

log = Logger(namespace='txcgate')

STATUS_EP = clientFromString(reactor, "tcp:localhost:20025")
COMMAND_EP = clientFromString(reactor, "tcp:localhost:20023")
DEFAULT_NETWORK = 254

level_re = re.compile('300-([/\w]*):\W?LEVEL=(\d+)')

class CGateStatusService(ClientService):
    def __init__(self, endpoint=STATUS_EP):
        self.__factory = CGateStatusFactory()
        ClientService.__init__(self, endpoint, self.__factory)

    def setMessageHandler(self, callback):
        self.__factory.setMessageHandler(callback)

class CGateCommandService(ClientService):
    def __init__(self, endpoint=COMMAND_EP):
        self.protocol = None
        self.__factory = CGateCommandFactory()

        ClientService.__init__(self, endpoint, self.__factory)

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

    def ramp(self, address, level):
        self.send('RAMP {address} {level}'.format(address=address, level=int(round(float(level)))))

    def trigger_event(self, address, level):
        self.send('TRIGGER EVENT {address} {level}'.format(address=address, level=int(round(float(level)))))

    def on(self, address):
        self.send('ON {address}'.format(address=address))

    def off(self, address):
        self.send('OFF {address}'.format(address=address))

    def setMessageHandler(self, callback):
        self.__factory.setMessageHandler(callback)

class CGateService(MultiService):
    def __init__(self, status_endpoint=STATUS_EP, command_endpoint=COMMAND_EP, network=DEFAULT_NETWORK):
        MultiService.__init__(self)

        self.network = network

        self.cs = CGateStatusService(status_endpoint)
        self.cs.setName('status_service')
        self.cs.setServiceParent(self)

        self.cc = CGateCommandService(command_endpoint)
        self.cc.setName('command_service')
        self.cc.setServiceParent(self)

        self.__levels = {}
        self.__onStatusMessage = None
        self.__pollingLevel = False

        def handleStatusMessage(message):
            if isinstance(message, command.Command):
                if message.level != None and message.address != None:
                    log.debug("Storing {address} as {level}".format(address=message.address, level=message.level))
                    self.__levels[message.address] = int(message.level)
            if self.__onStatusMessage:
                self.__onStatusMessage(message)
        self.cs.setMessageHandler(handleStatusMessage)

        def handleCommandMessage(message):
            if self.__pollingLevel: #300-//HOME/254/56/1: level=0
                level_match = level_re.match(message)
                if level_match:
                    self.__levels[level_match.group(1)] = int(level_match.group(2))
        self.cc.setMessageHandler(handleCommandMessage)

        def pollLevels(protocol):
            self.__pollingLevel = True
            def stopPoll():
                self.__pollingLevel = False
            reactor.callLater(20, stopPoll)
            def poll():
                self.cc.send('GET {net}/56/* LEVEL'.format(net=self.network))
            reactor.callLater(5, poll)
        self.cc.whenConnected().addCallback(pollLevels)

    def setStatusMessageHandler(self, callback):
        self.__onStatusMessage = callback

    def send(self, message):
        self.cc.send(message)

    def ramp(self, address, level):
        self.cc.ramp(address, level)

    def on(self, address, force=False):
        if force or self.__levels.get(address, 0) == 0:
            self.cc.on(address)

    def off(self, address):
        self.cc.off(address)

    def trigger_event(self, address, level):
        self.cc.trigger_event(address, level)
