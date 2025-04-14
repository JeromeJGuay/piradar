import time
import random
import struct
import datetime
import numpy as np

FRAME_DELIMITER = b"FH"
FRAME_HEADER = "<LBHHH"

SPOKE_DATA_DELIMITER = b"SD"
SPOKE_DATA_HEADER = "<HH512B"


def unpack_4bit_gray_scale(data):
    data_4bit = []
    for _bytes in data:
        low_nibble = _bytes & 0x0F
        high_nibble = (_bytes >> 4) & 0x0F

        data_4bit.extend([high_nibble, low_nibble])

    return data_4bit


def read_raw(raw_file: str, is4bits: bool) -> tuple[np.array, np.array, np.array, np.array]:
    with open(raw_file, "rb") as f:
        raw_data = f.read()

    timestamp, number_of_spoke, _range, heading, gain, spokes = load_raw_data(raw_data, is4bits=is4bits)

    angle = []
    data = []
    for spoke in spokes:
        angle += spoke[1]
        data += spoke[2]

    n_radial_bin = 1024 if is4bits else 512

    radius = np.linspace(0, _range[0], n_radial_bin)
    azimuth = np.array(angle, dtype=float)
    data = np.array(data, dtype=float)

    return timestamp, azimuth, radius, data


def load_raw_data(raw_data: bytes, is4bits=True):
    """
    spoke_data.angle = _spoke_angle * 360 / 4096  # 0..4096 = 0..360
    """
    timestamp = []
    number_of_spoke = []
    _range = []
    heading = []
    gain = []

    spokes = []

    for rf in raw_data.split(FRAME_DELIMITER)[1:]:
        frame_header = struct.unpack(FRAME_HEADER, rf[:11])  # Size of <lBHHH is 11

        timestamp.append(datetime.datetime.fromtimestamp(frame_header[0], datetime.UTC).strftime("%Y-%M-%dT%H:%M:%S"))
        number_of_spoke.append(frame_header[1])
        _range.append(frame_header[2])
        heading.append(frame_header[3])
        gain.append(frame_header[4])

        spoke_number = []
        angle = []
        intensities = []

        for rs in rf[11:].split(SPOKE_DATA_DELIMITER)[1:-1]:
            _raw_spoke = struct.unpack(SPOKE_DATA_HEADER, rs)

            spoke_number.append(_raw_spoke[0])
            angle.append(_raw_spoke[1] * 360 / 4096)
            if is4bits:
                intensities.append(unpack_4bit_gray_scale(_raw_spoke[2:]))
            else:
                intensities.append(_raw_spoke[2:])

        spokes.append([spoke_number, angle, intensities])

    return timestamp, number_of_spoke, _range, heading, gain, spokes


def generate_raw() -> bytes:
    number_of_spoke = 32
    _range = 24_000
    heading = 0
    gain = 127

    spoke_number = 0
    angle = 0
    raw_data = b""

    for _0 in range(128):
        time = int(datetime.datetime.now(datetime.UTC).timestamp())
        raw_data += b"FH" + struct.pack("<LBHHH", time, number_of_spoke, _range, heading, gain)

        for _1 in range(32):
            intensities = []
            for i in range(512):
                high_nibble = np.random.randint(0, 15)
                low_nibble = np.random.randint(0, 15)
                nibbles = high_nibble << 4 | low_nibble

                intensities.append(nibbles)

            raw_data += b"SD" + struct.pack(
                "<HH512B",
                spoke_number,
                angle,
                *intensities
            )
            spoke_number += 1
            angle += 1

    return raw_data



if __name__ == "__main__":
    from pathlib import Path

    import matplotlib as mpl

    mpl.use('Qt5Agg')
    import matplotlib.pyplot as plt

    #raw_data = generate_raw()

    path = "E:\\data"
    # files = list(Path(path).glob("*.raw"))

    # ppi_animated(raw_dir=path)

    # timestamp, azimuth, radius, data = read_raw(files[2], is4bits=True)

    # ppi_scatter(azimuth, radius, data)

    # ppi_contourf(azimuth, radius, data)


