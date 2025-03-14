import pyshark

class Snooper:

    def __init__(self, interface, address, port):
        self.capture = pyshark.LiveCapture(
            interface=interface,
            bpf_filter=f"dst host {address} and dst port {port}",  # either address or address and port should work
            use_ek=True,
            include_raw=True
        )

    def recv(self):
        return next(self.capture.sniff_continuously(1)).data.data.value


interface = "ethernet 2"
group = ("236.6.7.9", 6679)
snooper = Snooper(interface, group[0], group[1])

for i in range(10):
    print(snooper.recv())



