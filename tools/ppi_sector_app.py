from pathlib import Path


import numpy as np
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from matplotlib.animation import FuncAnimation

from tools.read_data import read_raw

class PpiLivePlotter:
    min_range = 100
    max_range = 75_000

    def __init__(self, data_directory, fading_time=5, refresh_rate=.5, is_polar=True):
        self.data_directory = data_directory

        self.is_polar = is_polar

        self.refresh_rate = refresh_rate * 1000

        self.fading_rate = (refresh_rate / fading_time)

        self.radar_plot = None
        self.previous_radar_plots = []

        self.is4bits = True

        self.auto_range = True
        self.max_radius = None

        self.file_id = 0# put back at 0
        self.files_list = self.get_new_files()

        ### PLOT ###
        if self.is_polar:
            self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
            self.ax.set_theta_zero_location("N")
            self.ax.set_theta_direction(-1)
            self.ax.set_rlim(0, 15_000)
        else:
            self.fig, self.ax = plt.subplots()
            rlim = 15_000
            self.ax.set_xlim(-rlim, rlim)
            self.ax.set_ylim(-rlim, rlim)

        self.ax_4bits_button = plt.axes([0.2, 0.01, 0.2, 0.05])  # Position: [left, bottom, width, height]
        self.ax_decrease_button = plt.axes([0.7 - 0.04 - 0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]
        self.ax_auto_button = plt.axes([0.7, 0.01, 0.1, 0.05])
        self.ax_increase_button = plt.axes([0.7 + 0.1 + 0.005, 0.01, 0.04, 0.05])  # Position: [left, bottom, width, height]

        self._4bits_button = Button(self.ax_4bits_button, "4bit" if self.is4bits else "8bit")
        self.decrease_zoom_button = Button(self.ax_decrease_button, '-')
        self.auto_zoom_button = Button(self.ax_auto_button, 'Auto')
        self.increase_zoom_button = Button(self.ax_increase_button, '+')

        # Assign the callback functions
        self.decrease_zoom_button.on_clicked(self.increase_range_callback)
        self.auto_zoom_button.on_clicked(self.auto_range_callback)
        self.increase_zoom_button.on_clicked(self.decrease_range_callback)
        self._4bits_button.on_clicked(self.toggle_4bits_callback)

        self.ani = FuncAnimation(self.fig, self.update_data, interval=self.refresh_rate, cache_frame_data=False)

        plt.show(block=True)

    def get_new_files(self):
        #return sorted(list(Path(self.data_directory).rglob("*.raw")))
        #return sorted(list(Path(self.data_directory).rglob("*[1-3].raw")))
        return sorted(list(Path(self.data_directory).rglob("*2.raw")))

    def fade_radar_plot(self):
        for plot in self.previous_radar_plots:
            alpha = max(plot.get_alpha() - self.fading_rate, 0)
            plot.set_alpha(alpha)

        for plot in self.previous_radar_plots[:]:  # Iterate over a copy of the list
            if plot.get_alpha() == 0:
                plot.remove()
                self.previous_radar_plots.remove(plot)

    def set_range(self, radius):
        if radius is not None:
            if self.is_polar:
                self.ax.set_rlim(0, radius)
            else:
                self.ax.set_xlim(-radius, radius)
                self.ax.set_ylim(-radius, radius)

    def increase_range_callback(self, event):
        self.auto_range = False
        current_radius = self.ax.get_ylim()[1]
        self.set_range(min(2 * current_radius, 75_000))
        plt.draw()

    def decrease_range_callback(self, event):
        self.auto_range = False
        current_radius = self.ax.get_ylim()[1]
        self.set_range(max(round(current_radius / 2), 100))
        plt.draw()

    def auto_range_callback(self, event):
        self.auto_range = True
        if self.max_radius:
            self.set_range(radius=self.max_radius)
        plt.draw()

    def toggle_4bits_callback(self, event):
        self.is4bits = not self.is4bits  # Toggle the value
        self._4bits_button.label.set_text("4bits" if self.is4bits else "8bits")  # Update button label
        plt.draw()  # Redraw the button with the new label

    def update_data(self, frame):

        self.fade_radar_plot()

        if self.file_id == len(self.files_list):
            return None

        raw_file = self.files_list[self.file_id]
        self.file_id += 1
        self.ax.set_title(f"Radar PPI - {Path(raw_file).name}")

        frame = read_raw(raw_file, is4bits=self.is4bits, merge=True)
        #frame=frame.isel(spoke_number=slice(0, 2048))

        if not frame:
            return None

        #for frame in frames:
        self.max_radius = float(frame.attrs['max_range'])

        data = frame['intensity'].values.astype(float)
        data[data < 1] = np.nan

        heading=-10
        frame['azimuth'] = frame['azimuth'] - np.deg2rad(heading)

        if self.is_polar:
            radar_plot = self.ax.contourf(
                frame['azimuth'], frame['radius'], data.T,
                levels=16 if self.is4bits else 256, cmap="viridis", alpha=1
            )
        else:
            x_coord = frame['radius'] * np.sin(frame['azimuth'])
            y_coord = frame['radius'] * np.cos(frame['azimuth'])

            radar_plot = self.ax.contourf(
                x_coord, y_coord, data.T,
            levels=16 if self.is4bits else 256, cmap="viridis", alpha=1
            )

        self.previous_radar_plots.append(radar_plot)

        return radar_plot


if __name__ == "__main__":
    #data_directory = "\\\\capteur-desktop\\2To\\data\\20250512"
    #data_directory = "D:\\data\\20250522\\18"
    #data_directory = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\test_2025-05-05\\processed"
    # data_directory = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\frames"
    #data_directory = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\test_2025-05-05"
    data_directory = r"C:\Users\guayj\Documents\workspace\data\radar_2025-07-30\10km\ivo\data\20250730\17"
    plp = PpiLivePlotter(
        data_directory=data_directory,
        fading_time=.5,
        refresh_rate=1,
        is_polar=True
    )

