from pathlib import Path
import struct
import datetime

import numpy as np
import xarray as xr
import scipy as sp

from tools.unpack_utils import load_raw_file
from tools.pool_utils import pool_function, starpool_function


FRAME_DELIMITER = b"FH"
FRAME_HEADER_FORMAT = "<LBHHH"
FRAME_HEADER_SIZE = struct.calcsize(FRAME_HEADER_FORMAT) #11

SPOKE_DATA_DELIMITER = b"SD"
SPOKE_DATA_FORMAT = "<HH512B"
SPOKE_DATA_SIZE = struct.calcsize(SPOKE_DATA_FORMAT)


def radar_processing_L0(raw_root_path: str, out_root_path: str, start_time: str, heading: float, lat:float, lon: float):
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")

    for day_path in Path(raw_root_path).iterdir():
        scan_day = day_path.stem
        if (datetime.datetime.strptime(scan_day, "%Y%m%d").date() - start_time.date()).total_seconds() < 0:
            print("Skipping", scan_day)
            continue

        args_list = []

        for hour_path in day_path.iterdir():
            scan_hour = hour_path.stem
            if (datetime.datetime.strptime(scan_day+scan_hour, "%Y%m%d%H") - start_time).total_seconds() < 0:
                print("Skipping", scan_day, scan_hour)
                continue

            out_dir = Path(out_root_path).joinpath(station, scan_day, scan_hour)

            Path(out_dir).mkdir(parents=True, exist_ok=True)

            grouped_scan_files = get_files_grouped_by_scan(raw_root_path, day=scan_day, hour=scan_hour)

            args_list += [
                (
                    raw_files,
                    heading,
                    lat,
                    lon,
                    station,
                    out_dir,
                )
                for raw_files in grouped_scan_files.values()
            ]

        if len(args_list) == 0:
            continue

        starpool_function(_radar_scan_processing_L0, args_list)


def get_files_grouped_by_scan(path, day, hour):
    scan_groups = {}
    raw_files = list(Path(path).joinpath(day, hour).glob("*.raw"))
    for rf in raw_files:
        scan_dt = rf.name.split("_")[0]
        if scan_dt in scan_groups:
            scan_groups[scan_dt].append(rf)
        else:
            scan_groups[scan_dt] = [rf]
    return scan_groups


def _radar_scan_processing_L0(raw_files: str, heading: float, lat: float, lon: float,station: str,out_dir: str)->xr.Dataset:

    ts = Path(raw_files[0]).name.split("_")[0]

    data = load_raw_scans(raw_files)

    try:
        fill_data_for_missing_spoke(data)

        pad_data_for_incomplete_scan(data)

        correct_azimuth_misalignment(data)

        dataset = make_dataset_volume(data=data, ts=ts, heading=heading)
    except ValueError as e:
        print(ts, e, "#######################")
        return None

    # Removing the first scan as a precaution
    dataset = dataset.isel(scan=slice(1, None))

    # add metadata
    dataset.attrs['lat'] = lat
    dataset.attrs['lon'] = lon
    dataset.attrs['processing'] = "piradar L0"
    dataset.attrs['processing_date'] = datetime.datetime.now().date().isoformat()

    ### OUTPUT TO NETCDF ###
    fname = "_".join([
        station,
        "L0",
        ts,
    ])

    encoding = {'intensity': {'zlib':True, 'complevel': 9}}
    dataset.to_netcdf(Path(out_dir).joinpath(f"{fname}.nc"), engine="h5netcdf", encoding=encoding)

    print(f"{station} | {ts} | L0 Done")

    return dataset


def load_raw_scans(raw_files: list[str]) -> dict[np.ndarray]:


    data = {
        "range": [],
        "time": [],
        "spoke_number": [],
        "raw_azimuth": [],
        "intensity": [],
    }

    for raw_file in raw_files:
        #frames += load_raw_file(raw_file=raw_file, is4bits=is4bits)
        frames = load_raw_file(raw_file=raw_file, is4bits=False)

        for frame in frames:
            data['range'].append(frame['range'])
            data['time'] += frame['time']
            data['spoke_number'] += frame['spoke_number']
            data['raw_azimuth'] += frame['raw_azimuth']
            data['intensity'] += frame['intensity']

    # Convert to numpy array with proper types.
    data['spoke_number'] = np.array(data['spoke_number'], dtype=np.uint16)
    data['raw_azimuth'] = np.array(data['raw_azimuth'], dtype=float)
    data['intensity'] = np.array(data['intensity'], dtype=float)
    data['time'] = np.array(data['time'], dtype='datetime64[s]')
    data['range'] = np.array(data['range'], dtype=float) # may int ? FIXME

    return data


def fill_data_for_missing_spoke(data: dict[np.ndarray]):
    """
    inplace modification
    """

    _diff = np.diff(data['spoke_number'])

    idx = np.where((_diff != 1) & (_diff != -4095))[0]

    n_missing = (_diff[idx] - 1) % 4096

    u_raw_azimuth, c_raw_azimuth = np.unique(np.diff(data['raw_azimuth']), equal_nan=False, return_counts=True)
    raw_azimuth_step = u_raw_azimuth[np.argmax(c_raw_azimuth)]

    for i in reversed(range(len(idx))):
        insert_index = idx[i] + 1

        _missing_spoke_number = np.arange(n_missing[i]) + data['spoke_number'][idx[i]] + 1
        _missing_spoke_number = _missing_spoke_number % 4096
        data['spoke_number'] = np.insert(data['spoke_number'], insert_index, _missing_spoke_number)

        _filled_azimuth = np.arange(n_missing[i]) * raw_azimuth_step + data['raw_azimuth'][idx[i]] + raw_azimuth_step
        _filled_azimuth = _filled_azimuth % 4096

        data['raw_azimuth'] = np.insert(data['raw_azimuth'], insert_index, _filled_azimuth)

        _nan_intensity = np.ones((n_missing[i], data['intensity'].shape[1])) * np.nan
        data['intensity'] = np.insert(data['intensity'], insert_index, _nan_intensity, axis=0)

        _missing_time = np.ones(n_missing[i]) * np.nan
        _missing_time = _missing_time.astype("datetime64[s]")
        data['time'] = np.insert(data['time'], insert_index, _missing_time)


def pad_data_for_incomplete_scan(data: dict):

    _mod = data['spoke_number'].shape[0] % 4096
    if _mod == 0:
        return

    pad_length = 4096 - _mod

    u_raw_azimuth, c_raw_azimuth = np.unique(np.diff(data['raw_azimuth']), equal_nan=False, return_counts=True)
    raw_azimuth_step = u_raw_azimuth[np.argmax(c_raw_azimuth)]

    _missing_spoke_number = np.arange(pad_length) + data['spoke_number'][-1] + 1
    _missing_spoke_number = _missing_spoke_number % 4096
    data['spoke_number'] = np.append(data['spoke_number'], _missing_spoke_number)

    _filled_azimuth = np.arange(pad_length) * raw_azimuth_step + data['raw_azimuth'][-1] + raw_azimuth_step
    _filled_azimuth = _filled_azimuth % 4096
    data['raw_azimuth'] = np.append(data['raw_azimuth'], _filled_azimuth)

    _nan_intensity = np.ones((pad_length, data['intensity'].shape[1])) * np.nan
    data['intensity'] = np.append(data['intensity'], _nan_intensity, axis=0)

    _missing_time = np.ones(pad_length) * np.nan
    _missing_time = _missing_time.astype("datetime64[s]")
    data['time'] = np.append(data['time'], _missing_time)

    pass


def correct_azimuth_misalignment(data: dict):

    spoke_number = data['spoke_number']
    raw_azimuth = data['raw_azimuth']

    # Step 1: Detect cycle length
    unique_X, counts = np.unique(spoke_number, return_counts=True)

    if np.unique(counts).shape != (1,):

        print(f"size: {spoke_number.shape}")
        print(f"unique_count {np.unique(counts)}")
        print(f"Nx: {counts.max()}, Lx: {spoke_number.shape[0] // np.unique(counts)}")

        raise ValueError("Invalid dimensions. Scans don't have the same number of spokes.")

    Nx = counts.max()
    Lx = spoke_number.shape[0] // Nx

    if spoke_number.shape[0] != Nx * Lx:
        raise ValueError("Invalid dimensions. Scans don't have the same number of spokes.")

    raw_azimuth_cycles = raw_azimuth.reshape(Nx, Lx)

    raw_azimuth_mode = sp.stats.mode(raw_azimuth_cycles, axis=0, keepdims=False).mode

    raw_azimuth[:] = np.tile(raw_azimuth_mode, Nx).flatten()


def make_dataset_volume(data: dict, ts, heading=0) -> xr.Dataset:

    uniques, count = np.unique(data['raw_azimuth'], return_counts=True)
    n_azimuth = len(uniques)
    n_scan = count.max()

    raw_azimuth_coord = data['raw_azimuth'][:n_azimuth]

    intensity = data['intensity'].reshape((n_scan, n_azimuth, data['intensity'].shape[1]))

    # Set nan fill values to 0 for encoding.
    intensity[~np.isfinite(intensity)] = 0

    intensity = intensity.astype(np.uint8)

    frame_time = data['time'].reshape((n_scan, n_azimuth))

    scan_time = xr.DataArray(
        frame_time.astype('datetime64[s]'),
        dims=["scan", 'azimuth']
    ).mean("scan")

    dataset = xr.Dataset(
        {
            "intensity": (["scan", "raw_azimuth", "r_bins"], intensity),
            "scan_time": scan_time
        },
        coords={
            "raw_azimuth": raw_azimuth_coord.astype("uint16"),
            "time": np.datetime64(f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[9:11]}:{ts[11:13]}:{ts[13:15]}", 's')
        },
        attrs={
            "range": data['range'][0],
            'heading': heading,
        }
    )

    dataset['intensity'].encoding['dtype'] = "uint8"

    dataset['time'].attrs["standard_name"] = "time"

    dataset['time'].encoding['units'] = 'seconds since 1970-01-01 00:00:00'
    dataset['time'].encoding["calendar"] = "gregorian"

    dataset['scan_time'].encoding['units'] = 'seconds since 1970-01-01 00:00:00'
    dataset['scan_time'].encoding["calendar"] = "gregorian"

    return dataset



if __name__ == "__main__":

    station = "ir"

    latlons = {
        "ive": [48.051246, -69.423985],
        "ivo": [47.995305, -69.483108],
        "ir":  [48.069522, -69.554446],
        "iap": [48.106456, -69.321692]
    }

    headings = {'ive': 103.0, 'ivo': -42.0, 'ir': -26.5, 'iap': -99.5}


    data_directories = {
        "ive": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ive_2025-07-30\data",
        "ivo": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ivo_2025-07-30\data",
        "ir": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\ir_2025-07-25\data",
        "iap": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\iap_2025-07-16\data",
    }

    recording_sequences = {
        "ive": ("2025-06-13T14:30:00", "2025-07-30T13:18:00"),
        "ivo": ("2025-06-13T17:55:00", "2025-07-30T14:13:00"),
        "ir": ("2025-06-06T16:52:00", "2025-07-25T18:13:00"),
        "iap": ("2025-06-05T21:55:00", "2025-07-16T12:00:00")
    }

    lat, lon = latlons[station]
    raw_root_path = data_directories[station]
    heading = headings[station]
    recording_sequence = recording_sequences[station]
    out_root_path = rf"E:\OPP\ppo-qmm_analyses\data\radar\L0"
    start_time = recording_sequence[0]

    #start_time = "2025-06-12T00:00:00"

    radar_processing_L0(
        raw_root_path=raw_root_path,
        out_root_path=out_root_path,
        start_time=start_time,
        heading=heading,
        lat=lat,
        lon=lon,
    )

 #   bad_file = r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\ir_2025-07-25\data\20250606\17\20250606T173600_s01.raw"

#    frames = load_raw_file(bad_file, False)

    # idx = 892461
    #
    # with open(bad_file, "rb") as f:
    #     raw = f.read()
    #
    # print(raw[idx-10:idx+10])