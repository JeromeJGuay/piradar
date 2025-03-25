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



class _AutoSeaClutterNudgeCmd: # unsure of the cformat #TEST ME  FIXME with reports
    """
    case CT_SEA: {
      if (m_ri->m_radar_type >= RT_HaloA) {
        // Capture data:
        // Data: 11c101000004 = Auto
        // Data: 11c10100ff04 = Auto-1
        // Data: 11c10100ce04 = Auto-50
        // Data: 11c101323204 = Auto+50
        // Data: 11c100646402 = 100
        // Data: 11c100000002 = 0
        // Data: 11c100000001 = Mode manual
        // Data: 11c101000001 = Mode auto

        uint8_t cmd[] = {0x11, 0xc1, 0, 0, 0, 1};

        if (state == RCS_MANUAL) {
          cmd[2] = 0x00;
          r = TransmitCmd(cmd, sizeof(cmd));
          cmd[5] = 0x02;
        } else {
          cmd[2] = 0x01;
          r = TransmitCmd(cmd, sizeof(cmd));
          cmd[5] = 0x04;
        }
        if (value > 0) {
          cmd[3] = (uint8_t)value;
        }
        cmd[4] = (uint8_t)value;
        LOG_VERBOSE(wxT("%s Halo Sea: %d auto %d"), m_name.c_str(), value, autoValue);
        r = TransmitCmd(cmd, sizeof(cmd));
      } else {
        int v = (value + 1) * 255 / 100;
        if (v > 255) {
          v = 255;
        }
        uint8_t cmd[] = {0x06, 0xc1, 0x02, 0, 0, 0, (uint8_t)autoValue, 0, 0, 0, (uint8_t)v};

        LOG_VERBOSE(wxT("%s Sea: %d auto %d"), m_name.c_str(), value, autoValue);
        r = TransmitCmd(cmd, sizeof(cmd));
      }
      break;
    """
    cformat = "BBBbbB"
    register = 0x11 # FIXME
    cmd = 0xc1
    sub_cmd = 0x01
    tail = 0x04

    def pack(self, value: int):

        return struct.pack(ENDIAN + self.cformat, self.register, self.cmd, self.sub_cmd, value, value, self.tail)


class _TargetExpansionCmd:
    cformat = "BBB"
    register = 0x12 # could be 0x09 for BR24, G4 and G3
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
    30 C1 01|  00 00 00 | E8 03 00 A1
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

