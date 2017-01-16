class Command(object):
    def __init__(self):
        self.address = None
        self.level = None

    def __str__(self):
        return "# noop"

class Ramp(Command):
    def __init__(self, address, level, time=0):
        self.address = address
        self.level = level
        self.time = time

    def __str__(self):
        return "RAMP {} {} {}".format(self.address, self.level, self.time)

class On(Ramp):
    def __init__(self, address):
        Ramp.__init__(self, address, 255, 0)

class Off(Ramp):
    def __init__(self, address):
        Ramp.__init__(self, address, 0, 0)

class Trigger(Ramp):
    def __str__(self):
        return "TRIGGER EVENT {} {}".format(self.address, self.level)

class ZoneSealed(Command):
    def __init__(self, address, sealed):
        self.address = address
        self.level = sealed

    def __str__(self):
        if self.level:
            return "# security zone_sealed {}".format(self.address)
        else:
            return "# security zone_unsealed {}".format(self.address)

class SystemArmed(Command):
    def __init__(self, address, type):
        self.address = address
        self.level = type

    def __str__(self):
        return "# security system_arm {} {}".format(self.address, self.level)
