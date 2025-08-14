import numpy as np
import xarray as xr

import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


def basic_radar_plot(dataset: xr.Dataset, zoom=None, is_polar: bool = False,
                     method="mean"):

    _methods_ = ("mean", "std",)

    if method not in _methods_ and not isinstance(method, int):
        raise ValueError(f"Method must be on off {_methods_} or an int (scan id)/.")

    if zoom is None:
        zoom = dataset.attrs['max_range']

    if is_polar:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlim(0, zoom)
    else:
        fig, ax = plt.subplots()
        ax.set_xlim(-zoom, zoom)
        ax.set_ylim(-zoom, zoom)

    if isinstance(method, int):
        radar_image = dataset.intensity.sel(scan=method).values.astyp(float)
    elif method == "mean":
        radar_image = dataset.intensity.mean('scan').values.astype(float)
    elif method == "std":
        radar_image = dataset.intensity.std('scan').values.astype(float)

    fig_title = " | ".join([
        dataset.attrs['station'],
        dataset.attrs['files_ts'],
        f"Scan {method}" if isinstance(method, int) else method,
    ])
    fig.suptitle(fig_title)
    radar_image[radar_image == 0] = np.nan

    azimuth = (dataset['azimuth'] + dataset.attrs['azimuth_offset'] - np.deg2rad(dataset.attrs['heading']))

    if is_polar:
        ax.contourf(
            azimuth,
            dataset['radius'],
            radar_image.T,
            levels=16 if dataset.attrs['is4bits'] else 256,
            cmap='viridis',
            alpha=1,
            zorder=100,
        )
        plt.tight_layout()
    else:

        x_coord = dataset['radius'] * np.sin(azimuth)
        y_coord = dataset['radius'] * np.cos(azimuth)

        ax.contourf(
            x_coord,
            y_coord,
            radar_image.T,
            levels=16 if dataset.attrs['is4bits'] else 256,
            cmap="viridis",
            alpha=1
        )
        plt.tight_layout()

    return fig


if __name__ == "__main__":
    from pathlib import Path

    import cartopy
    import cartopy.crs as ccrs
    import cartopy.io.shapereader as shapereader

    from processing_L1 import compute_lonlat_coordinates

    path_to_nhnl_shp = r"C:\Users\guayj\Documents\workspace\data\national_hydro_network_layers_shapefile"

    bank_shp_list = list(Path(path_to_nhnl_shp).glob("*BANK*.shp"))

    bank_shp_data = [shapereader.Reader(_shp) for _shp in bank_shp_list]

    data_dir = r"E:\OPP\ppo-qmm_analyses\data\radar\L1\ir\20250607"

    L1_file = Path(data_dir).joinpath("ir_L1_20250607_00.nc")

    ds = xr.open_dataset(L1_file)

    ds.attrs['heading'] = 25


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

    #ax = plt.axes(projection=ccrs.AlbersEqualArea(central_lon, central_lat))
    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)

    for bank_shp in bank_shp_data:
        ax.add_geometries(bank_shp.geometries(), ccrs.PlateCarree(), facecolor='lightgray', edgecolor='black')

    radar_image = ds.max('time')['mean'].values

    radar_image[radar_image == 0] = np.nan

    im = ax.contourf(
        ds.lon,
        ds.lat,
        radar_image,
        zorder=100,
        levels=255,
        transform=ccrs.PlateCarree()
    )

    plt.colorbar(im, ax=ax, shrink=0.5)

    ax.gridlines(draw_labels=True, lw=1.2, edgecolor="darkblue", zorder=12, facecolor='wheat')

    plt.legend()

    plt.show(block=True)
