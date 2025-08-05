from pathlib import Path
import struct
import datetime

import numpy as np
import xarray as xr

FRAME_DELIMITER = b"FH"
FRAME_HEADER_FORMAT = "<LBHHH"
FRAME_HEADER_SIZE = struct.calcsize(FRAME_HEADER_FORMAT) #11

SPOKE_DATA_DELIMITER = b"SD"
SPOKE_DATA_FORMAT = "<HH512B"
SPOKE_DATA_SIZE = struct.calcsize(SPOKE_DATA_FORMAT)


def read_raw(raw_file: str, is4bits: bool, merge=False) -> tuple[np.array, np.array, np.array, np.array]:
    with open(raw_file, "rb") as f:
        raw_data = f.read()

    frames_ds = load_raw_data(raw_data, is4bits=is4bits)

    if merge is True:
        return xr.concat(frames_ds, dim="spoke_number")

    return frames_ds


def load_raw_data(raw_data: bytes, is4bits=True):
    frames = []

    for rf in raw_data.split(FRAME_DELIMITER)[1:]:
        frames.append(load_frame_data(raw_frame=rf, is4bits=is4bits))

    return frames


def load_frame_data(raw_frame: bytes, is4bits=True) -> xr.Dataset:
    """
    spoke_data.angle = _spoke_angle * 360 / 4096  # 0..4096 = 0..360
    """

    raw_header, raw_spokes = raw_frame.split(SPOKE_DATA_DELIMITER)[:2]

    unpacked_header = struct.unpack(FRAME_HEADER_FORMAT, raw_header)

    frame_data = {
        "spoke_number": [],
        "azimuth": [],
        "raw_azimuth": [],
        "radius": np.linspace(0, unpacked_header[2], 1024 if is4bits else 512),
        "intensity": []
    }

    byte_pointer = 0
    while byte_pointer + SPOKE_DATA_SIZE <= len(raw_spokes):
        _raw_spoke = raw_spokes[byte_pointer: byte_pointer + SPOKE_DATA_SIZE]
        unpacked_spoke = struct.unpack(SPOKE_DATA_FORMAT, _raw_spoke)
        byte_pointer += SPOKE_DATA_SIZE

        frame_data["spoke_number"].append(unpacked_spoke[0])
        frame_data["azimuth"].append(unpacked_spoke[1] * 360 / 4096)
        frame_data["raw_azimuth"].append(unpacked_spoke[1])

        if is4bits:
            frame_data["intensity"].append(unpack_4bit_gray_scale(unpacked_spoke[2:]))
        else:
            frame_data["intensity"].append(unpacked_spoke[2:])

    for k in ["spoke_number", "azimuth", "intensity"]:
        frame_data[k] = np.array(frame_data[k])

    time = ["nat"] * frame_data['azimuth'].shape[0]
    time[-1] = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
    time = np.array(time, dtype='datetime64[ns]')

    dataset = xr.Dataset(
        {
            "intensity": (["spoke_number", "radius"], frame_data["intensity"]),
            "time": (["spoke_number"], time),
            "raw_azimuth": (["spoke_number"], frame_data["raw_azimuth"]),


        },
        coords={
            "spoke_number": frame_data["spoke_number"],
            "azimuth": ("spoke_number", np.deg2rad(frame_data["azimuth"])),
            "radius": frame_data["radius"],
        },
        attrs={
            "number_of_spoke": unpacked_header[1],
            "max_range": unpacked_header[2],
            "heading": unpacked_header[3] / 10,
            "gain": unpacked_header[4],
        }
    )

    return dataset


def load_frame_data_2(raw_frame: bytes, is4bits=True) -> xr.Dataset:
    """
    spoke_data.angle = _spoke_angle * 360 / 4096  # 0..4096 = 0..360
    """

    raw_header, raw_spokes = raw_frame.split(SPOKE_DATA_DELIMITER)[:2]

    unpacked_header = struct.unpack(FRAME_HEADER_FORMAT, raw_header)

    frame_data = {
        "spoke_number": [],
        "azimuth": [],
        "raw_azimuth": [],
        "radius": np.linspace(0, unpacked_header[2], 1024 if is4bits else 512),
        "intensity": []
    }

    byte_pointer = 0
    while byte_pointer + SPOKE_DATA_SIZE <= len(raw_spokes):
        _raw_spoke = raw_spokes[byte_pointer: byte_pointer + SPOKE_DATA_SIZE]
        unpacked_spoke = struct.unpack(SPOKE_DATA_FORMAT, _raw_spoke)
        byte_pointer += SPOKE_DATA_SIZE

        frame_data["spoke_number"].append(unpacked_spoke[0])
        frame_data["azimuth"].append(unpacked_spoke[1] * 360 / 4096)
        frame_data["raw_azimuth"].append(unpacked_spoke[1])

        if is4bits:
            frame_data["intensity"].append(unpack_4bit_gray_scale(unpacked_spoke[2:]))
        else:
            frame_data["intensity"].append(unpacked_spoke[2:])

    for k in ["spoke_number", "azimuth", "intensity"]:
        frame_data[k] = np.array(frame_data[k])

    time = ["nat"] * frame_data['azimuth'].shape[0]
    time[-1] = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
    time = np.array(time, dtype='datetime64[ns]')


    frame_data['time'] = time

    return frame_data


def unpack_4bit_gray_scale(data):
    data_4bit = []
    for _bytes in data:
        low_nibble = _bytes & 0x0F
        high_nibble = (_bytes >> 4) & 0x0F

        data_4bit.extend([high_nibble, low_nibble])

    return data_4bit


def get_file_by_scan(path):
    scan_groups = {}
    raw_files = list(Path(path).rglob("*.raw"))
    for rf in raw_files:
        scan_dt = rf.name.split("_")[0]
        if scan_dt in scan_groups:
            scan_groups[scan_dt].append(rf)
        else:
            scan_groups[scan_dt] = [rf]
    return scan_groups


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt

    #data_directory = r"D:\data\20250606\14"
    data_directory = r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\iap_2025-07-16\data\20250606"

    #raw_files = list(Path(data_directory).rglob("*.raw"))

    grouped_raw = get_file_by_scan(data_directory)

    ds_list = []

    #for rf in list(grouped_raw.values())[0]:
    #    ds_list.append(read_raw(rf, is4bits=True, merge=True))
    #ds = xr.concat(ds_list, 'scan')

    rf=list(grouped_raw.values())[0][0]

    ds = read_raw(rf,is4bits=True, merge=True)

    azimuth = ds['azimuth'].values

    _cuts = np.where(np.diff(azimuth) < 0)[0] + 1

