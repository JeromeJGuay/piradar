from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

import matplotlib
from matplotlib.animation import FuncAnimation
from matplotlib import animation


matplotlib.use('Qt5Agg')
#matplotlib.use("module://gr.matplotlib.backend_gr")

matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1

from matplotlib import style as mplstyle
mplstyle.use('fast')

import matplotlib.pyplot as plt


import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader

from tools.processing_utils import sel_file_by_time_slice

L1_ROOT_DIR = r"E:\OPP\ppo-qmm_analyses\data\radar_2\L1"

_path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

_bank_shp_list = list(Path(_path_to_nhnl_shp).glob("*BANK*.shp"))

BANK_SHP_DATA = [shapereader.Reader(_shp) for _shp in _bank_shp_list]


def add_bank(ax):
    for bank_shp in BANK_SHP_DATA:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)


def get_station_L1_index_df(station: str) -> pd.DataFrame:
    return pd.read_csv(Path(L1_ROOT_DIR).joinpath(f'{station}_L1_index.csv'))


def initiate_figure(extent):
    fig = plt.figure(figsize=(12, 8))
    central_lon = np.mean(extent[:2])
    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)
    add_bank(ax)

    return fig, ax


def load_L1_nc_files(nc_files) -> xr.Dataset:

    ds_list = []
    for ncf in nc_files:
        ds_list.append(xr.open_dataset(ncf))

    return xr.concat(ds_list, dim="time").sel(time=slice(start_time, end_time)).interpolate_na('azimuth')




if __name__ == "__main__":
    out_save_path = r"C:\Users\guayj\Documents\workspace\animation\radar"
    cmap = plt.cm.magma
    levels = 5

    extent = np.array([
        -69.9,
        -69.0,
        47.7,
        48.4,
    ])

    station = "ive"
    start_time = "2025-07-07T12:00:00"
    end_time = "2025-07-07T15:00:00"

    anim_save_path = Path(out_save_path).joinpath(station)
    anim_save_path.mkdir(exist_ok=True, parents=True)

    L1_index_df = get_station_L1_index_df(station)

    L1_files = sel_file_by_time_slice(L1_index_df, start_time, end_time)['path'].values

    ds = load_L1_nc_files(L1_files)

    print("L1 Data loaded")

    lon = ds['lon'].values
    lat = ds['lat'].values
    time = ds['time'].values

    ds = ds.interpolate_na('azimuth')


    def get_radar_im(i):
        rim = ds.isel(time=i)['scan_mean'].values
        rim[rim == 0] = np.nan
        return rim


    radar_images = [get_radar_im(i) for i in range(ds.sizes['time'])]


    print("figure init reached")
    fig, ax = initiate_figure(extent=extent)

    trail = 2
    mesh_obj = trail * [None]


    def update(i):
        if mesh_obj[0] is not None:
            try:
                mesh_obj[0].remove()
            except ValueError:
                pass

        for j in range(trail-1):
            if mesh_obj[j+1] is not None:
                mesh_obj[j+1].set_alpha((j+1)/trail)

        mesh_obj[0:trail-1] = mesh_obj[1:]

        mesh_obj[-1] = ax.pcolormesh(lon, lat, radar_images[i], zorder=100, transform=ccrs.PlateCarree(), cmap=cmap, shading='nearest')

        ts = np.datetime_as_string(time[i], unit='s')
        fig.suptitle(ts)
        print(i)
        print(f"updating: {ts}")

        return mesh_obj

    print("animation reached ... ")

    n_frames = ds.sizes['time']
    #n_frames=10
    ani = matplotlib.animation.FuncAnimation(fig, update, frames=n_frames,
                                             interval=500, blit=False, repeat=True)

    aname = f"{station}_{start_time.replace(':','')}_{end_time.replace(':','')}.mp4"

    ani.save(anim_save_path.joinpath(aname), writer="ffmpeg", fps=5, dpi=200)

