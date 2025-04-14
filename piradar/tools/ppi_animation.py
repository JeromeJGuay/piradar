import time
from pathlib import Path

import numpy as np
import matplotlib as mpl

mpl.use('Qt5Agg')
import matplotlib.pyplot as plt

from piradar.tools.read_data import read_raw

import os
from matplotlib.animation import FuncAnimation
from glob import glob

# Directory to watch for new files
data_directory = "C:\\Users\\guayj\\Desktop\\tmp"

# Initialize the radar figure
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
radar_plot = None


def update_data(frame):
    global radar_plot

    # Get the list of files in the directory
    files = sorted(glob(os.path.join(data_directory, "*.raw")))
    if not files:
        return radar_plot  # No files available

    # Pick the latest file
    latest_file = files[-1]

    # Read the data using the existing read_raw function
    timestamp, azimuth, radius, data = read_raw(latest_file, is4bits=False)

    #data[data < 1] = np.nan

    # Convert azimuth degrees to radians for polar plot
    azimuth_rad = np.radians(azimuth)

    # Clear previous plot and update with new data
    ax.clear()
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    radar_plot = ax.contourf(azimuth_rad, radius, data.T, cmap="viridis")
    #radar_plot = ax.pcolor(azimuth_rad, radius, data, shading="auto", cmap="viridis")

    ax.set_title(f"Radar PPI - {timestamp[0]}")

    return radar_plot


# Create the animation
ani = FuncAnimation(fig, update_data, interval=1000)  # Check every second

# Display the radar plot
plt.show(block=True)