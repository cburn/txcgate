from twisted.internet.protocol import Protocol
from sys import stdout

class CGate(Protocol):
    def dataReceived(self, data):
        stdout.write(data)
