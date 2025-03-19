import struct

ENDIAN = "!"


class TxOnCmds:
    A = struct.pack(ENDIAN+"HB", 0x00c1, 0x01)
    B = struct.pack(ENDIAN+"HB", 0x01c1, 0x01)


class TxOffCmds:
    A = struct.pack(ENDIAN+"HB", 0x00c1, 0x01)
    B = struct.pack(ENDIAN+"HB", 0x01c1, 0x00)



class StayOnCmds:
    A0 = struct.pack(ENDIAN+"HB", 0xa0c1, 0x02)
    A = struct.pack("BB", 0xa0, 0xc1)
    B = struct.pack("BB", 0x03, 0xc2)
    C = struct.pack("BB", 0x04, 0xc2)
    D = struct.pack("BB", 0x05, 0xc2)
    E = struct.pack("BB", 0x0a, 0xc2)


class _RangeCmd:
    cformat = "HI"
    cmd = 0x03c1

    def pack(self, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


RangeCmd = _RangeCmd() # TODO

class BearingAlignmentCmd:
    cformat = "HH"
    cmd = 0x05c1

    def pack(self, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class GainCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x00

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class SeaClutterCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x02

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class RainClutterCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x04

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class SidelobeSuppressionCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x05

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class AutoSeaClutterNudgeCmd:
    cformat = "HBbbB"
    cmd = 0x11c1
    sub_cmd = 0x01
    tail = 0x04

    def pack(self, value: int):

        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, value, value, self.tail)


class DopplerModeCmd:
    cformat = "HB"
    cmd = 0x23c1

    def pack(self, value):
        """Values of 1, 2, (0-off) normal, approaching_only"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class DopplerSpeedCmd:
    cformat = "HH"
    cmd = 0x24c1

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class AntennaHeightCmd:
    cformat = "HII"
    cmd = 0x30c1
    one = 0x01

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.one, value)


class InterferenceRejection:
    cformat = "HB"
    cmd = 0x08c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class SeaStateCmd:
    cformat = "HB"
    cmd = 0x0bc1

    def pack(self, value: int):
        """Values of 1 or 2, (0-calm) moderate, rough"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class ScanSpeedCmd:
    cformat = "HB"
    cmd = 0x0fc1

    def pack(self, value: int):
        """Values of 1 or 3, (0-low) medium, high
        Maybe its 0 to reset and 1 to increase ?
        """
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class ModeCmd:
    cformat = "HB"
    cmd = 0x10c1

    def pack(self, value: int):
        """Values of 1 ,2, 3, 5 (0-default), harbor, offshore, weather, bird"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class TargetExpansionCmd:
    cformat = "HB"
    cmd = 0x12c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class NoiseRejectionCmd:
    cformat = "HB"
    cmd = 0x21c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class TargetSeparationCmd:
    cformat = "HB"
    cmd = 0x22c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class LightCmd:
    cformat = "HB"
    cmd = 0x31c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


# class EnumCmd: # fixme me many commands
#     cformat = "HB"
#     cmd: int
#     value: int
#
#     def __init__(self, key, value):
#         pass
#
#     def pack(self, value):
#         # fixme
#         return struct.pack(ENDIAN + self.cformat, self.cmd, value)




if __name__ == '__main__':
    #radar_addresses = scan_for_halo_radar()
    print(RangeCmd().pack(100))
    print(AntennaHeightCmd().pack(100))
