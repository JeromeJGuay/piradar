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


# Initialize the radar figure
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rlim(0, 15_000)

FADING_RATE = 0.25  # 25% per refresh cycle
REFRESH_RATE = 1000  # 1 seconds

radar_plot = None
previous_radar_plots = []

is4bits = True
min_range = 100
auto_range = True
max_radius = None
max_range = 75_000

existing_files = set(glob(os.path.join(data_directory, "*.raw")))


def get_new_files():
    current_files = set(glob(os.path.join(data_directory, "*.raw")))
    new_files = current_files - existing_files

    existing_files.update(new_files)
    return sorted(new_files)


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

def increase_range_callback(event):
    global auto_range
    auto_range = False
    current_radius = ax.get_ylim()[1]
    set_range(min(2 * current_radius, 75_000))
    plt.draw()


def decrease_range_callback(event):
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


ax_4bits_button = plt.axes([0.2, 0.01, 0.2, 0.05])  # Position: [left, bottom, width, height]
_4bits_button = Button(ax_4bits_button, "4bit" if is4bits else "8bit")

def toggle_4bits_callback(event):
    global is4bits
    is4bits = not is4bits  # Toggle the value
    _4bits_button.label.set_text("4bits" if is4bits else "8bits")  # Update button label
    plt.draw()  # Redraw the button with the new label

# Add buttons ZOOM
ax_decrease_button = plt.axes([0.7-0.04-0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]
decrease_zoom_button = Button(ax_decrease_button, '-')

ax_auto_button = plt.axes([0.7, 0.01, 0.1, 0.05])
auto_zoom_button = Button(ax_auto_button, 'Auto')

ax_increase_button = plt.axes([0.7+0.1+0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]
increase_zoom_button = Button(ax_increase_button, '+')


# Assign the callback functions
decrease_zoom_button.on_clicked(increase_range_callback)
auto_zoom_button.on_clicked(auto_range_callback)
increase_zoom_button.on_clicked(decrease_range_callback)

_4bits_button.on_clicked(toggle_4bits_callback)

# Initial range setting
set_range(radius=None)


def update_data(frame):
    global radar_plot, previous_radar_plots, max_radius, is4bits

    fade_radar_plot()

    # Get the list of files in the directory

    raw_files = get_new_files()

    if not raw_files:
        ax.set_title("Radar PPI - No PPI")
        return radar_plot  # No files available

    latest = raw_files[-1]

    timestamp, azimuth, radius, data = read_raw(latest, is4bits=is4bits)

    max_radius = radius.max()

    data[data < 1] = np.nan
    azimuth_rad = np.radians(azimuth)

    radar_plot = ax.contourf(azimuth_rad, radius, data.T, levels=15, cmap="viridis", alpha=1)
    previous_radar_plots.append(radar_plot)

    ax.set_title(f"Radar PPI - {timestamp[0]}")

    #oldest_file.rename(processed_dir_path / oldest_file.name)  # Move processed file to other directory

    return radar_plot


# Create the animation
ani = FuncAnimation(fig, update_data, interval=REFRESH_RATE,cache_frame_data=False)  # Check every second

# Display the radar plot
plt.show(block=True)