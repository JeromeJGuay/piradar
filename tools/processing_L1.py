import datetime

import numpy as np
from pathlib import Path

import xarray as xr

from tools.coordinate_transform import polar_to_cartesian, xy_to_en


def integrate_scan(dataset: xr.Dataset) -> xr.Dataset:
    return xr.Dataset(
        {
            "mean": dataset.intensity.mean("scan"),
            "std": dataset.intensity.std("scan")
        },
        attrs={
            'processing': "piradar L1",
            'processing_date': datetime.datetime.now().date().isoformat(),
            'heading': dataset.attrs['heading'],
            'lon': dataset.attrs['lon'],
            'lat': dataset.attrs['lat'],
        }
    )


def align_for_azimuth(dataset: xr.Dataset) -> xr.Dataset:

    dataset = dataset.sortby("raw_azimuth")

    dataset.coords['azimuth'] = convert_raw_azimuth(dataset['raw_azimuth'])

    dataset = dataset.swap_dims({"raw_azimuth": "azimuth"})

    dataset = dataset.drop_vars("raw_azimuth")

    return dataset


def convert_raw_azimuth(raw_azimuth: np.ndarray):
    return ((2 * np.pi) / 4096) * raw_azimuth


def compute_lonlat_coordinates(dataset: xr.Dataset) -> xr.Dataset:
    x_grid = dataset['radius'] * np.sin(dataset['azimuth'])
    y_grid = dataset['radius'] * np.cos(dataset['azimuth'])

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
    station = "ivo"

    L0_root_path = rf"E:\OPP\ppo-qmm_analyses\data\radar\L0"
    L1_root_path = rf"E:\OPP\ppo-qmm_analyses\data\radar\L1"
    ###
    # PROCESSING L1
    for day_path in Path(L0_root_path).joinpath(station).iterdir():
        scan_day = day_path.stem

        for hour_path in day_path.iterdir():
            scan_hour = hour_path.stem

            out_dir = Path(L1_root_path).joinpath(station, scan_day)

            Path(out_dir).mkdir(parents=True, exist_ok=True)

            ds_list = []

            for L0_nc in hour_path.glob("*.nc"):
                ds = xr.open_dataset(L0_nc)

                ds = integrate_scan(dataset=ds)

                ds = align_for_azimuth(dataset=ds)

                ds_list.append(ds)

                print(L0_nc)

            ds = xr.concat(ds_list, dim='time')
            ds = compute_lonlat_coordinates(ds)

            fname = "_".join([
                station,
                "L1",
                scan_day,
                scan_hour,
            ])

            ds.to_netcdf(Path(out_dir).joinpath(f"{fname}.nc"), engine="h5netcdf")
            print(fname)
            # break

    # import matplotlib
    #
    # matplotlib.use('Qt5Agg')
    # import matplotlib.pyplot as plt
    #
    # #radar_image = ds.isel(time=0)['mean'].values
    # radar_image = ds.mean('time')['mean'].values
    #
    # radar_image[radar_image == 0] = np.nan
    #
    # plt.figure()
    # plt.contourf(
    #     ds.lon,
    #     ds.lat,
    #     radar_image,
    # )
    #
    # plt.show(block=True)





