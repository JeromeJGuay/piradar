import datetime
import struct
import numpy as np


FRAME_DELIMITER = b"FH"
FRAME_HEADER_FORMAT = "<LBHHH"
FRAME_HEADER_SIZE = struct.calcsize(FRAME_HEADER_FORMAT) #11

SPOKE_DATA_DELIMITER = b"SD"
SPOKE_DATA_FORMAT = "<HH512B"
SPOKE_DATA_SIZE = struct.calcsize(SPOKE_DATA_FORMAT)


def load_raw_file(raw_file: str, is4bits: bool):
    frames = []
    with open(raw_file, "rb") as f:
        while f.read(1):
            f.seek(-1, 1)

            if f.read(2) == FRAME_DELIMITER:
                raw_header = f.read(FRAME_HEADER_SIZE)
                try:
                    unpacked_header = struct.unpack(FRAME_HEADER_FORMAT, raw_header)
                    #print("ok")
                except struct.error:
                    print("not ok", f.tell(), len(raw_header), raw_header, raw_file)

                unpacked_frame = {
                    "range": unpacked_header[2],
                    "time": datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime(
                        "%Y-%m-%dT%H:%M:%S"),
                    "spoke_number": [],
                    "raw_azimuth": [],
                    "intensity": []
                }

                if f.read(2) == SPOKE_DATA_DELIMITER:
                    for i in range(32):
                        _raw_spoke = f.read(SPOKE_DATA_SIZE)
                        unpacked_spoke = struct.unpack(SPOKE_DATA_FORMAT, _raw_spoke)

                        unpacked_frame["spoke_number"].append(unpacked_spoke[0])
                        unpacked_frame["raw_azimuth"].append(unpacked_spoke[1])

                        if is4bits:
                            unpacked_frame["intensity"].append(unpack_4bit_gray_scale(unpacked_spoke[2:]))
                        else:
                            unpacked_frame["intensity"].append(unpacked_spoke[2:])

                time = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
                unpacked_frame["time"] = 32 * [time]

                frames.append(unpacked_frame)
            #else:
                #print("mhmmmm")
                #f.seek(-1, 1)

            #frames['time'] = [frames['time']] * len(frames['spoke_number'])

    return frames


def _x_load_raw_file(raw_file: str, is4bits: bool) -> list[dict[int]]:
    """
    Return the unpacked data as a list of unpacked frames.
    """
    frames = []

    with open(raw_file, "rb") as f:
        raw_data = f.read()

    for rf in raw_data.split(FRAME_DELIMITER)[1:]:
        try:
            uf = unpack_raw_frame(raw_frame=rf, is4bits=is4bits)
        except ValueError:
            print(f"Bad frame in {raw_file}")
            continue
        except struct.error:
            print(f"Bad frame in {raw_file}")
            continue

        uf['time'] = [uf['time']] * len(uf['spoke_number'])
        frames.append(uf)

    return frames


def unpack_raw_frame(raw_frame, is4bits=True) -> dict[int]:

    raw_header, raw_spokes = raw_frame.split(SPOKE_DATA_DELIMITER)[:2]

    unpacked_header = struct.unpack(FRAME_HEADER_FORMAT, raw_header)

    unpacked_frame = {
        "range": unpacked_header[2],
        "time": datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S"),
        "spoke_number": [],
        "raw_azimuth": [],
        "intensity": []
    }

    byte_pointer = 0
    while byte_pointer + SPOKE_DATA_SIZE <= len(raw_spokes):
        _raw_spoke = raw_spokes[byte_pointer: byte_pointer + SPOKE_DATA_SIZE]
        unpacked_spoke = struct.unpack(SPOKE_DATA_FORMAT, _raw_spoke)
        byte_pointer += SPOKE_DATA_SIZE

        unpacked_frame["spoke_number"].append(unpacked_spoke[0])
        unpacked_frame["raw_azimuth"].append(unpacked_spoke[1])

        if is4bits:
            unpacked_frame["intensity"].append(unpack_4bit_gray_scale(unpacked_spoke[2:]))
        else:
            unpacked_frame["intensity"].append(unpacked_spoke[2:])

    time = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")

    unpacked_frame["time"] = time

    return unpacked_frame


def unpack_4bit_gray_scale(data: bytes):
    data_4bit = []
    for _bytes in data:
        low_nibble = _bytes & 0x0F
        high_nibble = (_bytes >> 4) & 0x0F

        data_4bit.extend([high_nibble, low_nibble])

    return data_4bit


def compute_radius(range: int | float, is4bits=True) -> np.ndarray:
    return np.linspace(0, range, 1024 if is4bits else 512)


def convert_raw_azimuth(raw_azimuth: np.ndarray):
    return ((2 * np.pi) / 4096) * raw_azimuth