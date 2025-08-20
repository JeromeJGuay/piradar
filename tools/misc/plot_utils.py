import numpy as np
import xarray as xr

import matplotlib
from matplotlib import style as mplstyle
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

matplotlib.rcParams['path.simplify'] = True

#matplotlib.rcParams['path.simplify_threshold'] = 0.5
mplstyle.use('fast')

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader

from tools.processing_L1 import compute_lonlat_coordinates

L1_ROOT_DIR = r"E:\OPP\ppo-qmm_analyses\data\radar\L1"

_path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

_bank_shp_list = list(Path(_path_to_nhnl_shp).glob("*BANK*.shp"))

BANK_SHP_DATA = [shapereader.Reader(_shp) for _shp in _bank_shp_list]


def add_bank(ax):
    for bank_shp in BANK_SHP_DATA:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)


def get_L1_slices(station, ts, dt):
    t0 = np.datetime64(ts,'s')
    t1 = t0 + np.timedelta64(60*dt, 's')

    day = ts.split("T")[0].replace("-", "")
    hour = ts.split("T")[1].split(":")[0]
    filename = f"{station}_L1_{day}_{hour}.nc"
    fn = Path(L1_ROOT_DIR).joinpath(station, day, filename)

    if fn.is_file():
        return xr.open_dataset(fn).sel(time=slice(t0,t1))
    else:
        return None



def overlay_radar_plot(ts, dt):
    headings = {'ive': 103.0, 'ivo': -42.0, 'ir': -26.5, 'iap': -98.5}
    stations = ['ive', 'ivo', 'ir', 'iap']

    time_offsets = {
        "ive": 0,
        "ivo": 0,
        "ir": 40, # 40 minutes d'avance
        "iap": 0
    }

    colors = ['red', 'green', 'blue', 'yellow']

    extent = np.array([
        -69.9,
        -69.0,
        47.7,
        48.4,
    ])

    central_lon = np.mean(extent[:2])

    plt.figure(figsize=(12, 8))

    plt.suptitle(f"{ts}")

    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    add_bank(ax)

    for station, color in zip(stations, colors):
        _ts = str(np.datetime64(ts,'s') - np.timedelta64(60*time_offsets[station],'s'))
        ds = get_L1_slices(station, _ts, dt)

        ds.attrs['heading'] = headings[station]

        ds = compute_lonlat_coordinates(ds)

        radar_image = ds['scan_mean'].interpolate_na('azimuth').sum('time').values
        radar_image[radar_image == 0] = np.nan

        im = ax.contourf(
            ds.lon,
            ds.lat,
            radar_image,
            zorder=100,
            #levels=1,
            transform=ccrs.PlateCarree(),
            #colors=color,
            alpha=.25,
        )
        ax.scatter([], [], c=color, label=station)

    ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

    plt.legend()

    plt.show(block=True)



