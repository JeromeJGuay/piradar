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