from twisted.trial import unittest
from txcgate import message, command
import parsimonious.exceptions


class TestMessage(unittest.TestCase):
    def test_ramp(self):
        msg = 'lighting ramp //HOME/254/56/46 0 12 #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.Ramp)
        self.assertEqual(cmd.address, '//HOME/254/56/46')
        self.assertEqual(cmd.level, 0)
        self.assertEqual(cmd.time, 12)
        self.assertEqual(cmd.__str__(), 'RAMP //HOME/254/56/46 0 12')

        msg = 'lighting ramp //HOME/254/56/46 50% 12m #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.Ramp)
        self.assertEqual(cmd.address, '//HOME/254/56/46')
        self.assertEqual(cmd.level, 128)
        self.assertEqual(cmd.time, 720)
        self.assertEqual(cmd.__str__(), 'RAMP //HOME/254/56/46 128 720')

    def test_on(self):
        msg = 'lighting on //HOME/254/56/3  #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.On)
        self.assertEqual(cmd.address, '//HOME/254/56/3')
        self.assertEqual(cmd.level, 255)
        self.assertEqual(cmd.time, 0)
        self.assertEqual(cmd.__str__(), 'RAMP //HOME/254/56/3 255 0')

    def test_short_on(self):
        msg = 'on //HOME/254/56/3'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.On)
        self.assertEqual(cmd.address, '//HOME/254/56/3')
        self.assertEqual(cmd.level, 255)
        self.assertEqual(cmd.time, 0)
        self.assertEqual(cmd.__str__(), 'RAMP //HOME/254/56/3 255 0')

    def test_off(self):
        msg = 'lighting off //HOME/254/56/45  #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.Off)
        self.assertEqual(cmd.address, '//HOME/254/56/45')
        self.assertEqual(cmd.level, 0)
        self.assertEqual(cmd.time, 0)
        self.assertEqual(cmd.__str__(), 'RAMP //HOME/254/56/45 0 0')

    def test_trigger(self):
        msg = 'trigger event //HOME/254/202/13 3 #sourceunit=6 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.Trigger)
        self.assertEqual(cmd.address, '//HOME/254/202/13')
        self.assertEqual(cmd.level, 3)
        self.assertEqual(cmd.time, 0)
        self.assertEqual(cmd.__str__(), 'TRIGGER EVENT //HOME/254/202/13 3')

    def test_zone_sealed(self):
        msg = '# security zone_sealed //HOME/254/208/2  #sourceunit=20 OID='
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.ZoneSealed)
        self.assertEqual(cmd.address, '//HOME/254/208/2')
        self.assertEqual(cmd.level, 255)
        self.assertEqual(cmd.__str__(), '# security zone_sealed //HOME/254/208/2')

    def test_zone_unsealed(self):
        msg = '# security zone_unsealed //HOME/254/208/2  #sourceunit=20 OID='
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.ZoneSealed)
        self.assertEqual(cmd.address, '//HOME/254/208/2')
        self.assertEqual(cmd.level, 0)
        self.assertEqual(cmd.__str__(), '# security zone_unsealed //HOME/254/208/2')

    def test_security_armed(self):
        msg = '# security system_arm //HOME/254/208 1 #sourceunit=20 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.SystemArmed)
        self.assertEqual(cmd.address, '//HOME/254/208')
        self.assertEqual(cmd.level, 1)
        self.assertEqual(cmd.__str__(), '# security system_arm //HOME/254/208 1')

        msg = '# security system_arm //HOME/254/208 0 #sourceunit=20 OID=00000000-0000-0000-0000-000000000000'
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsInstance(cmd, command.SystemArmed)
        self.assertEqual(cmd.address, '//HOME/254/208')
        self.assertEqual(cmd.level, 0)
        self.assertEqual(cmd.__str__(), '# security system_arm //HOME/254/208 0')

    def test_bad_message(self):
        msg = 'a bad message'
        self.assertRaises(parsimonious.exceptions.ParseError, message.CGateVisitor().parse, msg)

    def test_trigger_msg(self):
        msg = "# trigger min //HOME/254/202/38  #sourceunit=20 OID=00000000-0000-0000-0000-000000000000"
        cmd = message.CGateVisitor().parse(msg)
        self.assertIsNone(cmd)
