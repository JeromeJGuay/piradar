from itertools import accumulate
import struct
import socket

from dataclasses import dataclass

ENDIAN = "!"

class ReportIds:
    _01B2 = 0x01b2
    _01C4 = 0x01c4
    _02C4 = 0x02c4
    _03C4 = 0x03c4
    _04C4 = 0x04c4
    # _05C4 = 0x05c4 # Not use (maybe it doesnt not exist)
    _06C4 = 0x06c4
    # _07C4 = 0x07c4 # Not use (maybe it doesnt not exist)
    _08C4 = 0x08c4
    # _09C4 = 0x09c4 # Not use (maybe it doesnt not exist)
    # _10C4 = 0x10c4 # Not use (maybe it doesnt not exist)
    # _11C4 = 0x11c4 # Not use (maybe it doesnt not exist)
    _12C4 = 0x12c4


class IPAddress:
    def __init__(self, data: tuple[int, int]):
        if isinstance(data[0], int):
            self.address = socket.inet_ntoa(struct.pack('!I', data[0]))
        else:
            self.address = data[0]
        self.port = data[1]

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.address)}, {repr(self.port)})"


class RadarReport01B2:
    cformats = ['H', '16s', 'LH', '12B', 'LH', '4B',
                'LH', '10B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH']

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]

        self.id = unpacked_fields[0][0]
        self.serialno = unpacked_fields[1] # decode as ascii to test fixme
        self.addr0 = IPAddress(unpacked_fields[2])
        self.u1 = unpacked_fields[3]
        self.addr1 = IPAddress(unpacked_fields[4])
        self.u2 = unpacked_fields[5]
        self.addr2 = IPAddress(unpacked_fields[6])
        self.u3 = unpacked_fields[7]
        self.addr3 = IPAddress(unpacked_fields[8])
        self.u4 = unpacked_fields[9]
        self.addr4 = IPAddress(unpacked_fields[10])
        self.u5 = unpacked_fields[11]
        self.addrDataA = IPAddress(unpacked_fields[12])
        self.u6 = unpacked_fields[13]
        self.addrSendA = IPAddress(unpacked_fields[14])
        self.u7 = unpacked_fields[15]
        self.addrReportA = IPAddress(unpacked_fields[16])
        self.u8 = unpacked_fields[17]
        self.addrDataB = IPAddress(unpacked_fields[18])
        self.u9 = unpacked_fields[19]
        self.addrSendB = IPAddress(unpacked_fields[20])
        self.u10 = unpacked_fields[21]
        self.addrReportB = IPAddress(unpacked_fields[22])
        self.u11 = unpacked_fields[23]
        self.addr11 = IPAddress(unpacked_fields[24])
        self.u12 = unpacked_fields[25]
        self.addr12 = IPAddress(unpacked_fields[26])
        self.u13 = unpacked_fields[27]
        self.addr13 = IPAddress(unpacked_fields[28])
        self.u14 = unpacked_fields[29]
        self.addr14 = IPAddress(unpacked_fields[30])
        self.u15 = unpacked_fields[31]
        self.addr15 = IPAddress(unpacked_fields[32])
        self.u16 = unpacked_fields[33]
        self.addr16 = IPAddress(unpacked_fields[34])

    def __repr__(self):
        _repr = f"{self.__class__.__name__}\n"
        for key, value in self.__dict__.items():
            _repr += f"{key}: {value}\n"
        return _repr


class RadarReport01C418:
    cformats = ["B", "B", "B", "B", "B", "B", "H", "H", "H"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.radar_status = unpacked_fields[2][0]
        self.field3 = unpacked_fields[3][0]
        self.field4 = unpacked_fields[4][0]
        self.field5 = unpacked_fields[5][0]
        self.field6 = unpacked_fields[6][0]
        self.field8 = unpacked_fields[7][0]
        self.field10 = unpacked_fields[7][0]


class RadarReport02C499:
    cformats = ["B", "B", "L", "B", "B", "L", "B", "B", "B", "H", "L", "B", "B", "B", "L", "L",
                "B", "B", "B", "B", "B", "B", "B", "B", "B", "B", "B",
                #"56B" Add if needed to have a size 99. at the moment size is 43
                ] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t register;                    // 0   0x02
          uint8_t command;                 // 1 0xC4
          uint32_t range;                  //  2-3   0x06 0x09
          uint8_t field4;                  // 6    0
          uint8_t mode;                    // 7    mode (0 = custom, 1 = harbor, 2 = offshore, 4 = bird, 5 = weather)
          uint32_t field8;                 // 8-11   1
          uint8_t gain;                    // 12
          uint8_t sea_auto;                // 13  0 = off, 1 = harbour, 2 = offshore
          uint8_t field14;                 // 14
          uint16_t field15;                // 15-16
          uint32_t sea;                    // 17-20   sea clutter (17)
          uint8_t field21;                 // 21
          uint8_t rain;                    // 22   rain clutter
          uint8_t field23;                 // 23
          uint32_t field24;                // 24-27
          uint32_t field28;                // 28-31
          uint8_t field32;                 // 32
          uint8_t field33;                 // 33
          uint8_t interference_rejection;  // 34
          uint8_t field35;                 // 35
          uint8_t field36;                 // 36
          uint8_t field37;                 // 37
          uint8_t target_expansion;        // 38
          uint8_t field39;                 // 39
          uint8_t field40;                 // 40
          uint8_t field41;                 // 41
          uint8_t target_boost;            // 42

          # NOTE THEIR MIGHT BE MORE FIELDS ?
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.range = unpacked_fields[2][0]
        self.field4 = unpacked_fields[3]
        self.mode = unpacked_fields[4][0]
        self.field8 = unpacked_fields[5][0]
        self.gain = unpacked_fields[6][0]
        self.sea_state_auto = unpacked_fields[7][0]
        self.field14 = unpacked_fields[8]
        self.field15 = unpacked_fields[9]
        self.sea_clutter = unpacked_fields[10][0]
        self.field21 = unpacked_fields[11]
        self.rain_clutter = unpacked_fields[12][0]
        self.field23 = unpacked_fields[13]
        self.field24 = unpacked_fields[14]
        self.field28 = unpacked_fields[15]
        self.field32 = unpacked_fields[16]
        self.field33 = unpacked_fields[17]
        self.interference_rejection = unpacked_fields[18][0]
        self.field35 = unpacked_fields[19]
        self.field36 = unpacked_fields[20]
        self.field37 = unpacked_fields[21]
        self.target_expansion = unpacked_fields[22][0]
        self.field39 = unpacked_fields[23]
        self.field40 = unpacked_fields[24]
        self.field41 = unpacked_fields[25]
        self.target_boost = unpacked_fields[26][0]
        #self.field42 = unpacked_fields[27][0] ## if needed to have len 99


class RadarReport03C4129:
    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t register;
        uint8_t command;
        uint8_t radar_type;  // I hope! 01 = 4G and new 3G, 08 = 3G, 0F = BR24, 00 = HALO
        uint8_t u00[31];     // Lots of unknown
        uint32_t hours;      // Hours of operation
        uint8_t u01[20];     // Lots of unknown
        uint16_t firmware_date[16];
        uint16_t firmware_time[16];
        uint8_t u02[7];
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO


class RadarReport04C466:
    cformats = ["B", "B", "L", "H", "H", "H", "L", "3B", "B"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t register;                // 0   0x04
          uint8_t command;             // 1   0xC4
          uint32_t field2;             // 2-5
          uint16_t bearing_alignment;  // 6-7
          uint16_t field8;             // 8-9
          uint16_t antenna_height;     // 10-11
          uint32_t field12;            // 12-15  0x00
          uint8_t field16[3];          // 16-18  0x00
          uint8_t accent_light;        // 19     accent light 0..3
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]

        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.field2 = unpacked_fields[2][0]
        self.bearing_alignment = unpacked_fields[3][0]
        self.field8 = unpacked_fields[4][0]
        self.antenna_height = unpacked_fields[5][0]
        self.field12 = unpacked_fields[6][0]
        self.field16 = unpacked_fields[7] # 3 values
        self.accent_light = unpacked_fields[8][0]


class SectorBlanking:
    cformat = "B2H"
    def __init__(self, data: tuple[int, int, int]):
        self.enable = data[0]
        self.start_angle = data[1]
        self.end_angle = data[2]


class RadarReport06C468:
    cformats = ["B", "B", "L", "6c", "24B"] + 4 * [SectorBlanking.cformat] + ["12B"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t register;                      // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[24];                // 12-35 unknown
        SectorBlankingReport blanking[4];  // 36-55
        uint8_t field3[12];                // 56-67
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.field1 = unpacked_fields[2][0]
        self.name = unpacked_fields[3] #6 values #myabe use 6s and unpack as ascii ? Fixme
        self.field2 = unpacked_fields[4] # 24 values
        self.blanking = (
            SectorBlanking(unpacked_fields[5]), # will be unpakced by SectorBlanking
            SectorBlanking(unpacked_fields[6]),
            SectorBlanking(unpacked_fields[7]),
            SectorBlanking(unpacked_fields[8])
        )
        self.field3 = unpacked_fields[9]


class RadarReport06C474:
    cformats = ["B", "B", "L", "6c", "30B"] + 4 * [SectorBlanking.cformat] + ["12B"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t register;                      // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[30];                // 12-41 unknown
        SectorBlankingReport blanking[4];  // 42-61
        uint8_t field4[12];                // 62-73
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.field1 = unpacked_fields[2][0]
        self.name = unpacked_fields[3] #6 values #myabe use 6s and unpack as ascii ? Fixme
        self.field2 = unpacked_fields[4] # 30 values
        self.blanking = (
            SectorBlanking(unpacked_fields[5]), # will be unpakced by SectorBlanking
            SectorBlanking(unpacked_fields[6]),
            SectorBlanking(unpacked_fields[7]),
            SectorBlanking(unpacked_fields[8])
        )
        self.field3 = unpacked_fields[9] # 12 values


class RadarReport08C418:
    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t register;                          // 0  0x08
        uint8_t command;                       // 1  0xC4
        uint8_t sea_state;                     // 2
        uint8_t local_interference_rejection;  // 3
        uint8_t scan_speed;                    // 4
        uint8_t sls_auto;                      // 5 installation: sidelobe suppression auto
        uint8_t field6;                        // 6
        uint8_t field7;                        // 7
        uint8_t field8;                        // 8
        uint8_t side_lobe_suppression;         // 9 installation: sidelobe suppression
        uint16_t field10;                      // 10-11
        uint8_t noise_rejection;               // 12    noise rejection
        uint8_t target_sep;                    // 13
        uint8_t sea_clutter;                   // 14 sea clutter on Halo
        int8_t auto_sea_clutter;               // 15 auto sea clutter on Halo
        uint8_t field13;                       // 16
        uint8_t field14;                       // 17
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO


class RadarReport08C421:

    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        RadarReport_08C4_18 old; # same a 08C418 here
        uint8_t doppler_state;
        uint16_t doppler_speed;
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO

class RadarReport12C466:
    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        // Device Serial number is sent once upon network initialization only
        uint8_t register;          // 0   0x12
        uint8_t command;       // 1   0xC4
        uint8_t serialno[12];  // 2-13 Device serial number at 3G (All?)
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO


class HaloHeadingPacket:
    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        {'N', 'K', 'O', 'E'},  // marker
        {0, 1, 0x90, 0x02},    // u00 bytes containing '00 01 90 02'
        0,                     // counter
        {0, 0, 0x10, 0, 0, 0x14, 0, 0, 4, 0, 0, 0, 0, 0, 5, 0x3C, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x20},  // u01
        {0x12, 0xf1},                                                                                // u02
        {0x01, 0x00},                                                                                // u03
        0,                                                                                           // epoch
        2,                                                                                           // u04
        0,                                                                                           // u05a, likely position
        0,                                                                                           // u05b, likely position
        {0xff},                                                                                      // u06
        0,                                                                                           // heading
        {0xff, 0x7f, 0x79, 0xf8, 0xfc}                                                               // u07
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ] #TODO


class HaloMysteryPacket:
    cformats = [] #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        {'N', 'K', 'O', 'E'},  // marker
        {0, 1, 0x90, 0x02},    // u00 bytes containing '00 01 90 02'
        0,                     // counter
        {0, 0, 0x10, 0, 0, 0x14, 0, 0, 4, 0, 0, 0, 0, 0, 5, 0x3C, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x20},  // u01
        {0x02, 0xf8},                                                                                // u02
        {0x01, 0x00},                                                                                // u03
        0,                                                                                           // epoch
        2,                                                                                           // u04
        0,                                                                                           // u05a, likely position
        0,                                                                                           // u05b, likely position
        {0xff},                                                                                      // u06
        {0xfc},                                                                                      // u07
        0,                                                                                           // mystery1
        0,                                                                                           // mystery2
        {0xff, 0xff}
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]


class RawSpokeData:
    cformats = ["B", "B", "H", "H", "H", "H", "H", "H", "H", "L", "L", "512B"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t headerLen;       // 1 bytes
          uint8_t status;          // 1 bytes
          uint16_t scan_number;    // 2 bytes, 0-4095
          uint16_t u00;            // Always 0x4400 (integer)
          uint16_t large_range;     // 2 bytes or -1
          uint16_t angle;          // 2 bytes
          uint16_t heading;        // 2 bytes heading with RI-10/11 or -1. See bitmask explanation above.
          uint16_t small_range;     // 2 bytes or -1
          uint16_t rotation;       // 2 bytes, rotation/angle
          uint32_t u02;            // 4 bytes signed integer, always -1
          uint32_t u03;            // 4 bytes signed integer, mostly -1 (0x80 in last byte) or 0xa0 in last byte
          uint8_t data[1024 / 2];
        """
        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]

        self.header_size = unpacked_fields[0][0]
        self.status = unpacked_fields[1][0]
        self.spoke_number = unpacked_fields[2][0]
        self.u00 = unpacked_fields[3][0]
        self.large_range = unpacked_fields[4][0]
        self.angle = unpacked_fields[5][0]
        self.heading = unpacked_fields[6][0]
        self.small_range = unpacked_fields[7][0]
        self.rotation_range = unpacked_fields[8][0]
        self.u02 = unpacked_fields[9][0]
        self.u03 = unpacked_fields[10][0]
        self.data = unpacked_fields[11]


class RawSectorData:
    """
    32 line expected. FIXME TODO
    make it so the number of line can vary according the size of the packet. that is:
    8 + number_of_lines * 536
    """
    # The number of spoke of the data is computed in the __init__().
    number_of_spokes = 32# 32. Maybe less ? make it so it can take more or less lines depending on the

    cformats = ["5B", "B", "H"] + number_of_spokes * ["".join(RawSpokeData.cformats)]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    header_size = int(size - number_of_spokes * RawSpokeData.size)

    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t stuff[5];
          uint8_t scanline_count;
          uint16_t scanline_size;
          RawScanline lines[120];  //  scan lines, or spokes
        """
        header_data = data[:self.header_size]
        unpacked_header= [
            struct.unpack_from(ENDIAN + ff, buffer=header_data, offset=fo)
            for ff, fo in zip(self.cformatsp[:3], self.field_offsets) # this is bad pratice [:3] fixme
        ]
        self.stuff = unpacked_header[0][0]
        self.number_of_spokes = unpacked_header[1][0]
        self.scanline_size = unpacked_header[2][0]

        self.number_of_spokes = int((RawSectorData.size - RawSectorData.header_size) / RawSpokeData.size)

        spokes_data = data[self.header_size:]

        self.spokes = [
            RawSpokeData(spokes_data[i * RawSpokeData.size: (i + 1) * RawSpokeData.size]) for i in range(self.number_of_spokes)
        ]



if __name__ == "__main__":
    #data=b"\x01\xb2\x31\x36\x31\x31\x34\x30\x31\x38\x38\x30\x00\x00\x00\x00\x00\x00\xc0\xa8\x01\xb9\x01\x01\x06\x00\xfd\xff\x20\x01\x02\x00\x10\x00\x00\x00\xc0\xa8\x01\xb9\x17\x60\x11\x00\x00\x00\xec\x06\x07\x16\x1a\x26\x1f\x00\x20\x01\x02\x00\x10\x00\x00\x00\xec\x06\x07\x17\x1a\x1c\x11\x00\x00\x00\xec\x06\x07\x18\x1a\x1d\x10\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x08\x1a\x16\x11\x00\x00\x00\xec\x06\x07\x0a\x1a\x18\x12\x00\x00\x00\xec\x06\x07\x09\x1a\x17\x10\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0d\x1a\x01\x11\x00\x00\x00\xec\x06\x07\x0e\x1a\x02\x12\x00\x00\x00\xec\x06\x07\x0f\x1a\x03\x12\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x12\x1a\x20\x11\x00\x00\x00\xec\x06\x07\x14\x1a\x22\x12\x00\x00\x00\xec\x06\x07\x13\x1a\x21\x12\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0c\x1a\x04\x11\x00\x00\x00\xec\x06\x07\x0d\x1a\x05\x12\x00\x00\x00\xec\x06\x07\x0e\x1a\x06"
    #r=RadarReport01B2(data)

    #data = b"\x01\xb2"

    print(RawSpokeData.size)
    print(RawSectorData.size)
    print(RawSectorData.size // RawSpokeData.size)