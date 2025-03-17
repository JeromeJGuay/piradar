from itertools import accumulate
import struct
import socket



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
    endian = "!"
    cformats = ['H', '16s', 'LH', '12B', 'LH', '4B',
                'LH', '10B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH', '10B',
                'LH', '4B', 'LH', '4B', 'LH']

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]
    id = 0x01b2
    def __init__(self, data):
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]

        self.id = unpacked_fields[0]
        self.serialno = unpacked_fields[1]
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
    endian = "!"
    cformats = ["B", "B", "B", "B", "B", "B", "H", "H", "H"]

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]
    id = 0x01c4
    def __init__(self, data):
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.radar_status = unpacked_fields[2]
        self.field3 = unpacked_fields[3]
        self.field4 = unpacked_fields[4]
        self.field5 = unpacked_fields[5]
        self.field6 = unpacked_fields[6]
        self.field8 = unpacked_fields[7]
        self.field10 = unpacked_fields[7]


class RadarReport02C499:
    endian = "!"
    cformats = [] #TODO
    id = 0x02c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t what;                    // 0   0x02
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
        """
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO


class RadarReport03C4129:
    endian = "!"
    cformats = [] #TODO
    id = 0x03c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t what;
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
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO

class RadarReport04C466:
    endian = "!"
    cformats = [] #TODO
    id = 0x04c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
          uint8_t what;                // 0   0x04
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
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
    #TODO


# struct SectorBlankingReport {
#   uint8_t enabled;
#   uint16_t start_angle;
#   uint16_t end_angle;
# };

class RadarReport06C4:
    id = 0x06c4

class RadarReport06C468:
    endian = "!"
    cformats = [] #TODO
    id = 0x06c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t what;                      // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[24];                // 12-35 unknown
        SectorBlankingReport blanking[4];  // 36-55
        uint8_t field3[12];                // 56-67
        """
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        #TODO


class RadarReport06C474:
    endian = "!"
    cformats = [] #TODO
    id = 0x06c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t what;                      // 0   0x04
        uint8_t command;                   // 1   0xC4
        uint32_t field1;                   // 2-5
        char name[6];                      // 6-11 "Halo;\0"
        uint8_t field2[30];                // 12-41 unknown
        SectorBlankingReport blanking[4];  // 42-61
        uint8_t field4[12];                // 62-73
        """
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        #TODO


class RadarReport08C4:
    id = 0x08c4


class RadarReport08C418:
    endian = "!"
    cformats = [] #TODO
    id = 0x09c4

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        uint8_t what;                          // 0  0x08
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
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO

class RadarReport08C421:
    endian = "!"
    cformats = [] #TODO

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        RadarReport_08C4_18 old; # same a 08C418 here
        uint8_t doppler_state;
        uint16_t doppler_speed;
        """
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO

class RadarReport12C466:
    endian = "!"
    cformats = [] #TODO

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
    field_offsets = [0] + list(accumulate(field_sizes))[:-1]

    def __init__(self, data):
        """
        // Device Serial number is sent once upon network initialization only
        uint8_t what;          // 0   0x12
        uint8_t command;       // 1   0xC4
        uint8_t serialno[12];  // 2-13 Device serial number at 3G (All?)
        """
        unpacked_fields = [
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]
        # TODO

class HaloHeadingPacket:
    endian = "!"
    cformats = [] #TODO

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
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
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ] #TODO

class HaloMysteryPacket:
    endian = "!"
    cformats = [] #TODO

    size = struct.calcsize(endian + "".join(cformats))
    field_sizes = [struct.calcsize(f) for f in cformats]
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
            struct.unpack_from(self.endian + ff, buffer=data, offset=fo)
            for ff, fo in zip(self.cformats, self.field_offsets)
        ]



if __name__ == "__main__":
    data=b"\x01\xb2\x31\x36\x31\x31\x34\x30\x31\x38\x38\x30\x00\x00\x00\x00\x00\x00\xc0\xa8\x01\xb9\x01\x01\x06\x00\xfd\xff\x20\x01\x02\x00\x10\x00\x00\x00\xc0\xa8\x01\xb9\x17\x60\x11\x00\x00\x00\xec\x06\x07\x16\x1a\x26\x1f\x00\x20\x01\x02\x00\x10\x00\x00\x00\xec\x06\x07\x17\x1a\x1c\x11\x00\x00\x00\xec\x06\x07\x18\x1a\x1d\x10\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x08\x1a\x16\x11\x00\x00\x00\xec\x06\x07\x0a\x1a\x18\x12\x00\x00\x00\xec\x06\x07\x09\x1a\x17\x10\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0d\x1a\x01\x11\x00\x00\x00\xec\x06\x07\x0e\x1a\x02\x12\x00\x00\x00\xec\x06\x07\x0f\x1a\x03\x12\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x12\x1a\x20\x11\x00\x00\x00\xec\x06\x07\x14\x1a\x22\x12\x00\x00\x00\xec\x06\x07\x13\x1a\x21\x12\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0c\x1a\x04\x11\x00\x00\x00\xec\x06\x07\x0d\x1a\x05\x12\x00\x00\x00\xec\x06\x07\x0e\x1a\x06"
    r=RadarReport01B2(data)