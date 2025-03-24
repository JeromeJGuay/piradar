import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from queue import Queue
import threading


class RadarPPIPlot(QtWidgets.QMainWindow):
    def __init__(self, fading_rate=5):
        super().__init__()
        self.initUI()
        self.fading_rate = fading_rate
        self.dataQueue = Queue()
        self.scatterItems = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update plot every 100ms

        self.cleanup_timer = QtCore.QTimer()
        self.cleanup_timer.timeout.connect(self.update_fading_items)
        self.cleanup_timer.start(500)  # Update fading effect every 100ms

    def initUI(self):
        self.setWindowTitle("Radar PPI Plot")
        self.setGeometry(100, 100, 800, 800)

        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.plotWidget = pg.PlotWidget()
        self.layout.addWidget(self.plotWidget)

        self.plotWidget.setAspectLocked()

        # Remove axes
        self.plotWidget.hideAxis('bottom')
        self.plotWidget.hideAxis('left')

        # Add concentric circles and radial spokes
        self.add_concentric_circles()
        self.add_radial_spokes()  # Add radial spokes once here

        # Set fixed axis range
        self.plotWidget.setXRange(-100, 100)
        self.plotWidget.setYRange(-100, 100)

    def add_concentric_circles(self):
        for r in range(20, 101, 20):  # Radii of concentric circles
            circle = QGraphicsEllipseItem(-r, -r, 2 * r, 2 * r)
            circle.setPen(pg.mkPen('w', width=0.5))
            self.plotWidget.addItem(circle)

    def add_radial_spokes(self):
        for angle in range(0, 360, 30):  # Angles for radial spokes
            rad = np.deg2rad(angle)
            x = 100 * np.cos(rad)
            y = 100 * np.sin(rad)
            line = QGraphicsLineItem(0, 0, x, y)
            line.setPen(pg.mkPen('w', width=0.5))
            self.plotWidget.addItem(line)

    def update_plot(self):
        if not self.dataQueue.empty():
            data, max_range, angle = self.dataQueue.get()
            x, y, colors = self.polar_to_cartesian(data, max_range, angle)
            spots = [{'pos': (x[i], y[i]), 'brush': pg.mkBrush(colors[i]), 'size': 5, 'pen': None} for i in
                     range(len(x))]
            scatterItem = pg.ScatterPlotItem()
            scatterItem.setData(spots)
            self.plotWidget.addItem(scatterItem)
            self.scatterItems.append((scatterItem, spots))

    def polar_to_cartesian(self, data, max_range, angle):
        angle_rad = np.deg2rad(angle)
        ranges = np.linspace(0, max_range, len(data))
        x = ranges * np.cos(angle_rad)
        y = ranges * np.sin(angle_rad)

        # Filter out zero values
        mask = data <= 5
        x = x[mask]
        y = y[mask]
        data = data[mask]

        # Normalize data for alpha intensity
        min_val, max_val = 0, 15
        norm_data = (data - min_val) / (max_val - min_val)
        alphas = (norm_data * 255).astype(int)  # Scale alpha from 0 to 255

        # Create colors with varying alpha
        colors = [(0, 255, 0, alpha) for alpha in alphas]  # Green color with varying alpha

        return x, y, colors

    def update_fading_items(self):
        # Gradually decrease alpha of scatter items
        for scatterItem, spots in self.scatterItems:
            for spot in spots:
                new_alpha = max(spot['brush'].color().alpha() - self.fading_rate, 0)
                spot['brush'].setColor(pg.mkColor(0, 255, 0, new_alpha))
            scatterItem.setData(spots)

        # Remove items that are fully transparent
        self.scatterItems = [(item, spots) for item, spots in self.scatterItems if
                             not all(spot['brush'].color().alpha() == 0 for spot in spots)]

    def add_data(self, data, max_range, angle):
        self.dataQueue.put((data, max_range, angle))


class DataThread(threading.Thread):
    def __init__(self, radarPPI):
        threading.Thread.__init__(self)
        self.radarPPI = radarPPI
        self.running = True
        self.count = 0

    def run(self):
        while self.running:
            # Example data generation
            data = np.random.rand(100) * 15  # Random data between 0 and 15
            data[::10] = 0  # Set some values to 0 for testing
            max_range = 100
            #angle = np.random.rand() * 360  # Random angle between 0 and 360
            angle = self.count
            self.radarPPI.add_data(data, max_range, angle)

            self.count = (self.count + 5) % 360
            QtCore.QThread.msleep(100)  # Simulate delay between new data

    def stop(self):
        self.running = False


if __name__ == '__main__':
    fading_rate = 5  # Adjust the fading rate here
    app = QtWidgets.QApplication(sys.argv)
    radarPPI = RadarPPIPlot(fading_rate=fading_rate)
    radarPPI.show()

    # Start the data thread
    dataThread = DataThread(radarPPI)
    dataThread.start()


    def on_exit():
        dataThread.stop()
        dataThread.join()


    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec_())