import struct

__all__ = [
    'TxOnCmds',
    'TxOffCmds',
    'StayOnCmd',
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
    'TargetBoostCmd',
    'LightCmd',
    'LocalInterferenceFilterCmd'
]

ENDIAN = ">"


class TxOnCmds:
    cmd = 0xc1
    #                        register, cmd, value
    A = struct.pack(ENDIAN+"3B", 0x00, cmd, 0x01)
    B = struct.pack(ENDIAN+"3B", 0x01, cmd, 0x01)


class TxOffCmds:
    cmd = 0xc1
    #                        register, cmd, value
    A = struct.pack(ENDIAN+"3B", 0x00, cmd, 0x01)
    B = struct.pack(ENDIAN+"3B", 0x01, cmd, 0x00)


class StayOnCmd:
    register = 0x0a
    cmd = 0xc1
    value = 0x02
    A = struct.pack(ENDIAN+"3B", register, cmd, value)


class ReportCmds:
    cmd = 0xc2
    R284 = struct.pack("BB", 0x03, cmd)
    R3 = struct.pack("BB", 0x04, cmd)
    R4 = struct.pack("BB", 0x05, cmd)
    R9 = struct.pack("BB", 0x0a, cmd) # unkown report 0x09C4


class _RangeCmd:
    cformat = "BBI"
    register = 0x03
    cmd = 0xc1

    def pack(self, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _BearingAlignmentCmd:
    cformat = "BBH"
    register = 0x05
    cmd = 0xc1

    def pack(self, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _GainCmd:
    """
    0   1  2  [        3] [        4]
    06 C1 00  00 00 00 01 00 00 00 A1
    """

    cformat = "BBBII"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x00

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, auto, value)


class _SeaClutterCmd:
    """
    0   1  2  [        3] [        4]
    06 C1 02  00 00 00 01 00 00 00 A1
    """
    cformat = "BBBII"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x02

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, auto, value)


class _RainClutterCmd:
    """
    0   1  2  [        3] [        4]
    06 C1 04  00 00 00 01 00 00 00 A1
    """
    cformat = "BBBII"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x04

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, auto, value)


class _SidelobeSuppressionCmd:
    """
    0   1  2  [        3] [        4]
    06 C1 05  00 00 00 01 00 00 00 A1
    """
    cformat = "BBBII"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x05

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, auto, value)


class _AutoSeaClutterNudgeCmd: # unsure of the cformat #TEST ME  FIXME with reports
    cformat = "BBBbbB"
    register = 0x11
    cmd = 0xc1
    sub_cmd = 0x01
    tail = 0x04

    def pack(self, value: int):

        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, value, value, self.tail)


class _DopplerModeCmd:
    cformat = "BBB"
    register = 0x23
    cmd = 0xc1

    def pack(self, value):
        """Values of 1, 2, (0-off) normal, approaching_only"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _DopplerSpeedCmd: # unsure of the cformat #TEST ME  FIXME with reports
    cformat = "BBH" #
    register = 0x24
    cmd = 0xc1

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _AntennaHeightCmd: # Unsure of cformat. to test FIXME with reports
    cformat = "BBBI"
    register = 0x30
    cmd = 0xc1
    sub_cmd = 0x01

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, value)


class _InterferenceRejection:
    cformat = "BBB"
    register = 0x08
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _SeaStateAutoCmd:
    cformat = "BBB"
    register = 0x0b
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 1 or 2, (0-calm) moderate, rough"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _ScanSpeedCmd:
    cformat = "BBB"
    register = 0x0f
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 1 or 3, (0-low) medium, high
        Maybe its 0 to reset and 1 to increase ?
        """
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _ModeCmd:
    cformat = "BBB"
    register = 0x10
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 1 ,2, 3, 5 (0-default), harbor, offshore, weather, bird"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _NoiseRejectionCmd:
    cformat = "BBB"
    register = 0x21
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _TargetExpansionCmd:
    cformat = "BBB"
    register = 0x12
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _TargetSeparationCmd:
    cformat = "BBB"
    register=0x22
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _LightCmd:
    cformat = "BBB"
    register = 0x31
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _TargetBoostCmd: # maybe just for BR24 ?
    cformat = "BBB"
    register = 0x0A
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 2 off, low, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _LocalInterferenceFilterCmd:
    cformat = "BBB"
    register = 0x0E
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)





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
TargetBoostCmd = _TargetBoostCmd()
LightCmd = _LightCmd()
LocalInterferenceFilterCmd = _LocalInterferenceFilterCmd()

