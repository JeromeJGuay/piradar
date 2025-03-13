import struct

class HaloHeadingPacket:
    cformat = '4s 4B 2B 26B 2B 2B Q Q 4B 4B B 2B 5B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.marker = unpacked_data[0]
        self.u00 = unpacked_data[1:5]
        self.counter = struct.unpack('>H', bytes(unpacked_data[5:7]))[0]
        self.u01 = unpacked_data[7:33]
        self.u02 = unpacked_data[33:35]
        self.u03 = unpacked_data[35:37]
        self.epoch = unpacked_data[37]
        self.u04 = unpacked_data[38]
        self.u05a = unpacked_data[39:43]
        self.u05b = unpacked_data[43:47]
        self.u06 = unpacked_data[47]
        self.heading = struct.unpack('>H', bytes(unpacked_data[48:50]))[0]
        self.u07 = unpacked_data[50:55]

class HaloMysteryPacket:
    cformat = '4s 4B 2B 26B 2B 2B Q Q 4B 4B B B 2B 2B 2B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.marker = unpacked_data[0]
        self.u00 = unpacked_data[1:5]
        self.counter = struct.unpack('>H', bytes(unpacked_data[5:7]))[0]
        self.u01 = unpacked_data[7:33]
        self.u02 = unpacked_data[33:35]
        self.u03 = unpacked_data[35:37]
        self.epoch = unpacked_data[37]
        self.u04 = unpacked_data[38]
        self.u05a = unpacked_data[39:43]
        self.u05b = unpacked_data[43:47]
        self.u06 = unpacked_data[47]
        self.u07 = unpacked_data[48]
        self.mystery1 = struct.unpack('>H', bytes(unpacked_data[49:51]))[0]
        self.mystery2 = struct.unpack('>H', bytes(unpacked_data[51:53]))[0]
        self.u08 = unpacked_data[53:55]

class RadarReport01C418:
    cformat = 'B B B B B B H H H'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.radar_status = unpacked_data[2]
        self.field3 = unpacked_data[3]
        self.field4 = unpacked_data[4]
        self.field5 = unpacked_data[5]
        self.field6 = unpacked_data[6]
        self.field8 = unpacked_data[7]
        self.field10 = unpacked_data[8]

class RadarReport02C499:
    cformat = 'B B I B B I B B B B I B B B B H I B B B B I I B B B B B B B B B B B B B B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.range = unpacked_data[2]
        self.field4 = unpacked_data[3]
        self.mode = unpacked_data[4]
        self.field8 = unpacked_data[5]
        self.gain = unpacked_data[6]
        self.sea_auto = unpacked_data[7]
        self.field14 = unpacked_data[8]
        self.field15 = unpacked_data[9]
        self.sea = unpacked_data[10]
        self.field21 = unpacked_data[11]
        self.rain = unpacked_data[12]
        self.field23 = unpacked_data[13]
        self.field24 = unpacked_data[14]
        self.field28 = unpacked_data[15]
        self.field32 = unpacked_data[16]
        self.field33 = unpacked_data[17]
        self.interference_rejection = unpacked_data[18]
        self.field35 = unpacked_data[19]
        self.field36 = unpacked_data[20]
        self.field37 = unpacked_data[21]
        self.target_expansion = unpacked_data[22]
        self.field39 = unpacked_data[23]
        self.field40 = unpacked_data[24]
        self.field41 = unpacked_data[25]
        self.target_boost = unpacked_data[26]

class RadarReport03C4129:
    cformat = 'B B B 31B I 20B 16H 16H 7B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.radar_type = unpacked_data[2]
        self.u00 = unpacked_data[3:34]
        self.hours = unpacked_data[34]
        self.u01 = unpacked_data[35:55]
        self.firmware_date = unpacked_data[55:71]
        self.firmware_time = unpacked_data[71:87]
        self.u02 = unpacked_data[87:94]

class RadarReport04C466:
    cformat = 'B B I H H H I 3B B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.field2 = unpacked_data[2]
        self.bearing_alignment = unpacked_data[3]
        self.field8 = unpacked_data[4]
        self.antenna_height = unpacked_data[5]
        self.field12 = unpacked_data[6]
        self.field16 = unpacked_data[7:10]
        self.accent_light = unpacked_data[10]


class RadarReport06C468:
    cformat = 'B B I 6s 24B 4H 12B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.field1 = unpacked_data[2]
        self.name = unpacked_data[3]
        self.field2 = unpacked_data[4:28]
        self.blanking = [unpacked_data[28:31], unpacked_data[31:34], unpacked_data[34:37], unpacked_data[37:40]]
        self.field3 = unpacked_data[40:52]

class RadarReport06C474:
    cformat = 'B B I 6s 30B 4H 12B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.field1 = unpacked_data[2]
        self.name = unpacked_data[3]
        self.field2 = unpacked_data[4:34]
        self.blanking = [unpacked_data[34:37], unpacked_data[37:40], unpacked_data[40:43], unpacked_data[43:46]]
        self.field4 = unpacked_data[46:58]

class RadarReport08C418:
    cformat = 'B B B B B B B B B B H B B B b B'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.sea_state = unpacked_data[2]
        self.local_interference_rejection = unpacked_data[3]
        self.scan_speed = unpacked_data[4]
        self.sls_auto = unpacked_data[5]
        self.field6 = unpacked_data[6]
        self.field7 = unpacked_data[7]
        self.field8 = unpacked_data[8]
        self.side_lobe_suppression = unpacked_data[9]
        self.field10 = unpacked_data[10]
        self.noise_rejection = unpacked_data[11]
        self.target_sep = unpacked_data[12]
        self.sea_clutter = unpacked_data[13]
        self.auto_sea_clutter = unpacked_data[14]
        self.field13 = unpacked_data[15]
        self.field14 = unpacked_data[16]

class RadarReport08C421:
    cformat = 'B B B B B B B B B B H B B B b B B H'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.old = RadarReport08C418(data[:18])
        self.doppler_state = unpacked_data[18]
        self.doppler_speed = unpacked_data[19]

class RadarReport12C466:
    cformat = 'B B 12s'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.serialno = unpacked_data[2].decode()

class RadarReport01B2:
    cformat = '16s 18B 6s 4B 6s 10B 6s 4B 6s 10B 6s 4B 6s 4B 6s 10B 6s 10B 6s'
    size = struct.calcsize(cformat)

    def __init__(self, data):
        unpacked_data = struct.unpack(self.cformat, data)
        self.serialno = unpacked_data[0].decode()
        self.u1 = unpacked_data[1:19]
        self.addr1 = unpacked_data[19]
        self.u2 = unpacked_data[20:24]
        self.addr2 = unpacked_data[24]
        self.u3 = unpacked_data[25:35]
        self.addr3 = unpacked_data[35]
        self.u4 = unpacked_data[36:40]
        self.addr4 = unpacked_data[40]
        self.u5 = unpacked_data[41:51]
        self.addr5 = unpacked_data[51]
        self.u6 = unpacked_data[52:56]
        self.addr6 = unpacked_data[56]
        self.u7 = unpacked_data[57:61]
        self.addr7 = unpacked_data[61]
        self.u8 = unpacked_data[62:72]
        self.addr8 = unpacked_data[72]
        self.u9 = unpacked_data[73:77]
        self.addr9 = unpacked_data[77]
        self.u10 = unpacked_data[78:82]
        self.addr10 = unpacked_data[82]
        self.u11 = unpacked_data[83:93]
        self.addr11 = unpacked_data[93]
        self.u12 = unpacked_data[94:98]
        self.addr12 = unpacked_data[98]
        self.u13 = unpacked_data[99:103]
        self.addr13 = unpacked_data[103]
        self.u14 = unpacked_data[104:114]
        self.addr14 = unpacked_data[114]
        self.u15 = unpacked_data[115:125]
        self.addr15 = unpacked_data[125]
        self.u16 = unpacked_data[126:136]
        self.addr16 = unpacked_data[136]

# Example usage
data = b'\x01\xC4\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'

print(RadarReport01C418.size, len(data))
radar_report_01c4_18 = RadarReport01C418(data)
print(radar_report_01c4_18.radar_status)