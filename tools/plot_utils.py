import numpy as np
import xarray as xr

import matplotlib
from matplotlib import style as mplstyle
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

matplotlib.rcParams['path.simplify'] = True

#matplotlib.rcParams['path.simplify_threshold'] = 0.5
mplstyle.use('fast')


if __name__ == "__main__":
    from pathlib import Path

    import cartopy
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shapereader

    from processing_L1 import compute_lonlat_coordinates

    path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

    bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

    bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

    data_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1\iap\20250711"


    file_idx = 1
    L1_files = list(Path(data_dir).glob("*.nc"))
    L1_file = L1_files[file_idx]

    ds = xr.open_dataset(L1_file)

    #ds.attrs['heading'] = -40

    #ds = compute_lonlat_coordinates(ds)

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
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='None', edgecolor='black')

    #radar_image = ds.max('time')['mean'].values

    #i_slices = [0,10,20,30, 40, 50]
    #cmap = plt.get_cmap('jet')
    #colors = cmap(np.linspace(0, 1, len(i_slices)))

    #for id, color in zip(i_slices, colors):
    #radar_image = ds['mean'].isel(time=slice(id, id+5)).mean('time').values
    radar_image = ds['scan_mean'].max('time').values
    radar_image[radar_image == 0] = np.nan

    im = ax.contourf(
        ds.lon,
        ds.lat,
        radar_image,
        zorder=100,
        levels=1,
        transform=ccrs.PlateCarree(),
        colors='red',
        alpha=.5,
    )

    data_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1\ir\20250711"
    file_idx = 0
    L1_files = list(Path(data_dir).glob("*.nc"))
    L1_file = L1_files[file_idx]
    ds = xr.open_dataset(L1_file)

    #ds.attrs['heading'] = -25
    ds = compute_lonlat_coordinates(ds)

    radar_image = ds['scan_mean'].max('time').values
    radar_image[radar_image == 0] = np.nan

    im = ax.contourf(
        ds.lon,
        ds.lat,
        radar_image,
        zorder=100,
        levels=1,
        transform=ccrs.PlateCarree(),
        colors='blue',
        alpha=.5,
    )

    ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

    plt.show(block=True)
