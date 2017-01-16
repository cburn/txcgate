from twisted.trial import unittest
from twisted.test import proto_helpers
from txcgate.protocol import CGateStatusProtocol
from txcgate import message, command

class dummy_factory(object):
    def _onMessage(self, command):
        self.cmd = command

class TestProtocol(unittest.TestCase):
    def setUp(self):
        self.tr = proto_helpers.StringTransport()
        self.proto = CGateStatusProtocol()
        self.proto.factory = dummy_factory
        self.proto.makeConnection(self.tr)

    def test_proto(self):
        msg = 'lighting ramp //HOME/254/56/46 0 12 #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        self.proto.dataReceived(msg + '\r\n')
        self.assertIsInstance(self.proto.factory.cmd, command.Ramp)
        self.assertEqual(self.proto.cmd.address, '//HOME/254/56/46')
        self.assertEqual(self.proto.cmd.level, 0)
        self.assertEqual(self.proto.cmd.time, 12)
        self.assertEqual(self.proto.cmd.__str__(), 'RAMP //HOME/254/56/46 0 12')

    test_proto.skip = "Test in development"
