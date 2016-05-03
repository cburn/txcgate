from twisted.trial import unittest
from twisted.test import proto_helpers
from txcgate.protocol import CGateProtocol

def handleCommand(command):
    print command

class TestProtocol(unittest.TestCase):
    def setUp(self):
        self.tr = proto_helpers.StringTransport()
        self.proto = CGateProtocol()
        self.proto.handle = handleCommand
        self.proto.makeConnection(self.tr)

    def test_proto(self):
        msg = 'lighting ramp //HOME/254/56/46 0 12 #sourceunit=6 OID=46ee8710-b6d5-1033-a7a8-bacdd30054cb'
        self.proto.dataReceived(msg + '\r\n')
