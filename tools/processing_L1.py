import datetime

import numpy as np
from pathlib import Path

import xarray as xr

from tools.coordinate_transform import xy_to_en


from tools.pool_utils import pool_function, starpool_function

from tools.unpack_utils import convert_raw_azimuth, compute_radius


def l1_processing(station: str, L0_root_path: str, L1_root_path: str):
    for day_path in Path(L0_root_path).joinpath(station).iterdir():
        scan_day = day_path.stem
        args = [
            [scan_day, hour_path, L1_root_path, station] for hour_path in day_path.iterdir()
        ]

        starpool_function(
            _l1_pre_processing_pool,
            args
        )


def _l1_pre_processing_pool(
        scan_day,
        hour_path,
        L1_root_path,
        station,
) -> xr.Dataset:


    scan_hour = hour_path.stem

    out_dir = Path(L1_root_path).joinpath(station, scan_day)

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    ds_list = []

    for L0_nc in hour_path.glob("*.nc"):
        ds = xr.open_dataset(L0_nc)

        ds = integrate_scan(dataset=ds)

        ds = sort_by_azimuth(dataset=ds)

        ds = add_radius_coords(dataset=ds)

        ds_list.append(ds)

    if len(ds_list) == 0:
        return

    ds = xr.concat(ds_list, dim='time')

    ds = compute_lonlat_coordinates(ds)

    fname = "_".join([
        station,
        "L1",
        scan_day,
        scan_hour,
    ])

    encoding = {
        "scan_mean": dict(zlib=True, complevel=9),
        "scan_std": dict(zlib=True, complevel=9)
    }

    ds.to_netcdf(
        Path(out_dir).joinpath(f"{fname}.nc"),
        engine="h5netcdf",
        encoding=encoding
    )
    print(fname)
    return ds


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


if __name__ == "__main__":
    import time
    station = "iap"

    L0_root_path = rf"E:\OPP\ppo-qmm_analyses\data\radar\L0"
    L1_root_path = rf"E:\OPP\ppo-qmm_analyses\data\radar\L1"

    l1_processing(L0_root_path=L0_root_path, L1_root_path=L1_root_path, station=station)


