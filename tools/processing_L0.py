from pathlib import Path
import datetime

import numpy as np
import pandas as pd
import xarray as xr
import scipy as sp

from tools.unpack_utils import load_raw_file
from tools.pool_utils import starpool_function
from tools.processing_utils import load_raw_file_index, sel_raw_file_by_time


def radar_processing_L0(
        raw_file_index: str,
        out_root_dir: str,
        station: str,
        start_time: str,
        end_time: str,
        heading: float,
        lat: float,
        lon: float,
        time_offset: int,
        ):
    """

    Parameters
    ----------
    raw_file_index
    out_root_dir
    station
    start_time
    end_time
    heading
    lat
    lon
    time_offset: In minutes:
        realtime = radar_time - time_offset

    Returns
    -------

    """

    rf_index_df = load_raw_file_index(raw_file_index)

    rf_index_df = sel_raw_file_by_time(dataframe=rf_index_df, start_time=start_time, end_time=end_time)

    args_list = []

    L0_out_path = Path(out_root_dir).joinpath("L0")

    for ts, group in rf_index_df.groupby('timestamp'):
        _date = str(ts).split(" ")[0]
        out_path = L0_out_path.joinpath(station, _date)
        out_path.mkdir(parents=True, exist_ok=True)

        args_list.append(
            (
                group['path'].values,
                out_path,
                station,
                heading,
                lat,
                lon,
                time_offset,
            )
        )

    L0_file_index = starpool_function(_radar_processing_L0, args_list)

    df = pd.DataFrame(L0_file_index, columns=['station', 'timestamp', 'path'])

    df.to_csv(L0_out_path.joinpath(f'{station}_L0_index.csv'), index=False)


def _radar_processing_L0(
        raw_files: str,
        out_path: str,
        station: str,
        heading: float,
        lat: float,
        lon: float,
        time_offset: int
) -> xr.Dataset:
    """

    Parameters
    ----------
    raw_files
    station
    out_path
    heading
    lat
    lon
    time_offset: in minutes.
        realtime = radar_time - time_offset

    Returns
    -------

    """
    ts = Path(raw_files[0]).stem.split("_")[0]

    data = load_raw_scans(raw_files)

    try:
        fill_data_for_missing_spoke(data)

        pad_data_for_incomplete_scan(data)

        correct_azimuth_misalignment(data)

        dataset = make_dataset_volume(data=data, ts=ts, heading=heading)

        if time_offset:# not None or 0
            dt = np.timedelta64(time_offset * 60, 's')
            dataset['time'].values = dataset['time'].values - dt
            dataset['scan_time'].values = dataset['scan_time'].values - dt

    except ValueError as e:
        print(ts, e, "error in radar_scan_processing_L0")
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
    save_path = Path(out_path).joinpath(f"{fname}.nc")
    dataset.to_netcdf(save_path, engine="h5netcdf", encoding=encoding)

    print(f"{station} | {ts} | L0 Done")

    return station, str(dataset.time.values), save_path


def load_raw_scans(raw_files: list[str]) -> dict[np.ndarray]:

    data = {
        "range": [],
        "time": [],
        "spoke_number": [],
        "raw_azimuth": [],
        "intensity": [],
    }

    for raw_file in raw_files:
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
