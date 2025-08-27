import datetime

import numpy as np
import pandas as pd
from pathlib import Path

import xarray as xr

from tools.coordinate_transform import xy_to_en

from tools.pool_utils import starpool_function

from tools.unpack_utils import convert_raw_azimuth, compute_radius

from tools.processing_utils import sel_file_by_time_slice


def radar_processing_L1(station: str, L0_file_index: str, out_root_dir: str, start_time: str=None, end_time: str=None):

        L1_out_path = Path(out_root_dir).joinpath("L1")

        out_path = L1_out_path.joinpath(station)
        out_path.mkdir(parents=True, exist_ok=True)

        L0_index_df = pd.read_csv(L0_file_index)
        L0_index_df = sel_file_by_time_slice(dataframe=L0_index_df, start_time=start_time, end_time=end_time)

        L0_index_df['date'] = L0_index_df['timestamp'].dt.date

        args_list = []

        L0_index_df['date'] = L0_index_df['timestamp'].dt.date
        L0_index_df['hour'] = L0_index_df['timestamp'].dt.hour
        for date, date_group in L0_index_df.groupby('date'):
            for hour, hour_group in date_group.groupby('hour'):
                ts = f"{date}T{hour:02}".replace('-', '')
                args_list.append([
                    ts,
                    hour_group['path'].values,
                    station,
                    out_path
                ])

        L1_file_index = starpool_function(
            _radar_processing_L1,
            args_list
        )

        df = pd.DataFrame(L1_file_index, columns=['station', 'start_time', 'end_time', 'number_of_scan', 'path'])

        df.to_csv(L1_out_path.joinpath(f'{station}_L1_index.csv'), index=False)


def _radar_processing_L1(date, L0_files, station, out_path) -> xr.Dataset:
    ds_list = []

    for L0_nc in L0_files:
        ds_list.append(_radar_pre_processing_L1(L0_nc))
    ds = xr.concat(ds_list, dim='time')

    # interpolate missing azimuth
    # Some scan will have raw azimuht of: 1,3,5, ..., 4095 and the next 2,4,6,...,4094.
    # These values are interpolated to have continuous grids. Should not affect the accuracy of the data
    ds = ds.interpolate_na('azimuth')

    ds = compute_lonlat_coordinates(ds)

    fname = "_".join([
        station,
        "L1",
        date
    ])

    encoding = {
        "scan_mean": dict(zlib=True, complevel=9),
        "scan_std": dict(zlib=True, complevel=9)
    }

    _out_path = out_path.joinpath(f"{fname}.nc")
    ds.to_netcdf(
        _out_path,
        engine="h5netcdf",
        encoding=encoding
    )
    print(f"{fname} done !")
    return station, str(ds.time.min().values), str(ds.time.max().values), ds.sizes['time'], _out_path


def _radar_pre_processing_L1(L0_nc: str) -> xr.Dataset:
    dataset = xr.open_dataset(L0_nc)

    dataset = integrate_scan(dataset=dataset)

    dataset = sort_by_azimuth(dataset=dataset)

    dataset = add_radius_coords(dataset=dataset)

    return dataset


def integrate_scan(dataset: xr.Dataset) -> xr.Dataset:
    return xr.Dataset(
        {
            "scan_mean": dataset.intensity.mean("scan").astype(np.float32),
            "scan_std": dataset.intensity.std("scan").astype(np.float32)
        },
        attrs={
            'processing': "piradar L1",
            'processing_date': datetime.datetime.now().date().isoformat(),
            'heading': dataset.attrs['heading'],
            'lon': dataset.attrs['lon'],
            'lat': dataset.attrs['lat'],
            'range': dataset.attrs['range']
        }
    )


def add_radius_coords(dataset: xr.Dataset) -> xr.Dataset:

    _range = compute_radius(dataset.attrs['range'], is4bits=False)

    dataset = dataset.assign_coords({"radius": ('r_bins', _range)})

    return dataset


def sort_by_azimuth(dataset: xr.Dataset) -> xr.Dataset:

    dataset = dataset.sortby("raw_azimuth")

    dataset.coords['azimuth'] = convert_raw_azimuth(dataset['raw_azimuth'])

    dataset = dataset.swap_dims({"raw_azimuth": "azimuth"})

    dataset = dataset.drop_vars("raw_azimuth")

    return dataset


def compute_lonlat_coordinates(dataset: xr.Dataset) -> xr.Dataset:
    azimuth = dataset['azimuth'] + np.deg2rad(dataset.attrs['heading'])

    x_grid = dataset['radius'] * np.sin(azimuth)
    y_grid = dataset['radius'] * np.cos(azimuth)

    xy_grid = np.array([x_grid, y_grid]).T

    origin_en = np.array([
        dataset.attrs['lon'],
        dataset.attrs['lat']
    ])
    en_grid = xy_to_en(points_xy=xy_grid, origin_en=origin_en)

    lon_grid = en_grid[..., 0]
    lat_grid = en_grid[..., 1]

    dataset['lon'] = xr.DataArray(lon_grid, dims=('azimuth', "radius"))
    dataset['lat'] = xr.DataArray(lat_grid, dims=('azimuth', "radius"))

    return dataset.set_coords(['lon', 'lat'])


