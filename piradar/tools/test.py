from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from piradar.tools.read_data import read_raw


# plt.figure(figsize=(8, 8))
#
# frames = read_raw(rawfiles[1], is4bits=True)
#
# for frame in frames[0:30]:
#     # polar north, clockwise
#     x_coord = frame['radius'] * np.sin(frame['azimuth'])
#     y_coord = frame['radius'] * np.cos(frame['azimuth'])
#
#     plt.contourf(x_coord, y_coord, frame['intensity'].T)
#
# plt.show(block=True)

def cartesian_ppi(frames):
    if isinstance(frames, xr.Dataset):
        frames = [frames]

    fig, ax = plt.subplots()

    rlim = frames[0].attrs['max_range']
    ax.set_xlim(-rlim, rlim)
    ax.set_ylim(-rlim, rlim)

    for frame in frames:
        # polar north, clockwise
        x_coord = frame['radius'] * np.sin(frame['azimuth'])
        y_coord = frame['radius'] * np.cos(frame['azimuth'])

        #plt.contourf(x_coord, y_coord, frame['intensity'].T)
        plt.contourf(x_coord, y_coord, frame['intensity'].T)#, levels=[8, 16])

    plt.show(block=True)


def polar_ppi(frames):
    if isinstance(frames, xr.Dataset):
        frames = [frames]

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    #ax.set_rlim(0, 15_000)
    for frame in frames:
        # Compute degree increments
        _spoke_steps = np.diff(frame['spoke_number'].values)
        split_indices = np.where((_spoke_steps != 1))[0]
        if split_indices.any():
            print(frame['spoke_number'].values)
            split_indices = split_indices + 1
            split_frame = []
            start_idx = 0

            for split_idx in split_indices:
                split_frame.append(frame.isel(spoke_number=slice(start_idx, split_idx)))
                start_idx = split_idx

            # Add the remaining portion after the last split
            split_frame.append(frame.isel(spoke_number=slice(start_idx, None)))

            for sf in split_frame:
                ax.contourf(sf['azimuth'], sf['radius'], sf['intensity'].T)
        else:
            ax.contourf(frame['azimuth'], frame['radius'], frame['intensity'].T)

    plt.show(block=True)


if __name__ == '__main__':
    data_directory = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\"
    out_data_directory = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\frames"
    Path(out_data_directory).mkdir(parents=True, exist_ok=True)
    rawfiles = list(Path(data_directory).glob('*.raw'))

    from piradar.tools.read_data import convert_rawsector_v0_to_raw_frames
    import time

    for raw_file in rawfiles:
        convert_rawsector_v0_to_raw_frames(raw_file, out_dir=out_data_directory, freq=10)

