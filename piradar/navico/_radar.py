import psutil

import struct
import socket
import threading
import time


# def valid_interface(i):
#     return i and i.ifa_addr and i.ifa_addr.sa_family == socket.AF_INET and (i.ifa_flags & socket.IFF_UP) > 0 and (i.ifa_flags & socket.IFF_LOOPBACK) == 0 and (i.ifa_flags & socket.IFF_MULTICAST) > 0
#

def get_local_addresses():
    addresses = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                addresses.append(addr.address)
    return addresses

# Example usage
print(get_local_addresses())


def ip_address_to_string(a):
    return socket.inet_ntoa(struct.pack('!I', a))


def ip_address_from_string(a):
    return struct.unpack('!I', socket.inet_aton(a))[0]


class AddressSet:
    def __init__(self, label, data, send, report, interface):
        self.label = label
        self.data = data
        self.send = send
        self.report = report
        self.interface = interface

    def __str__(self):
        return f'{self.label}: data: {ip_address_to_string(self.data.address)}:{self.data.port}, report: {ip_address_to_string(self.report.address)}:{self.report.port}, send: {ip_address_to_string(self.send.address)}:{self.send.port}'


def scan(addresses=None):
    if addresses is None:
        addresses = get_local_addresses()
    ret = []
    for a in addresses:
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.settimeout(1)
        listen_sock.bind(('', 6878))
        mreq = struct.pack('4sl', socket.inet_aton('236.6.7.5'), socket.inet_aton(ip_address_to_string(a)))
        listen_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_sock.bind((ip_address_to_string(a), 0))
        data = struct.pack('!H', 0xb101)
        send_sock.sendto(data, ('236.6.7.5', 6878))
        for _ in range(3):
            try:
                in_data, from_addr = listen_sock.recvfrom(1024)
                if len(in_data) == struct.calcsize('!HHIHHHHIIBB'):
                    b201 = struct.unpack('!HHIHHHHIIBB', in_data)
                    if b201[0] == 0xb201:
                        asa = AddressSet('HaloA', b201[1], b201[2], b201[3], a)
                        ret.append(asa)
                        asb = AddressSet('HaloB', b201[4], b201[5], b201[6], a)
                        ret.append(asb)
            except socket.timeout:
                continue
        listen_sock.close()
        send_sock.close()
        if ret:
            break
    return ret


class Radar:
    def __init__(self, addresses):
        self.m_addresses = addresses
        self.m_exit_flag = False
        self.m_state = {}
        self.m_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.m_send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.m_send_address = ('', 0)
        self.m_send_socket.bind(self.m_send_address)
        self.m_send_address = (self.m_addresses.send.address, self.m_addresses.send.port)
        self.send_heartbeat()
        self.m_data_thread = threading.Thread(target=self.data_thread)
        self.m_report_thread = threading.Thread(target=self.report_thread)
        self.m_data_thread.start()
        self.m_report_thread.start()

    def __del__(self):
        self.m_exit_flag = True
        self.m_data_thread.join()
        self.m_report_thread.join()

    def send_command(self, key, value):
        if key == 'status':
            if value == 'transmit':
                data1 = struct.pack('!HB', 0xc100, 1)
                data2 = struct.pack('!HB', 0xc101, 1)
                self.send_command_raw(data1)
                self.send_command_raw(data2)
            elif value == 'standby':
                data1 = struct.pack('!HB', 0xc100, 1)
                data2 = struct.pack('!HB', 0xc101, 0)
                self.send_command_raw(data1)
                self.send_command_raw(data2)
        elif key == 'range':
            cmd = struct.pack('!HI', 0xc103, int(float(value) * 10))
            self.send_command_raw(cmd)
        elif key == 'bearing_alignment':
            cmd = struct.pack('!HH', 0xc105, int(float(value) * 10))
            self.send_command_raw(cmd)
        elif key == 'gain':
            cmd = struct.pack('!HIBB', 0xc106, 0, 1 if value == 'auto' else 0, int(float(value) * 255 / 100))
            self.send_command_raw(cmd)
        elif key == 'sea_clutter':
            cmd = struct.pack('!HIBB', 0xc106, 2, 1 if value == 'auto' else 0, int(float(value) * 255 / 100))
            self.send_command_raw(cmd)
        elif key == 'rain_clutter':
            cmd = struct.pack('!HIBB', 0xc106, 4, 0, int(float(value) * 255 / 100))
            self.send_command_raw(cmd)
        elif key == 'sidelobe_suppression':
            cmd = struct.pack('!HIBB', 0xc106, 5, 1 if value == 'auto' else 0, int(float(value) * 255 / 100))
            self.send_command_raw(cmd)
        else:
            cmd_map = {'off': 0, 'low': 1, 'medium': 2, 'high': 3}
            if key == 'interference_rejection':
                self.send_command_raw(struct.pack('!HB', 0xc108, cmd_map[value]))
            elif key == 'sea_state':
                self.send_command_raw(struct.pack('!HB', 0xc10b, {'moderate': 1, 'rough': 2}.get(value, 0)))
            elif key == 'scan_speed':
                self.send_command_raw(struct.pack('!HB', 0xc10f, {'medium': 1, 'high': 3}.get(value, 0)))
            elif key == 'mode':
                self.send_command_raw(struct.pack('!HB', 0xc110, {'harbor': 1, 'offshore': 2, 'weather': 4, 'bird': 5}.get(value, 0)))
            elif key == 'auto_sea_clutter_nudge':
                self.send_command_raw(struct.pack('!HBBHB', 0xc111, 1, int(float(value)), int(float(value)), 4))
            elif key == 'target_expansion':
                self.send_command_raw(struct.pack('!HB', 0xc112, cmd_map[value]))
            elif key == 'noise_rejection':
                self.send_command_raw(struct.pack('!HB', 0xc121, cmd_map[value]))
            elif key == 'target_separation':
                self.send_command_raw(struct.pack('!HB', 0xc122, cmd_map[value]))
            elif key == 'doppler_mode':
                self.send_command_raw(struct.pack('!HB', 0xc123, {'normal': 1, 'approaching_only': 2}.get(value, 0)))
            elif key == 'doppler_speed':
                self.send_command_raw(struct.pack('!HH', 0xc124, int(float(value) * 100)))
            elif key == 'antenna_height':
                self.send_command_raw(struct.pack('!HIIB', 0xc130, 1, int(float(value) * 1000), 1))
            elif key == 'lights':
                self.send_command_raw(struct.pack('!HB', 0xc131, cmd_map[value]))

    def send_heartbeat(self):
        self.send_command_raw(struct.pack('!HB', 0xa0c1, 0))
        self.send_command_raw(struct.pack('!HB', 0x03c2, 0))
        self.send_command_raw(struct.pack('!HB', 0x04c2, 0))
        self.send_command_raw(struct.pack('!HB', 0x05c2, 0))
        self.m_last_heartbeat = time.time()

    def check_heartbeat(self):
        if time.time() - self.m_last_heartbeat > 1:
            self.send_heartbeat()
            return True
        return False

    def send_command_raw(self, data):
        self.m_send_socket.sendto(data, self.m_send_address)

    def data_thread(self):
        data_socket = self.create_listener_socket(self.m_addresses.interface, self.m_addresses.data.address, self.m_addresses.data.port)
        while not self.m_exit_flag:
            try:
                in_data = data_socket.recv(65535)
                sector = struct.unpack('!HHIHHHHIIBB', in_data[:struct.calcsize('!HHIHHHHIIBB')])
                scanlines = []
                for i in range(sector[6]):
                    scanline = struct.unpack('!HHH', in_data[struct.calcsize('!HHIHHHHIIBB') + i * struct.calcsize('!HHH'):struct.calcsize('!HHIHHHHIIBB') + (i + 1) * struct.calcsize('!HHH')])
                    scanlines.append(scanline)
                self.process_data(scanlines)
            except socket.timeout:
                continue
        data_socket.close()

    def report_thread(self):
        report_socket = self.create_listener_socket(self.m_addresses.interface, self.m_addresses.report.address, self.m_addresses.report.port)
        while not self.m_exit_flag:
            try:
                in_data = report_socket.recv(65535)
                report = struct.unpack('!HHIHHHHIIBB', in_data[:struct.calcsize('!HHIHHHHIIBB')])
                self.process_report(report)
            except socket.timeout:
                continue
        report_socket.close()

    def create_listener_socket(self, interface, mcast_address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind(('', port))
        mreq = struct.pack('4sl', socket.inet_aton(ip_address_to_string(mcast_address)), socket.inet_aton(ip_address_to_string(interface)))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return sock

    def process_data(self, scanlines):
        # Assuming scanlines is a list of Scanline objects or dictionaries
        processed_data = []
        for scanline in scanlines:
            angle = scanline['angle']
            range = scanline['range']
            intensities = scanline['intensities']
            processed_data.append({
                'angle': angle,
                'range': range,
                'intensities': intensities
            })
        # Save processed_data to file or use it as needed
        print(processed_data)

    def process_report(self, in_data):
        new_state = {}
        id = struct.unpack_from('!H', in_data, 0)[0]

        if id == 0xc401:
            status = in_data[2]
            if status == 1:
                new_state["status"] = "standby"
            elif status == 2:
                new_state["status"] = "transmit"
            elif status == 5:
                new_state["status"] = "spinning_up"
            else:
                new_state["status"] = "unknown"

        elif id == 0xc402:
            if len(in_data) >= struct.calcsize('!HBBHHHH'):
                range_value, mode, gain, gain_auto, sea_clutter, sea_clutter_auto, rain_clutter = struct.unpack_from('!HBBHHHH', in_data, 2)
                new_state["range"] = str(range_value / 10)
                new_state["mode"] = ["custom", "harbor", "offshore", "unknown", "weather", "bird"][mode]
                new_state["gain"] = str(gain * 100 / 255.0)
                new_state["gain_mode"] = "auto" if gain_auto else "manual"
                new_state["sea_clutter"] = str(sea_clutter * 100 / 255.0)
                new_state["sea_clutter_mode"] = "auto" if sea_clutter_auto else "manual"
                new_state["rain_clutter"] = str(rain_clutter * 100 / 255.0)

        # Add other cases here, following the same pattern

        state_updated = False
        for key, value in new_state.items():
            if key not in self.m_state or self.m_state[key] != value:
                self.m_state[key] = value
                state_updated = True

        if state_updated:
            self.state_updated()


class HeadingSender:
    def __init__(self, bind_address):
        self.m_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.m_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.m_send_address = ('239.238.55.73', 7527)
        self.m_socket.bind((ip_address_to_string(bind_address), 0))
        self.m_heading = 0.0
        self.m_exit_flag = False
        self.m_sender_thread = threading.Thread(target=self.sender_thread)
        self.m_sender_thread.start()

    def __del__(self):
        self.m_exit_flag = True
        self.m_sender_thread.join()

    def sender_thread(self):
        while not self.m_exit_flag:
            time.sleep(0.1)
            heading_packet = struct.pack('!4s4sH26s2s2sQ8s8sII1sH5s', b'NKOE', b'\x00\x01\x90\x02', 0, b'\x00' * 26, b'\x12\xf1', b'\x01\x00', int(time.time() * 1000), b'\x00' * 8, b'\x00' * 8, 0, 0, b'\xff', int(self.m_heading * 63488.0 / 360.0), b'\x00' * 5)
            self.m_socket.sendto(heading_packet, self.m_send_address)

    def set_heading(self, heading):
        self.m_heading = heading


if __name__ == '__main__':
    address = get_local_addresses()
    radar = Radar(address)

#    radar.process_report(report_data)
#    radar.process_data(scanlines)
