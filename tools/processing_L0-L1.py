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


def load_raw(raw_files: str, is4bits=True):

    frames = []
    for raw_file in raw_files:

        with open(raw_file, "rb") as f:
            raw_data = f.read()

        for rf in raw_data.split(FRAME_DELIMITER)[1:]:
            uf = unpack_raw_frame(raw_frame=rf, is4bits=is4bits)
            uf['time'] = [uf['time']] * len(uf['spoke_number'])
            frames.append(uf)

    data = {
        "range": [],
        "time": [],
        "spoke_number": [],
        "raw_azimuth": [],
        "intensity": []
    }

    for frame in frames:
        data['range'] += data['range']
        data['time'] += frame['time']
        data['spoke_number'] += frame['spoke_number']
        data['raw_azimuth'] += frame['raw_azimuth']
        data['intensity'] += frame['intensity']


    ### Remove data before the first cut in raw_azimuth
    # the radar seems to need to reset its azimuth when first starting to transmit.
    # cut_index = np.where(np.diff(data['raw_azimuth']) < 0)[0] + 1
    # first_cut = cut_index[1]
    # for var in ['time', 'spoke_number', 'raw_azimuth', 'intensity']:
    #     data[var] = data[var][first_cut:]

    return data


def unpack_raw_frame(raw_frame, is4bits=True):

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

    #time = ["nat"] * unpacked_frame['azimuth'].shape[0]
    time = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
    #time = np.array(time, dtype='datetime64[ns]')

    unpacked_frame["time"] = time

    return unpacked_frame


def unpack_4bit_gray_scale(data):
    data_4bit = []
    for _bytes in data:
        low_nibble = _bytes & 0x0F
        high_nibble = (_bytes >> 4) & 0x0F

        data_4bit.extend([high_nibble, low_nibble])

    return data_4bit


def convert_raw_azimuth(raw_azimuth: np.ndarray):
    return ((2 * np.pi) / 4096) * raw_azimuth


def compute_radius(range: int | float, is4bits=True) -> np.ndarray:
    return np.linspace(0, range, 1024 if is4bits else 512)


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


def correct_azimuth_misalignment(spoke_number: list, raw_azimuth: list) -> np.ndarray:

    if not isinstance(spoke_number, np.ndarray):
        spoke_number = np.array(spoke_number)
    if not isinstance(raw_azimuth, np.ndarray):
        raw_azimuth = np.array(raw_azimuth)

    # Step 1: Detect cycle length
    unique_X, counts = np.unique(spoke_number, return_counts=True)

    if np.unique(counts).shape != (1,):
        raise ValueError("Invalid dimensions. Scans don't have the same number of spokes.")

    Nx = counts[0]
    Lx = len(spoke_number) // Nx

    if len(spoke_number) != Nx*Lx:
        raise ValueError("Invalid dimensions. Scans don't have the same number of spokes.")

    # Step 2: Reshape into cycles
    #spoke_number_cycles = spoke_number.reshape(Nx, Lx)
    raw_azimuth_cycles = raw_azimuth.reshape(Nx, Lx)

    # Step 3: Use the most frequent cycle as reference
    #reference_cycle_index = np.argmax([np.sum(raw_azimuth_cycles == raw_azimuth_cycles[i]) for i in range(num_cycles)])
    #reference_Y = raw_azimuth_cycles[reference_cycle_index]

    raw_azimuth_mode = sp.stats.mode(raw_azimuth_cycles, axis=0, keepdims=False).mode

    return np.tile(raw_azimuth_mode, Nx).flatten()
    # Step 4: Correct misaligned cycles
    #raw_azimuth_corrected = raw_azimuth_cycles.copy()
    #raw_azimuth_corrected[:,:] = raw_azimuth_mode

    # Step 5: Flatten corrected Y array
   # return raw_azimuth_corrected.flatten()


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    import scipy as sp

    #data_directory = r"D:\data\20250606\14"
    data_directory = r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\iap_2025-07-16\data\20250606"
    #data_directory = r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\ir_2025-07-25\data\20250607"

    #raw_files = list(Path(data_directory).rglob("*.raw"))

    grouped_raw = list(get_file_by_scan(data_directory).values())

    for i in range(50):
        print(i)
        data = load_raw(raw_files=grouped_raw[3], is4bits=True)

        # FIX RAW_AZIMUTH MISALIGNMENT
        spoke_number = np.array(data['spoke_number'])
        raw_azimuth = np.array(data['raw_azimuth'])

        raw_azimuth_corrected = correct_azimuth_misalignment(spoke_number, raw_azimuth)
    #
    # plt.figure()
    # plt.plot(spoke_number, raw_azimuth, label='y')
    # plt.plot(spoke_number, raw_azimuth_corrected, '--', label='y_corrected')
    # plt.show(block=True)
