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

import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader

from processing_L1 import compute_lonlat_coordinates


def plot_1():
    from pathlib import Path

    import cartopy
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shapereader

    from processing_L1 import compute_lonlat_coordinates

    features = {'toupie': [-69.61437, 48.10823]}

    path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

    bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

    bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

    data_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1\ivo\20250616"

    file_idx = 4
    L1_files = list(Path(data_dir).glob("*.nc"))
    L1_file = L1_files[file_idx]

    ds = xr.open_dataset(L1_file)

    ds.attrs['heading'] = -41.5

    ds = compute_lonlat_coordinates(ds)

    extent = np.array([
        ds['lon'].min(),
        ds['lon'].max(),
        ds['lat'].min(),
        ds['lat'].max(),
    ])

    central_lon = np.mean(extent[:2])
    central_lat = np.mean(extent[2:])
    plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    for bank_shp in bank_shp_data:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)

    # radar_image = ds.max('time')['mean'].values

    i_step = 6
    i_slices = np.arange(0, 60, i_step)
    cmap = plt.get_cmap('jet')
    colors = cmap(np.linspace(0, 1, len(i_slices)))

    for id, color in zip(i_slices, colors):
        radar_image = ds['scan_mean'].isel(time=slice(id, id + i_step)).mean('time').values
        # radar_image = ds['scan_mean'].max('time').values
        radar_image[radar_image == 0] = np.nan

        im = ax.contourf(
            ds.lon,
            ds.lat,
            radar_image,
            zorder=100,
            levels=1,
            transform=ccrs.PlateCarree(),
            colors=color,
            alpha=.5,
        )

    for feature, [lon, lat] in features.items():
        ax.scatter(lon, lat, marker='v', transform=ccrs.PlateCarree(), zorder=110)

    ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

    plt.show(block=True)

def overlay_radar_plot():
    headings = {
        "ive": 105   - 2.0,
        "ivo": -41.5 - 0.5,
        "ir": -26.5  - 0.0,
        "iap": -97.5 - 2.0,
    }

    stations = ['ive', 'ivo', 'ir', 'iap']

    time_offsets = {
        "ive": 0,
        "ivo": 0,
        "ir": -30,
        "iap": 0
    }

    colors = ['red', 'green', 'blue', 'yellow']

    path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

    bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

    bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

    day = "20250615"
    hour = "0"
    minute = 45
    dt_minute = 1

    start_time = np.datetime64(f"{day[:4]}-{day[4:6]}-{day[6:]}T{hour}:{minute:02}:00")
    end_time = np.datetime64(start_time, 's') + np.timedelta64(dt_minute * 60, 's')

    data_root_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1"

    extent = np.array([
        -69.9,
        -69.0,
        47.7,
        48.4,
    ])

    central_lon = np.mean(extent[:2])
    central_lat = np.mean(extent[2:])

    plt.figure(figsize=(12, 8))

    plt.suptitle(f"{start_time}")

    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    for bank_shp in bank_shp_data:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)

    for station, color in zip(stations, colors):
        data_dir = Path(data_root_dir).joinpath(station, day)

        L1_files = list(Path(data_dir).glob(f"*_{hour}*.nc"))

        if len(L1_files) == 0:
            print(station)
            continue

        L1_file = L1_files[0]

        ds = xr.open_dataset(L1_file)

        ds.attrs['heading'] = headings[station]

        ds = compute_lonlat_coordinates(ds)

        time_offset = np.timedelta64(time_offsets[station] * 60, 's')
        ds_tmp = ds.sel(time=slice(start_time + time_offset, end_time + time_offset)).mean('time').interpolate_na('azimuth')
        radar_image = ds_tmp['scan_mean'].values
        radar_image[radar_image == 0] = np.nan

        #print(station, ds_tmp.time.values)

        im = ax.contourf(
            ds_tmp.lon,
            ds_tmp.lat,
            radar_image,
            zorder=100,
            #levels=1,
            transform=ccrs.PlateCarree(),
            colors=color,
            alpha=.5,
        )

        ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

        ax.scatter([], [], c=color, label=station)

    plt.legend()

    plt.show(block=True)


#if __name__ == "__main__":
from pathlib import Path

import cartopy
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader

from processing_L1 import compute_lonlat_coordinates
from pool_utils import pool_function

fig_save_root_path = r"C:\Users\guayj\Documents\workspace\figures\radar"

headings = {'ive': 103.0, 'ivo': -42.0, 'ir': -26.5, 'iap': -99.5}

stations = ['ive', 'ivo', 'ir', 'iap']

colors = ['red', 'green', 'blue', 'yellow']

path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

data_root_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1"

extent = np.array([
    -69.9,
    -69.0,
    47.7,
    48.4,
])

central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[2:])

station = "ir"

fig_save_path = Path(fig_save_root_path).joinpath(station)
fig_save_path.mkdir(parents=True, exist_ok=True)

data_dir = Path(data_root_dir).joinpath(station)#, day)
L1_files = list(Path(data_dir).rglob(f"*.nc"))


def hourly_plot(L1_file):
    ds = xr.open_dataset(L1_file)
    ds.attrs['heading'] = headings[station]
    ds = compute_lonlat_coordinates(ds)

    cmap = plt.get_cmap('jet')
    colors = cmap(np.linspace(0, 1, ds.sizes['time']))

    plt.figure(figsize=(12, 8))

    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    for bank_shp in bank_shp_data:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)

    fname = f"{station}_{str(ds.time.values[0])[0:19]}"

    plt.suptitle(fname)

    for i_slice, color in zip(range(ds.sizes['time']), colors):

        ds_tmp = ds.isel(time=i_slice)
        radar_image = ds_tmp['scan_mean'].interpolate_na('azimuth').values
        radar_image[radar_image == 0] = np.nan

        im = ax.contourf(
            ds_tmp.lon,
            ds_tmp.lat,
            radar_image,
            zorder=100,
            transform=ccrs.PlateCarree(),
            colors=color,
            alpha=.5,
        )

        ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

    # Convert time to minutes since the start
    time_minutes = (ds.time - ds.time[0]) / np.timedelta64(1, 'm')

    # Create a ScalarMappable for the colorbar
    norm = matplotlib.colors.Normalize(vmin=time_minutes.min().item(), vmax=time_minutes.max().item())
    sm = matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Required for colorbar

    # Add the colorbar
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, shrink=0.7)
    cbar.set_label('Time (minutes)', fontsize=12)

    _fname = fname.replace("-", "").replace(":", "")
    print(_fname)
    plt.savefig(fig_save_path.joinpath(f"{_fname}.png"), dpi=200)
    plt.close()

pool_function(hourly_plot, L1_files)