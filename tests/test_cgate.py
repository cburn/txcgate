#!/usr/bin/python

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

from txcgate.protocol import CGate

point = TCP4ClientEndpoint(reactor, "homeauto", 20024)
d = connectProtocol(point, CGate())
reactor.run()
