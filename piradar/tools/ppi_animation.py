import time
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from piradar.tools.read_data import read_raw

import os
from matplotlib.animation import FuncAnimation
from glob import glob

# Directory to watch for new files
data_directory = "C:\\Users\\guayj\\Desktop\\tmp"

raw_dir_path = Path(data_directory)
processed_dir_path = raw_dir_path.joinpath("processed")
processed_dir_path.mkdir(exist_ok=True)

# Initialize the radar figure
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rlim(0, 15_000)


FADING_RATE = 0.25  # 25% per refresh cycle
REFRESH_RATE = 1000  # 1 seconds

radar_plot = None
previous_radar_plots = []
no_new_ppi_counter = 0

min_range = 100
auto_range = True
max_radius = None
max_range = 75_000


def fade_radar_plot():
    global previous_radar_plots

    for plot in previous_radar_plots:
        #for collection in plot.collections:
        alpha = max(plot.get_alpha() - FADING_RATE, 0)
        plot.set_alpha(alpha)

    # Remove fully transparent plots from the axis
    for plot in previous_radar_plots[:]:  # Iterate over a copy of the list
        if plot.get_alpha() == 0:
            plot.remove()
            previous_radar_plots.remove(plot)


def set_range(radius):
    if radius is not None:
        ax.set_rlim(0, radius)  # Set custom range


def increase_range(event):
    global auto_range
    auto_range = False
    current_radius = ax.get_ylim()[1]
    set_range(min(2 * current_radius, 75_000))
    plt.draw()


def decrease_range(event):
    global auto_range
    auto_range = False
    current_radius = ax.get_ylim()[1]
    set_range(max(round(current_radius / 2), 100))
    plt.draw()


# Button callback for auto range
def auto_range_callback(event):
    global auto_range
    auto_range = True
    if max_radius:
        set_range(radius=max_radius)
    plt.draw()



# Add buttons ZOOM
ax_decrease_button = plt.axes([0.7-0.04-0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]
decrease_zoom_button = Button(ax_decrease_button, '-')

ax_auto_button = plt.axes([0.7, 0.01, 0.1, 0.05])
auto_zoom_button = Button(ax_auto_button, 'Auto')

ax_increase_button = plt.axes([0.7+0.1+0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]
increase_zoom_button = Button(ax_increase_button, '+')


# Assign the callback functions
decrease_zoom_button.on_clicked(increase_range)
auto_zoom_button.on_clicked(auto_range_callback)
increase_zoom_button.on_clicked(decrease_range)

# Initial range setting
set_range(radius=None)


def update_data(frame):
    global radar_plot, previous_radar_plots, max_radius

    fade_radar_plot()

    # Get the list of files in the directory
    raw_files = sorted(list(raw_dir_path.glob("*.raw")))

    if not raw_files:
        ax.set_title("Radar PPI - No PPI")
        return radar_plot  # No files available

    oldest_file = raw_files.pop(0)

    timestamp, azimuth, radius, data = read_raw(oldest_file, is4bits=False)

    max_radius = radius.max()

    data[data < 1] = np.nan
    azimuth_rad = np.radians(azimuth)

    # no_new_ppi_counter += 1
    # if no_new_ppi_counter > 2:
    #     ax.set_rlim(0, 10_000)
    # if auto_range is True:
    #     ax.set_rlim(0, np.round(max_radius))
    # if zoom == "auto": ## DO something like this


    radar_plot = ax.contourf(azimuth_rad, radius, data.T, levels=15, cmap="viridis", alpha=1)
    previous_radar_plots.append(radar_plot)

    ax.set_title(f"Radar PPI - {timestamp[0]}")

    oldest_file.rename(processed_dir_path / oldest_file.name)  # Move processed file to other directory

    return radar_plot


# Create the animation
ani = FuncAnimation(fig, update_data, interval=REFRESH_RATE,cache_frame_data=False)  # Check every second

# Display the radar plot
plt.show(block=True)