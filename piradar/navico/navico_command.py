"""Note on sector blanking
### DEDUCTION ###

This command sets no transmit sectors
You can set up to 4 sectors, which are the blanking sectors

First the ENABLE COMMAND
[
    register = 0x0d
    command  = 0xc1
    sector = (0x00 to 0x03) maybe or maybe 1-4 dont know yet.
    3 bytes 0x00 padding
    enable = [0x00 or 0x01] I would guess
]
Then the Angle command
[
    register = 0xc0
    command = 0xc1
    sector = (0x00 to 0x03) maybe or maybe 1-4 dont know yet.
    3 bytes 0x00 padding
    start_angle = 2bytes (degree to decidegrees)
    end_angle = 2bytes (degree to decidegrees)
"""
import struct

__all__ = [
    'TxOnCmds',
    'TxOffCmds',
    'StayOnCmd',
    'ReportCmds',
    'RangeCmd',
    'BearingAlignmentCmd',
    'GainCmd',
    'SeaClutterCmd',
    'RainClutterCmd',
    'SidelobeSuppressionCmd',
    'SeaClutterNudgeCmd',
    'DopplerModeCmd',
    'DopplerSpeedCmd',
    'AntennaHeightCmd',
    'InterferenceRejectionCmd',
    'SeaStateAutoCmd',
    'ScanSpeedCmd',
    'ModeCmd',
    'NoiseRejectionCmd',
    'TargetExpansionCmd',
    'TargetExpansionHaloCmd',
    'TargetSeparationCmd',
    'TargetBoostCmd',
    'LightCmd',
    'LocalInterferenceFilterCmd',

    'SetBlankingSectorCmd',
    'EnableBlankingSectorCmd'
]

ENDIAN = "<"


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
    register = 0xa0
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
    """
     CMD  |         255 |
     0  1 |  3  4  5  6 |
    03 C1 | ff 00 00 00 |
    """
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
     CMD    |      fill |  1 |     fill  | 255
     0  1  2|   3  4  5 |  6 |  7  8  9 |  10
    06 C1 00|  00 00 00 | 01 | 00 00 00 |  ff
    """

    cformat = "BBB BBB B BBB B"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x00

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd,
                           0,0,0, auto,
                           0,0,0, value)


class _SeaClutterCmd:
    """
     CMD    |      fill |  1 |     fill  | 255
     0  1  2|   3  4  5 |  6 |  7  8  9 |  10
    06 C1 02|  00 00 00 | 01 | 00 00 00 |  ff
    """
    cformat = "BBB BBB B BBB B"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x02

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd,
                           0,0,0, auto,
                           0,0,0, value)

class _RainClutterCmd:
    """
     CMD    |      fill |  1 |     fill  | 255
     0  1  2|   3  4  5 |  6 |  7  8  9 |  10
    06 C1 04|  00 00 00 | 01 | 00 00 00 |  ff
    """
    cformat = "BBB BBB B BBB B"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x04

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd,
                           0,0,0, auto,
                           0,0,0, value)


class _SidelobeSuppressionCmd:
    """
     CMD    |      fill |  1 |     fill  | 255
     0  1  2|   3  4  5 |  6 |  7  8  9 |  10
    06 C1 05|  00 00 00 | 01 | 00 00 00 |  ff
    """
    cformat = "BBB BBB B BBB B"
    register = 0x06
    cmd = 0xc1
    sub_cmd = 0x05

    def pack(self, auto: bool, value: int):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd,
                           0,0,0, auto,
                           0,0,0, value)


class _InterferenceRejection:
    cformat = "BBB"
    register = 0x08
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _TargetBoostCmd: # maybe just for BR24 ?
    cformat = "BBB"
    register = 0x0a
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 2 off, low, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)



class _SeaStateAutoCmd:
    cformat = "BBB"
    register = 0x0b
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 1 or 2, (0-calm) moderate, rough"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _LocalInterferenceFilterCmd:
    cformat = "BBB"
    register = 0x0e
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
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


class _SeaClutterNudgeCmd:
    """
    |                | Registry | Command | Manual / Auto | Value 1 | Value 2 | Selector |
    |:---------------|---------:|--------:|--------------:|--------:|--------:|---------:|
    | *byte length*  |        1 |       1 |             1 |       1 |       1 |        1 |
    | Auto  Settings |       11 |      01 |            01 |      XX |      XX |       04 |
    | Manual Settngs |       11 |      01 |            00 |      XX |      XX |       02 |
    | Switch On/Off  |       11 |      01 |            XX |      00 |      00 |       01 |
    """
    cformat = "BBBbbB"
    register = 0x11
    cmd = 0xc1

    def pack(self, auto: bool, value: int):

        if auto is True:
            selector = 0x04
        else:
            selector = 0x02

        if value < 0:
            increment_sign = 0x00
        else:
            increment_sign = value

        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd,
                           auto, increment_sign, value, selector)


class _TargetExpansionCmd:
    cformat = "BBB"
    register = 0x09
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 or 1"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _TargetExpansionHaloCmd:
    cformat = "BBB"
    register = 0x12
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _NoiseRejectionCmd:
    cformat = "BBB"
    register = 0x21
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
    """
     CMD    |      fill |       1000
     0  1  2|   3  4  5 |  6  7  8  9
    30 C1 01|  00 00 00 | E8 03 00 00
    """
    cformat = "BBB BBB I"
    register = 0x30
    cmd = 0xc1
    sub_cmd = 0x01

    def pack(self, value):
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd,
                           0, 0, 0,
                           value)


class _LightCmd:
    cformat = "BBB"
    register = 0x31
    cmd = 0xc1

    def pack(self, value: int):
        """Values of 0 to 3 off, low, medium, high"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, value)


class _SetBlankingSector:
    """
     CMD  | Sector  |      fill |  Start |  Stop |
     0  1 |        2|   3  4  5 |   6  7 |  8  9 |
    C0 C1 |  [00,03]|  00 00 00 |  00 00 | 00 00 |
    """
    cformat = "BBB 3B HH"
    register = 0xc0
    cmd = 0xc1

    def pack(self, sector: int, start: int, stop: int):
        """Sector: 0..3 and start and stop are in decidegree"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, sector, 0, 0, 0, start, stop)


class _EnableBlankingSector:
    """
     CMD  | Sector  |      fill |  On/off |
     0  1 |        2|   3  4  5 |       6 |
    0d C1 |  [00,03]|  00 00 00 | [00,01] |
    """
    cformat = "BBB 3B B"
    register = 0x0d
    cmd = 0xc1

    def pack(self, sector: int, value: int):
        """Sector: 0..3 and value 0-1 (enable, disable)"""
        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, sector, 0, 0 ,0, value)


RangeCmd = _RangeCmd()  # TODO
BearingAlignmentCmd = _BearingAlignmentCmd()
GainCmd = _GainCmd()
SeaClutterCmd = _SeaClutterCmd()
RainClutterCmd = _RainClutterCmd()
SidelobeSuppressionCmd = _SidelobeSuppressionCmd()
SeaClutterNudgeCmd = _SeaClutterNudgeCmd()
DopplerModeCmd = _DopplerModeCmd()
DopplerSpeedCmd = _DopplerSpeedCmd()
AntennaHeightCmd = _AntennaHeightCmd()
InterferenceRejectionCmd = _InterferenceRejection()
SeaStateAutoCmd = _SeaStateAutoCmd()
ScanSpeedCmd = _ScanSpeedCmd()
ModeCmd = _ModeCmd()
NoiseRejectionCmd = _NoiseRejectionCmd()
TargetExpansionCmd = _TargetExpansionCmd()
TargetExpansionHaloCmd = _TargetExpansionHaloCmd()
TargetSeparationCmd = _TargetSeparationCmd()
TargetBoostCmd = _TargetBoostCmd()
LightCmd = _LightCmd()
LocalInterferenceFilterCmd = _LocalInterferenceFilterCmd()

SetBlankingSectorCmd = _SetBlankingSector()
EnableBlankingSectorCmd = _EnableBlankingSector()

