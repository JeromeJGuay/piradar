import struct

__all__ = [
    'TxOnCmds',
    'TxOffCmds',
    'StayOnCmds',
    'RangeCmd',
    'BearingAlignmentCmd',
    'GainCmd',
    'SeaClutterCmd',
    'RainClutterCmd',
    'SidelobeSuppressionCmd',
    'AutoSeaClutterNudgeCmd',
    'DopplerModeCmd',
    'DopplerSpeedCmd',
    'AntennaHeightCmd',
    'InterferenceRejectionCmd',
    'SeaStateAutoCmd',
    'ScanSpeedCmd',
    'ModeCmd',
    'NoiseRejectionCmd',
    'TargetExpansionCmd',
    'TargetSeparationCmd',
    'LightCmd'
]

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

class _BearingAlignmentCmd:
    cformat = "HH"
    cmd = 0x05c1

    def pack(self, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _GainCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x00

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class _SeaClutterCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x02

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class _RainClutterCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x04

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class _SidelobeSuppressionCmd:
    cformat = "HIIB"
    cmd = 0x06c1
    sub_cmd = 0x05

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, auto, value)


class _AutoSeaClutterNudgeCmd:
    cformat = "HBbbB"
    cmd = 0x11c1
    sub_cmd = 0x01
    tail = 0x04

    def pack(self, value: int):

        return struct.pack(ENDIAN + self.cformat, self.cmd, self.sub_cmd, value, value, self.tail)


class _DopplerModeCmd:
    cformat = "HB"
    cmd = 0x23c1

    def pack(self, value):
        """Values of 1, 2, (0-off) normal, approaching_only"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _DopplerSpeedCmd:
    cformat = "HH"
    cmd = 0x24c1

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _AntennaHeightCmd:
    cformat = "HII"
    cmd = 0x30c1
    one = 0x01

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.cmd, self.one, value)


class _InterferenceRejection:
    cformat = "HB"
    cmd = 0x08c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _SeaStateAutoCmd:
    cformat = "HB"
    cmd = 0x0bc1

    def pack(self, value: int):
        """Values of 1 or 2, (0-calm) moderate, rough"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _ScanSpeedCmd:
    cformat = "HB"
    cmd = 0x0fc1

    def pack(self, value: int):
        """Values of 1 or 3, (0-low) medium, high
        Maybe its 0 to reset and 1 to increase ?
        """
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _ModeCmd:
    cformat = "HB"
    cmd = 0x10c1

    def pack(self, value: int):
        """Values of 1 ,2, 3, 5 (0-default), harbor, offshore, weather, bird"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _NoiseRejectionCmd:
    cformat = "HB"
    cmd = 0x21c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _TargetExpansionCmd:
    cformat = "HB"
    cmd = 0x12c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)



class _TargetSeparationCmd:
    cformat = "HB"
    cmd = 0x22c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)


class _LightCmd:
    cformat = "HB"
    cmd = 0x31c1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.cmd, value)



RangeCmd = _RangeCmd() # TODO
BearingAlignmentCmd = _BearingAlignmentCmd()
GainCmd = _GainCmd()
SeaClutterCmd = _SeaClutterCmd()
RainClutterCmd = _RainClutterCmd()
SidelobeSuppressionCmd = _SidelobeSuppressionCmd()
AutoSeaClutterNudgeCmd = _AutoSeaClutterNudgeCmd()
DopplerModeCmd = _DopplerModeCmd()
DopplerSpeedCmd = _DopplerSpeedCmd()
AntennaHeightCmd = _AntennaHeightCmd()
InterferenceRejectionCmd = _InterferenceRejection()
SeaStateAutoCmd = _SeaStateAutoCmd()
ScanSpeedCmd = _ScanSpeedCmd()
ModeCmd = _ModeCmd()
NoiseRejectionCmd = _NoiseRejectionCmd()
TargetExpansionCmd = _TargetExpansionCmd()
TargetSeparationCmd = _TargetSeparationCmd()
LightCmd = _LightCmd()

