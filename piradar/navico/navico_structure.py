from itertools import accumulate
import struct
import socket

class HaloHeadingPacket:
    cformat = '4s 4B 2B 26B 2B 2B Q Q 4B 4B B 2B 5B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.marker = unpacked_fields[0]
        self.u00 = unpacked_fields[1:5]
        self.counter = struct.unpack('>H', bytes(unpacked_fields[5:7]))[0]
        self.u01 = unpacked_fields[7:33]
        self.u02 = unpacked_fields[33:35]
        self.u03 = unpacked_fields[35:37]
        self.epoch = unpacked_fields[37]
        self.u04 = unpacked_fields[38]
        self.u05a = unpacked_fields[39:43]
        self.u05b = unpacked_fields[43:47]
        self.u06 = unpacked_fields[47]
        self.heading = struct.unpack('>H', bytes(unpacked_fields[48:50]))[0]
        self.u07 = unpacked_fields[50:55]

class HaloMysteryPacket:
    cformat = '4s 4B 2B 26B 2B 2B Q Q 4B 4B B B 2B 2B 2B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.marker = unpacked_fields[0]
        self.u00 = unpacked_fields[1:5]
        self.counter = struct.unpack('>H', bytes(unpacked_fields[5:7]))[0]
        self.u01 = unpacked_fields[7:33]
        self.u02 = unpacked_fields[33:35]
        self.u03 = unpacked_fields[35:37]
        self.epoch = unpacked_fields[37]
        self.u04 = unpacked_fields[38]
        self.u05a = unpacked_fields[39:43]
        self.u05b = unpacked_fields[43:47]
        self.u06 = unpacked_fields[47]
        self.u07 = unpacked_fields[48]
        self.mystery1 = struct.unpack('>H', bytes(unpacked_fields[49:51]))[0]
        self.mystery2 = struct.unpack('>H', bytes(unpacked_fields[51:53]))[0]
        self.u08 = unpacked_fields[53:55]

class RadarReport01C418:
    cformat = 'B B B B B B H H H'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.radar_status = unpacked_fields[2]
        self.field3 = unpacked_fields[3]
        self.field4 = unpacked_fields[4]
        self.field5 = unpacked_fields[5]
        self.field6 = unpacked_fields[6]
        self.field8 = unpacked_fields[7]
        self.field10 = unpacked_fields[8]

class RadarReport02C499:
    cformat = 'B B I B B I B B B B I B B B B H I B B B B I I B B B B B B B B B B B B B B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.range = unpacked_fields[2]
        self.field4 = unpacked_fields[3]
        self.mode = unpacked_fields[4]
        self.field8 = unpacked_fields[5]
        self.gain = unpacked_fields[6]
        self.sea_auto = unpacked_fields[7]
        self.field14 = unpacked_fields[8]
        self.field15 = unpacked_fields[9]
        self.sea = unpacked_fields[10]
        self.field21 = unpacked_fields[11]
        self.rain = unpacked_fields[12]
        self.field23 = unpacked_fields[13]
        self.field24 = unpacked_fields[14]
        self.field28 = unpacked_fields[15]
        self.field32 = unpacked_fields[16]
        self.field33 = unpacked_fields[17]
        self.interference_rejection = unpacked_fields[18]
        self.field35 = unpacked_fields[19]
        self.field36 = unpacked_fields[20]
        self.field37 = unpacked_fields[21]
        self.target_expansion = unpacked_fields[22]
        self.field39 = unpacked_fields[23]
        self.field40 = unpacked_fields[24]
        self.field41 = unpacked_fields[25]
        self.target_boost = unpacked_fields[26]

class RadarReport03C4129:
    cformat = 'B B B 31B I 20B 16H 16H 7B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.radar_type = unpacked_fields[2]
        self.u00 = unpacked_fields[3:34]
        self.hours = unpacked_fields[34]
        self.u01 = unpacked_fields[35:55]
        self.firmware_date = unpacked_fields[55:71]
        self.firmware_time = unpacked_fields[71:87]
        self.u02 = unpacked_fields[87:94]

class RadarReport04C466:
    cformat = 'B B I H H H I 3B B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.field2 = unpacked_fields[2]
        self.bearing_alignment = unpacked_fields[3]
        self.field8 = unpacked_fields[4]
        self.antenna_height = unpacked_fields[5]
        self.field12 = unpacked_fields[6]
        self.field16 = unpacked_fields[7:10]
        self.accent_light = unpacked_fields[10]


class RadarReport06C468:
    cformat = 'B B I 6s 24B 4H 12B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.field1 = unpacked_fields[2]
        self.name = unpacked_fields[3]
        self.field2 = unpacked_fields[4:28]
        self.blanking = [unpacked_fields[28:31], unpacked_fields[31:34], unpacked_fields[34:37], unpacked_fields[37:40]]
        self.field3 = unpacked_fields[40:52]

class RadarReport06C474:
    cformat = 'B B I 6s 30B 4H 12B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.field1 = unpacked_fields[2]
        self.name = unpacked_fields[3]
        self.field2 = unpacked_fields[4:34]
        self.blanking = [unpacked_fields[34:37], unpacked_fields[37:40], unpacked_fields[40:43], unpacked_fields[43:46]]
        self.field4 = unpacked_fields[46:58]

class RadarReport08C418:
    cformat = 'B B B B B B B B B B H B B B b B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.sea_state = unpacked_fields[2]
        self.local_interference_rejection = unpacked_fields[3]
        self.scan_speed = unpacked_fields[4]
        self.sls_auto = unpacked_fields[5]
        self.field6 = unpacked_fields[6]
        self.field7 = unpacked_fields[7]
        self.field8 = unpacked_fields[8]
        self.side_lobe_suppression = unpacked_fields[9]
        self.field10 = unpacked_fields[10]
        self.noise_rejection = unpacked_fields[11]
        self.target_sep = unpacked_fields[12]
        self.sea_clutter = unpacked_fields[13]
        self.auto_sea_clutter = unpacked_fields[14]
        self.field13 = unpacked_fields[15]
        self.field14 = unpacked_fields[16]

class RadarReport08C421:
    cformat = 'B B B B B B B B B B H B B B b B B H'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.old = RadarReport08C418(data[:18])
        self.doppler_state = unpacked_fields[18]
        self.doppler_speed = unpacked_fields[19]

class RadarReport12C466:
    cformat = 'B B 12s'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_fields = struct.unpack(self.cformat, data)
        self.what = unpacked_fields[0]
        self.command = unpacked_fields[1]
        self.serialno = unpacked_fields[2].decode()


class IPAddress:
    def __init__(self, data: tuple[int, int]):
        self.address = socket.inet_ntoa(struct.pack('!I', data[0]))
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
        self.addr5 = IPAddress(unpacked_fields[12])
        self.u6 = unpacked_fields[13]
        self.addr6 = IPAddress(unpacked_fields[14])
        self.u7 = unpacked_fields[15]
        self.addr7 = IPAddress(unpacked_fields[16])
        self.u8 = unpacked_fields[17]
        self.addr8 = IPAddress(unpacked_fields[18])
        self.u9 = unpacked_fields[19]
        self.addr9 = IPAddress(unpacked_fields[20])
        self.u10 = unpacked_fields[21]
        self.addr10 = IPAddress(unpacked_fields[22])
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

        # self.id = unpacked_fields[0]
        # self.serialno = unpacked_fields[1]
        # self.addr0 = unpacked_fields[2]
        # self.u1 = unpacked_fields[3]
        # self.addr1 = unpacked_fields[4]
        # self.u2 = unpacked_fields[5]
        # self.addr2 = unpacked_fields[6]
        # self.u3 = unpacked_fields[7]
        # self.addr3 = unpacked_fields[8]
        # self.u4 = unpacked_fields[9]
        # self.addr4 = unpacked_fields[10]
        # self.u5 = unpacked_fields[11]
        # self.addr5 = unpacked_fields[12]
        # self.u6 = unpacked_fields[13]
        # self.addr6 = unpacked_fields[14]
        # self.u7 = unpacked_fields[15]
        # self.addr7 = unpacked_fields[16]
        # self.u8 = unpacked_fields[17]
        # self.addr8 = unpacked_fields[18]
        # self.u9 = unpacked_fields[19]
        # self.addr9 = unpacked_fields[20]
        # self.u10 = unpacked_fields[21]
        # self.addr10 = unpacked_fields[22]
        # self.u11 = unpacked_fields[23]
        # self.addr11 = unpacked_fields[24]
        # self.u12 = unpacked_fields[25]
        # self.addr12 = unpacked_fields[26]
        # self.u13 = unpacked_fields[27]
        # self.addr13 = unpacked_fields[28]
        # self.u14 = unpacked_fields[29]
        # self.addr14 = unpacked_fields[30]
        # self.u15 = unpacked_fields[31]
        # self.addr15 = unpacked_fields[32]
        # self.u16 = unpacked_fields[33]
        # self.addr16 = unpacked_fields[34]


    def __repr__(self):
        _repr = f"{self.__class__.__name__}\n"
        for key, value in self.__dict__.items():
            _repr += f"{key}: {value}\n"
        return _repr



# Example usage
a=[0x1, 0xb2, 0x31, 0x36, 0x31, 0x31, 0x34, 0x30, 0x31, 0x38, 0x38, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xc0, 0xa8, 0x1, 0xb9, 0x1, 0x1, 0x6, 0x0, 0xfd, 0xff, 0x20, 0x1, 0x2, 0x0, 0x10, 0x0, 0x0, 0x0, 0xc0, 0xa8, 0x1, 0xb9, 0x17, 0x60, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x16, 0x1a, 0x26, 0x1f, 0x0, 0x20, 0x1, 0x2, 0x0, 0x10, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x17, 0x1a, 0x1c, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x18, 0x1a, 0x1d, 0x10, 0x0, 0x20, 0x1, 0x3, 0x0, 0x10, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x8, 0x1a, 0x16, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xa, 0x1a, 0x18, 0x12, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x9, 0x1a, 0x17, 0x10, 0x0, 0x20, 0x2, 0x3, 0x0, 0x10, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xd, 0x1a, 0x1, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xe, 0x1a, 0x2, 0x12, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xf, 0x1a, 0x3, 0x12, 0x0, 0x20, 0x1, 0x3, 0x0, 0x10, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x12, 0x1a, 0x20, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x14, 0x1a, 0x22, 0x12, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0x13, 0x1a, 0x21, 0x12, 0x0, 0x20, 0x2, 0x3, 0x0, 0x10, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xc, 0x1a, 0x4, 0x11, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xd, 0x1a, 0x5, 0x12, 0x0, 0x0, 0x0, 0xec, 0x6, 0x7, 0xe, 0x1a, 0x6]
data=b"\x01\xb2\x31\x36\x31\x31\x34\x30\x31\x38\x38\x30\x00\x00\x00\x00\x00\x00\xc0\xa8\x01\xb9\x01\x01\x06\x00\xfd\xff\x20\x01\x02\x00\x10\x00\x00\x00\xc0\xa8\x01\xb9\x17\x60\x11\x00\x00\x00\xec\x06\x07\x16\x1a\x26\x1f\x00\x20\x01\x02\x00\x10\x00\x00\x00\xec\x06\x07\x17\x1a\x1c\x11\x00\x00\x00\xec\x06\x07\x18\x1a\x1d\x10\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x08\x1a\x16\x11\x00\x00\x00\xec\x06\x07\x0a\x1a\x18\x12\x00\x00\x00\xec\x06\x07\x09\x1a\x17\x10\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0d\x1a\x01\x11\x00\x00\x00\xec\x06\x07\x0e\x1a\x02\x12\x00\x00\x00\xec\x06\x07\x0f\x1a\x03\x12\x00\x20\x01\x03\x00\x10\x00\x00\x00\xec\x06\x07\x12\x1a\x20\x11\x00\x00\x00\xec\x06\x07\x14\x1a\x22\x12\x00\x00\x00\xec\x06\x07\x13\x1a\x21\x12\x00\x20\x02\x03\x00\x10\x00\x00\x00\xec\x06\x07\x0c\x1a\x04\x11\x00\x00\x00\xec\x06\x07\x0d\x1a\x05\x12\x00\x00\x00\xec\x06\x07\x0e\x1a\x06"
print(RadarReport01B2.size)
#raport = RadarReport01B2(data[:144])
#ONLY VALID FORMAT TO UNPACK B201

# endian = "!"
# cformats = ['H', '16s', 'LH', '12B', 'LH', '4B',
#             'LH', '10B', 'LH', '4B', 'LH', '10B',
#             'LH', '4B', 'LH', '4B', 'LH', '10B',
#             'LH', '4B', 'LH', '4B', 'LH', '10B',
#             'LH', '4B', 'LH', '4B', 'LH', '10B',
#             'LH', '4B', 'LH', '4B', 'LH']
#
# size = struct.calcsize(endian + "".join(cformats))
# field_sizes = [struct.calcsize(f) for f in cformats]
# field_offsets = [0] + list(accumulate(field_sizes))[:-1]
#
# for i in range(len(field_sizes)):
#     print(struct.unpack_from(endian + cformats[i], data, offset=field_offsets[i]))

report = RadarReport01B2(data)
# unpacked_fields = struct.unpack("!" + RadarReport01B2.cformat, data)
#
#
# import socket
# for i in range(len(unpacked_fields)):
#     if isinstance(unpacked_fields[i], int) and unpacked_fields[i] > 1e5:
#         print(socket.inet_ntoa(struct.pack('!I', unpacked_fields[i])), unpacked_fields[i+1])