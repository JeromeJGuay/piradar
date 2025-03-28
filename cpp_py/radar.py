import struct
import socket
import threading
import time

from piradar.navico import ip_address_to_string

class Radar:
    def __init__(self, addresses):
        self.m_addresses = addresses
        self.m_exit_flag = False
        self.m_state = {}
        self.report_data = []  # Add this attribute to store report data
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
        # Implementation of send_command
        pass

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
        data_socket = self.create_listener_socket(self.m_addresses.interface_addr, self.m_addresses.data.address, self.m_addresses.data.port)
        while not self.m_exit_flag:
            try:
                in_data, from_addr = data_socket.recvfrom(65535)
                sector = struct.unpack('!HHIHHHHIIBB', in_data[:struct.calcsize('!HHIHHHHIIBB')])
                scanlines = []
                for i in range(sector[6]):
                    scanline = struct.unpack('!HHH', in_data[struct.calcsize('!HHIHHHHIIBB') + i * struct.calcsize('!HHH'):struct.calcsize('!HHIHHHHIIBB') + (i + 1) * struct.calcsize('!HHH')])
                    scanlines.append(scanline)
                self.process_data(scanlines)
            except socket.timeout:
                continue
        data_socket.close()

    def process_data(self, scanlines):
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
        print(processed_data)

    def report_thread(self):
        report_socket = self.create_listener_socket(self.m_addresses.interface_addr, self.m_addresses.report.address, self.m_addresses.report.port)
        while not self.m_exit_flag:
            try:
                in_data = report_socket.recv(65535)
                report = struct.unpack('!HHIHHHHIIBB', in_data[:struct.calcsize('!HHIHHHHIIBB')])
                self.process_report(report)
            except socket.timeout:
                continue
        report_socket.close()

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
            self.report_data.append(new_state)  # Store the report data

    def create_listener_socket(self, interface, mcast_address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind(('', port))
        mreq = struct.pack('4sl', socket.inet_aton(ip_address_to_string(mcast_address)), socket.inet_aton(ip_address_to_string(interface)))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return sock


if __name__ == "__main__":
    # from piradar.navico.network import get_local_addresses, scan_for_radar
    r=Radar('169.254.23.242')