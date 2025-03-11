import struct



class RangeCmd:
    cformat = "HI"
    cmd = 0xc103

    def pack(self, value):
        value = int(value * 10)
        return struct.pack("!" + self.cformat, self.cmd, value)


class BearingAlignmentCmd:
    cformat = "HH"
    cmd = 0xc105

    def pack(self, value):
        value = int(value * 10)
        return struct.pack("!" + self.cformat, self.cmd, value)


class GainCmd:
    cformat = "HIIB"
    cmd = 0xc106
    sub_cmd = 0x00

    def pack(self, auto: bool, value: int):
        value = int(value * 255 / 100)
        value = min(int(value), 255)
        return struct.pack("!" + self.cformat, self.cmd, self.sub_cmd, auto, value)


class SeaClutterCmd:
    cformat = "HIIB"
    cmd = 0xc106
    sub_cmd = 0x02

    def pack(self, auto: bool, value: int):
        value = int(value * 255 / 100)
        value = min(int(value), 255)
        return struct.pack("!" + self.cformat, self.cmd, self.sub_cmd, auto, value)


class RainClutterCmd:
    cformat = "HIIB"
    cmd = 0xc106
    sub_cmd = 0x04

    def pack(self, auto: bool, value: int):
        value = int(value * 255 / 100)
        value = min(int(value), 255)
        return struct.pack("!" + self.cformat, self.cmd, self.sub_cmd, auto, value)


class SidelobeSuppressionCmd:
    cformat = "HIIB"
    cmd = 0xc106
    sub_cmd = 0x05

    def pack(self, auto: bool, value: int):
        value = int(value * 255 / 100)
        value = min(int(value), 255)
        return struct.pack("!" + self.cformat, self.cmd, self.sub_cmd, auto, value)

class AutoSeaClutterNudgeCmd:
    cformat = "HBbbB"
    cmd = 0xc111
    sub_cmd = 0x01
    tail = 0x04

    def pack(self, value):
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, self.sub_cmd, value, value, self.tail)


class DooplerSpeedCmd:
    cformat = "HH"
    cmd = 0xc124

    def pack(self, value):
        value = int(value * 100)
        return struct.pack("!" + self.cformat, self.cmd, value)


class AntennaHeightCmd:
    cformat = "HII"
    cmd = 0xc130
    one = 0x01

    def pack(self, value):
        value = int(value * 1000) # to mm
        return struct.pack("!" + self.cformat, self.cmd, self.one, value)

class EnumCmd: # fixme me many commands
    cformat = "HB"
    cmd: int
    value: int

    def __init__(self, key, value):
        pass

    def pack(self, value):
        # fixme
        return struct.pack("!" + self.cformat, self.cmd, value)


class InterferanceRejection:
    cformat = "HB"
    cmd = 0xc108

    def pack(self, value):
        """Values of 0 to 3 off, low, medium, high"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class SeaStateCmd:
    cformat = "HB"
    cmd = 0xc10b

    def pack(self, value):
        """Values of 1 or 2, (0-calm) moderate, rough"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class ScanSpeedCmd:
    cformat = "HB"
    cmd = 0xc10f

    def pack(self, value):
        """Values of 1 or 3, (0-low) medium, high"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class ModeCmd:
    cformat = "HB"
    cmd = 0xc110

    def pack(self, value):
        """Values of 1 ,2, 3, 5 (0-default), harbor, offshore, weather, bird"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class TargetExpansionCmd:
    cformat = "HB"
    cmd = 0xc112

    def pack(self, value):
        """Values of 0 to 3 off, low, medium, high"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class NoiseRejectionCmd:
    cformat = "HB"
    cmd = 0xc121

    def pack(self, value):
        """Values of 0 to 3 off, low, medium, high"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class TargetSeparationCmd:
    cformat = "HB"
    cmd = 0xc122

    def pack(self, value):
        """Values of 0 to 3 off, low, medium, high"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)


class DooplerCmd:
    cformat = "HB"
    cmd = 0xc123

    def pack(self, value):
        """Values of 1, 2, (0-off) normal, approaching_only"""
        value = int(value)
        return struct.pack("!" + self.cformat, self.cmd, value)



if __name__ == '__main__':
    #radar_addresses = scan_for_halo_radar()
    print(RangeCmd().pack(100))
    print(AntennaHeightCmd().pack(100))
