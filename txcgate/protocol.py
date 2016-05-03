from message import CGateVisitor, ParseError
from twisted.protocols.basic import LineReceiver
from sys import stdout

class CGateProtocol(LineReceiver):
    def __init__(self):
        self.visitor = CGateVisitor()
        self.handle = None

    def lineReceived(self, data):
        try:
            command = self.visitor.parse(data)
            if self.handle: self.handle(command) 
        except ParseError: pass
