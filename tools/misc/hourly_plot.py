import numpy as np
import xarray as xr
import pandas as pd
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

matplotlib.rcParams['path.simplify'] = True

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader

from tools.processing_L1 import compute_lonlat_coordinates
from tools.pool_utils import pool_function
from tools.processing_utils import sel_file_by_time_slice

fig_save_root_path = r"C:\Users\guayj\Documents\workspace\figures\radar"

# headings = {'ive': 103.0, 'ivo': -42.0, 'ir': -26.5, 'iap': -100.0} # 2025-06
headings = {'ive': 106.0, 'ivo': -38.0, 'ir': -26.5, 'iap': -100.0} # 2025-10

stations = ['ive', 'ivo', 'ir', 'iap']

DISCRET_HOUR_CMAP = ['red', 'green', 'blue', 'yellow']

path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

root_path = Path(rf"E:\OPP\ppo-qmm_analyses\data\radar_2025-10-14")

extent = np.array([
    -69.9,
    -69.0,
    47.7,
    48.4,
])

central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[2:])

station = "ive"

fig_save_path = Path(fig_save_root_path).joinpath(station)
fig_save_path.mkdir(parents=True, exist_ok=True)

start_time = "2025-07-29T00:00:00"
end_time = "2025-10-14T00:00:00"

L1_index_df = pd.read_csv(Path(root_path).joinpath("L1", f'{station}_L1_index.csv'))
L1_files = sel_file_by_time_slice(L1_index_df, start_time, end_time)['path'].values


# ALWAYS 60 time
cmap = plt.get_cmap('jet')
DISCRET_HOUR_CMAP = cmap(np.linspace(0, 1, 60))

exists_ok=True


def hourly_plot(L1_file):
    print(f"Loading: {L1_file}")
    ds = xr.open_dataset(L1_file)

    fname = f"{station}_{str(ds.time.values[0])[0:19]}"

    _fname = fname.replace("-", "").replace(":", "")
    _fig_save_path = fig_save_path.joinpath(f"{_fname}.png")
    if exists_ok and _fig_save_path.exists():
        ds.close()
        print(f"fig {_fname} already exist")
        return

    #### pre data
    ds.attrs['heading'] = headings[station]
    ds = compute_lonlat_coordinates(ds)

    #### FIGURE
    plt.figure(figsize=(12, 8))

    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    for bank_shp in bank_shp_data:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black', zorder=200)

    radar_images = ds['scan_mean'].interpolate_na('azimuth').values
    radar_images[radar_images == 0] = np.nan
    lon = ds['lon'].values
    lat = ds['lat'].values

    plt.suptitle(fname)
    for i_slice, color in zip(range(ds.sizes['time']), DISCRET_HOUR_CMAP):
        #print(f"{i_slice} / {ds.sizes['time']}")
        #ds_tmp = ds.isel(time=i_slice)
        #radar_image = ds_tmp['scan_mean'].interpolate_na('azimuth').values
        #radar_image[radar_image == 0] = np.nan

        im = ax.contourf(
            lon,
            lat,
            radar_images[i_slice],
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

    plt.tight_layout()

    # Add the colorbar
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, shrink=0.7)
    cbar.set_label('Time (minutes)', fontsize=12)

    pos = cbar.ax.get_position()
    pos.x0 = 0.9
    cbar.ax.set_position(pos)

    plt.savefig(_fig_save_path, dpi=200)
    print(f"{_fig_save_path} Saved !")
    plt.close()

    ds.close()


if __name__ == "__main__":
    pool_function(hourly_plot, L1_files, n_workers=40)

