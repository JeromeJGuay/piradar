"""
Other reports:
    0xc403: RadarReport_c403
    0xc409: RadarReport_c409
    0xc40a: RadarReport_c40a
    0xc611: RadarReport_c611-> heartbeat ? According to CPP
"""
import struct

class RawScanline:
    format = "BBHHHHHHII512s"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.headerLen = unpacked_data[0]
        self.status = unpacked_data[1]
        self.scan_number = unpacked_data[2]
        self.u00 = unpacked_data[3]
        self.large_range = unpacked_data[4]
        self.angle = unpacked_data[5]
        self.heading = unpacked_data[6]
        self.small_range = unpacked_data[7]
        self.rotation = unpacked_data[8]
        self.u02 = unpacked_data[9]
        self.u03 = unpacked_data[10]
        self.data = unpacked_data[11]

class RawSector:
    format = "5sBH" + RawScanline.format * 120

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.stuff = unpacked_data[0]
        self.scanline_count = unpacked_data[1]
        self.scanline_size = unpacked_data[2]
        self.lines = [RawScanline(data[3 + i*struct.calcsize(RawScanline.format): 3 + (i+1)*struct.calcsize(RawScanline.format)]) for i in range(120)]

class IPAddress:
    format = "IH"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.address = unpacked_data[0]
        self.port = unpacked_data[1]


class RadarReport_b201:
    format = "H16s" + "IH12s" * 16

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.id = unpacked_data[0]
        self.serialno = unpacked_data[1].decode('ascii').strip('\x00')
        self.addr0 = IPAddress(data[2:10])
        self.addr1 = IPAddress(data[22:30])
        self.addr2 = IPAddress(data[36:44])
        self.addr3 = IPAddress(data[56:64])
        self.addr4 = IPAddress(data[70:78])
        self.addrDataA = IPAddress(data[84:92])
        self.addrSendA = IPAddress(data[98:106])
        self.addrReportA = IPAddress(data[112:120])
        self.addrDataB = IPAddress(data[126:134])
        self.addrSendB = IPAddress(data[140:148])
        self.addrReportB = IPAddress(data[154:162])
        self.addr11 = IPAddress(data[168:176])
        self.addr12 = IPAddress(data[182:190])
        self.addr13 = IPAddress(data[196:204])
        self.addr14 = IPAddress(data[210:218])
        self.addr15 = IPAddress(data[224:232])
        self.addr16 = IPAddress(data[238:246])

class RadarReport_c402:
    format = "HIB3sB3sBIB11sB3sB"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.id = unpacked_data[0]
        self.range = unpacked_data[1]
        self.skip1 = unpacked_data[2]
        self.mode = unpacked_data[3]
        self.gain_auto = unpacked_data[4]
        self.skip2 = unpacked_data[5]
        self.gain = unpacked_data[6]
        self.sea_clutter_auto = unpacked_data[7]
        self.skip3 = unpacked_data[8]
        self.sea_clutter = unpacked_data[9]
        self.skip4 = unpacked_data[10]
        self.rain_clutter = unpacked_data[11]
        self.skip5 = unpacked_data[12]
        self.interference_rejection = unpacked_data[13]
        self.skip6 = unpacked_data[14]
        self.target_expansion = unpacked_data[15]

class RadarReport_c404:
    format = "BBIHHH7sB"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.what = unpacked_data[0]
        self.command = unpacked_data[1]
        self.field2 = unpacked_data[2]
        self.bearing_alignment = unpacked_data[3]
        self.field8 = unpacked_data[4]
        self.antenna_height = unpacked_data[5]
        self.unknown = unpacked_data[6]
        self.lights = unpacked_data[7]

class RadarReport_c408:
    format = "BBBBBBBBBBBBBBBBBBBB"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
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
        self.target_separation = unpacked_data[12]
        self.field11 = unpacked_data[13]
        self.auto_sea_clutter_nudge = unpacked_data[14]
        self.field13 = unpacked_data[15]
        self.field14 = unpacked_data[16]
        self.doppler_state = unpacked_data[17]
        self.doppler_speed = unpacked_data[18]

class HaloHeadingPacket:
    format = "4s4sH26s2s2sQQLL1sH5s"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.marker = unpacked_data[0]
        self.u00 = unpacked_data[1]
        self.counter = unpacked_data[2]
        self.u01 = unpacked_data[3]
        self.u02 = unpacked_data[4]
        self.u03 = unpacked_data[5]
        self.epoch = unpacked_data[6]
        self.u04 = unpacked_data[7]
        self.u05a = unpacked_data[8]
        self.u05b = unpacked_data[9]
        self.u06 = unpacked_data[10]
        self.heading = unpacked_data[11]
        self.u07 = unpacked_data[12]

class HaloMysteryPacket:
    format = "4s4sH26s2s2sQQLL1s1s2s2s2s"

    def __init__(self, data):
        unpacked_data = struct.unpack(self.format, data)
        self.marker = unpacked_data[0]
        self.u00 = unpacked_data[1]
        self.counter = unpacked_data[2]
        self.u01 = unpacked_data[3]
        self.u02 = unpacked_data[4]
        self.u03 = unpacked_data[5]
        self.epoch = unpacked_data[6]
        self.u04 = unpacked_data[7]
        self.u05a = unpacked_data[8]
        self.u05b = unpacked_data[9]
        self.u06 = unpacked_data[10]
        self.u07 = unpacked_data[11]
        self.mystery1 = unpacked_data[12]
        self.mystery2 = unpacked_data[13]
        self.u08 = unpacked_data[14]