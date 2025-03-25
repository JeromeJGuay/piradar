from itertools import accumulate
import struct

from dataclasses import dataclass, fields, field

__all__ = [
    "REPORTS_IDS",
    "RadarReport01B2",
    "RadarReport01C4",
    "RadarReport02C4",
    "RadarReport03C4",
    "RadarReport04C4",
    "RadarReport06C4",
    "RadarReport08C4",
    "RadarReport12C4",
    "RawSectorData",
    "RawSpokeData",
    # "HaloHeadingPacket",
    # "HaloMysteryPacket",
]

ENDIAN = "<"


@dataclass(frozen=True)
class _ReportIds:
    r_01B2: int = field(default=0x01b2)
    r_01C4: int = field(default=0x01c4)
    r_02C4: int = field(default=0x02c4)
    r_03C4: int = field(default=0x03c4)
    r_04C4: int = field(default=0x04c4)
    # _05C4 = 0x05c4 # Not use (maybe it doesnt not exist)
    r_06C4: int = field(default=0x06c4)
    # _07C4 = 0x07c4 # Not use (maybe it doesnt not exist)
    r_08C4: int = field(default=0x08c4)
    # _09C4 = 0x09c4 # Not use (maybe it doesnt not exist)
    # _10C4 = 0x10c4 # Not use (maybe it doesnt not exist)
    # _11C4 = 0x11c4 # Not use (maybe it doesnt not exist)
    r_12C4: int = field(default=0x12c4)

    def __iter__(self):
        for field in fields(self):
            yield getattr(self, field.name)


# This here is done so that I can also iterate over the field of the _ReportIds class
REPORTS_IDS = _ReportIds()


@dataclass
class IPAddressRaw:
    address: int
    port: int


class RadarReport01B2:
    expected_size = 222
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
        self.serialno = unpacked_fields[1][0].decode("ascii")
        self.addr0 = IPAddressRaw(*unpacked_fields[2])
        self.u1 = unpacked_fields[3]
        self.addr1 = IPAddressRaw(*unpacked_fields[4])
        self.u2 = unpacked_fields[5]
        self.addr2 = IPAddressRaw(*unpacked_fields[6])
        self.u3 = unpacked_fields[7]
        self.addr3 = IPAddressRaw(*unpacked_fields[8])
        self.u4 = unpacked_fields[9]
        self.addr4 = IPAddressRaw(*unpacked_fields[10])
        self.u5 = unpacked_fields[11]
        self.addrDataA = IPAddressRaw(*unpacked_fields[12])
        self.u6 = unpacked_fields[13]
        self.addrSendA = IPAddressRaw(*unpacked_fields[14])
        self.u7 = unpacked_fields[15]
        self.addrReportA = IPAddressRaw(*unpacked_fields[16])
        self.u8 = unpacked_fields[17]
        self.addrDataB = IPAddressRaw(*unpacked_fields[18])
        self.u9 = unpacked_fields[19]
        self.addrSendB = IPAddressRaw(*unpacked_fields[20])
        self.u10 = unpacked_fields[21]
        self.addrReportB = IPAddressRaw(*unpacked_fields[22])
        self.u11 = unpacked_fields[23]
        self.addr11 = IPAddressRaw(*unpacked_fields[24])
        self.u12 = unpacked_fields[25]
        self.addr12 = IPAddressRaw(*unpacked_fields[26])
        self.u13 = unpacked_fields[27]
        self.addr13 = IPAddressRaw(*unpacked_fields[28])
        self.u14 = unpacked_fields[29]
        self.addr14 = IPAddressRaw(*unpacked_fields[30])
        self.u15 = unpacked_fields[31]
        self.addr15 = IPAddressRaw(*unpacked_fields[32])
        self.u16 = unpacked_fields[33]
        self.addr16 = IPAddressRaw(*unpacked_fields[34])

    def __repr__(self):
        _repr = f"{self.__class__.__name__}\n"
        for key, value in self.__dict__.items():
            _repr += f"{key}: {value}\n"
        return _repr


class RadarReport01C4:
    expected_size = 18
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


class RadarReport02C4:
    expected_size = 99 # acutal size is 43 (99 from openCPN radar pi???
    cformats = ["B", "B", "L", "B", "B", "B", "3B", "B", "B", "B", "H", "L", "B", "B", "B", "L", "L",
                "B", "B", "B", "B", "B", "B", "B", "B", "B", "B", "B",
                "56B" # Add if needed to have a size 99. at the moment size is 43
                ]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t register;                // 0   0x02
          uint8_t command;                 // 1 0xC4
          uint32_t range;                  //  2-3   0x06 0x09
          uint8_t field4;                  // 6    0
          uint8_t mode;                    // 7    mode (0 = custom, 1 = harbor, 2 = offshore, 4 = bird, 5 = weather)
          uint8_t gain_auto                // 8
          uint8_t field11[3];              // 9-11
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

          uint8_t field43[56] Added by jérôme
          # NOTE THEIR MIGHT BE MORE FIELDS ?
        """
        if len(data) != self.expected_size: # size is 43 not 99. but it could be for halo ?? maybe idk.
            data = data + (self.size - len(data)) * b"\x00"

        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.range = unpacked_fields[2][0]
        self.field4 = unpacked_fields[3][0]
        self.mode = unpacked_fields[4][0]
        self.auto_gain = unpacked_fields[5][0]
        self.field8 = unpacked_fields[6] #3value
        self.gain = unpacked_fields[7][0]
        self.auto_sea_state = unpacked_fields[8][0]
        self.field14 = unpacked_fields[9][0]
        self.field15 = unpacked_fields[10][0]
        self.sea_clutter = unpacked_fields[11][0]
        self.field21 = unpacked_fields[12][0]
        self.rain_clutter = unpacked_fields[13][0]
        self.field23 = unpacked_fields[14][0]
        self.field24 = unpacked_fields[15][0]
        self.field28 = unpacked_fields[16][0]
        self.field32 = unpacked_fields[17][0]
        self.field33 = unpacked_fields[18][0]
        self.interference_rejection = unpacked_fields[19][0]
        self.field35 = unpacked_fields[20][0]
        self.field36 = unpacked_fields[21][0]
        self.field37 = unpacked_fields[22][0]
        self.target_expansion = unpacked_fields[23][0]
        self.field39 = unpacked_fields[24][0]
        self.field40 = unpacked_fields[25][0]
        self.field41 = unpacked_fields[26][0]
        self.target_boost = unpacked_fields[27][0]

        self.field43 = unpacked_fields[28] # 56


class RadarReport03C4:
    expected_size = 129
    cformats = ["B", "B", "B", "31B", "L", "20B", "32s", "32s", "7B"]

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
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.radar_type = unpacked_fields[2][0]
        self.u00 = unpacked_fields[3] # 31 values
        self.hours = unpacked_fields[4][0]
        self.u01 = unpacked_fields[5] # 20 values
        self.firmware_date = unpacked_fields[6][0].decode("ascii")
        self.firmware_time = unpacked_fields[7][0].decode("ascii")
        self.u02 = unpacked_fields[8] # 7 values


class RadarReport04C4:
    expected_size = 66
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
        self.field16 = unpacked_fields[7]  # 3 values
        self.accent_light = unpacked_fields[8][0]


class SectorBlanking:
    cformat = "B2H"

    def __init__(self, data: tuple[int, int, int]):
        self.enable = data[0]
        self.start_angle = data[1]
        self.end_angle = data[2]


class RadarReport06C4:
    expected_size = 74
    cformats = ["B", "B", "L", "6c", "30B"] + 4 * [SectorBlanking.cformat] + ["12B"]

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        [Report ofsSize 74]
        uint8_t register;                  // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[30];                // 12-41 unknown
        SectorBlankingReport blanking[4];  // 42-61
        uint8_t field4[12];                // 62-73

        [Report ofsSize 68]
        uint8_t register;                  // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[24];                // 12-35 unknown
        SectorBlankingReport blanking[4];  // 36-55
        uint8_t field3[12];                // 56-67
        """

        if len(data) == 68:
            self.cformats = ["B", "B", "L", "6c", "24B"] + 4 * [SectorBlanking.cformat] + ["12B"]

        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.field1 = unpacked_fields[2][0]
        self.name = unpacked_fields[3]  #6 values #myabe use 6s and unpack as ascii ? Fixme
        self.field2 = unpacked_fields[4]  # 26 or 30 values depending on the report size (68 or 74)
        self.blanking = (
            SectorBlanking(unpacked_fields[5]),  # will be unpakced by SectorBlanking
            SectorBlanking(unpacked_fields[6]),
            SectorBlanking(unpacked_fields[7]),
            SectorBlanking(unpacked_fields[8])
        )
        self.field3 = unpacked_fields[9]  # 12 values


class RadarReport08C4:
    expected_size = 21
    cformats = 10 * ["B"] + ["H"] + 6 * ["B"] + ["B", "H"]  #TODO

    size = struct.calcsize(ENDIAN + "".join(cformats))
    field_sizes = [struct.calcsize(ENDIAN + f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        RadarReport_08C4_18 old; # same a 08C418 here
        uint8_t doppler_state;
        uint16_t doppler_speed;
        """
        # Padding to 21 (report could be 18)
        if len(data) != self.expected_size:
            data = data + (self.size - len(data)) * b"\x00"

        unpacked_fields = [
            struct.unpack_from(ENDIAN + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.sea_state = unpacked_fields[2][0]
        self.local_interference_filter = unpacked_fields[3][0]
        self.scan_speed = unpacked_fields[4][0]
        self.auto_side_lobe_suppression = unpacked_fields[5][0]
        self.field6 = unpacked_fields[6][0]
        self.field7 = unpacked_fields[7][0]
        self.field8 = unpacked_fields[8][0]
        self.side_lobe_suppression = unpacked_fields[9][0]
        self.field10 = unpacked_fields[10][0]
        self.noise_rejection = unpacked_fields[11][0]
        self.target_separation = unpacked_fields[12][0]
        self.sea_clutter = unpacked_fields[13][0] # doubt
        self.auto_sea_clutter = unpacked_fields[14][0]
        self.field13 = unpacked_fields[14][0]
        self.field14 = unpacked_fields[15][0]

        self.doppler_mode = unpacked_fields[16][0]
        self.doppler_speed = unpacked_fields[17][0]


class RadarReport12C4:
    expected_size = 66
    cformats = ["B", "B", "12s"]  #TODO

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
        self.register = unpacked_fields[0][0]
        self.command = unpacked_fields[1][0]
        self.serialno = unpacked_fields[2][0].decode("ascii")


class HaloHeadingPacket:
    cformats = []  #TODO

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
        ]  #TODO


class HaloMysteryPacket:
    cformats = []  #TODO

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
    number_of_spokes = 32  # 32. Maybe less ? make it so it can take more or less lines depending on the
    header_cformats = ["5B", "B", "H"]
    cformats = header_cformats + number_of_spokes * ["".join(RawSpokeData.cformats)]

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
        unpacked_header = [
            struct.unpack_from(ENDIAN + ff, buffer=header_data, offset=fo)
            for ff, fo in zip(self.cformats[:len(self.header_cformats)], self.field_offsets)
        ]
        self.stuff = unpacked_header[0][0]
        self.number_of_spokes = unpacked_header[1][0]
        self.scanline_size = unpacked_header[2][0]

        self.number_of_spokes = int((RawSectorData.size - RawSectorData.header_size) / RawSpokeData.size)

        spokes_data = data[self.header_size:]

        self.spokes = [
            RawSpokeData(spokes_data[i * RawSpokeData.size: (i + 1) * RawSpokeData.size]) for i in
            range(self.number_of_spokes)
        ]
