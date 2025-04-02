"""
    def write_raw_sector_data(self, raw_data_output_file: str, sector_data: SectorData):
        with open(raw_data_output_file, "ba") as f:
            packed_frame_header = b"FH" + struct.pack(
                "<LBHHH",
                sector_data.time,
                sector_data.number_of_spokes,
                sector_data.spoke_data[0]._range,  #
                sector_data.spoke_data[0].heading, # should not change but ok
                self.reports.setting.gain,
            )
            f.write(packed_frame_header)
            for spoke_data in sector_data.spoke_data:
                packed_spoke_data = b"SD" + struct.pack(
                    "<HH512B",
                    spoke_data.spoke_number,
                    spoke_data.angle,
                    *spoke_data.intensities
                )

                f.write(packed_spoke_data)

 def unpack_4bit_gray_scale(self, data):

     data_4bit = []
     for _bytes in data:
         low_nibble = _bytes & 0x0F
         high_nibble = (_bytes >> 4) & 0x0F

         data_4bit.extend([low_nibble, high_nibble])

     return data_4bit

"""
import numpy as np
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from pathlib import Path

path = "E:\\radar"

filename = "ppi_data.txt"

frame_delimiter = "FH:"
spoke_delimiter = "SH:"
data_delimiter = "SD:"

frames = []


with open(Path(path).joinpath(filename), "r") as file:
    for line in file.readlines():
        if line.startswith(frame_delimiter):
            _time, nspoke = line.strip("\n").split(frame_delimiter)[-1].split(',')
            frames.append({"time": _time, 'nspoke': nspoke, 'spokes': []})

        if line.startswith(spoke_delimiter):
            _spoke_number, angle, _range = line.strip("\n").split(spoke_delimiter)[-1].split(",")


            frames[-1]['spokes'].append({
                "spoke_number": int(_spoke_number),
                "angle": round(float(angle), 2),
                "range": round(float(_range), 2),
                "data": None
            })

        if line.startswith(data_delimiter):
            frames[-1]['spokes'][-1]['data'] = np.array(line.strip("\n").split(data_delimiter)[-1].split(","), dtype=int)



timestamp = None
grouped_frame = {}
for frame in frames:
    if frame['time'] not in grouped_frame:
        grouped_frame[frame['time']] = {
            'spoke_number': [],
            'angle': [],
            'data': []
        }
    for spoke in frame['spokes']:
        grouped_frame[frame['time']]['spoke_number'].extend([spoke['spoke_number']])
        grouped_frame[frame['time']]['angle'].extend([spoke['angle']])
        grouped_frame[frame['time']]['data'].extend([spoke['data']])
        grouped_frame[frame['time']]['range'].extend([spoke['range']])

timestamps = list(grouped_frame.keys())


radius = np.linspace(0, 100, 1024)


for j in range(3):
    frame_id = 5+j
    sector = grouped_frame[timestamps[frame_id]]
    azim = np.deg2rad(sector['angle'])
    for i in range(len(sector['data'])):
        data = sector['data'][i]
        mask = data > 0
        x = radius[mask] * np.cos(azim[i])
        y = radius[mask] * np.sin(azim[i])
        plt.scatter(x, y, c='g', alpha=0.05*data[mask]/15, s=20, linewidths=0)

plt.xlim([-10, 10])
plt.ylim([-10, 10])
plt.show(block=True)




