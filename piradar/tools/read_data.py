"""
void NavicoReceive::InitializeLookupData() {
  if (lookupData[5][255] == 0) {
    for (int j = 0; j <= UINT8_MAX; j++) {
      uint8_t low = lookupNibbleToByte[(j & 0x0f)];
      uint8_t high = lookupNibbleToByte[(j & 0xf0) >> 4];

      lookupData[LOOKUP_SPOKE_LOW_NORMAL][j] = (uint8_t)low;
      lookupData[LOOKUP_SPOKE_HIGH_NORMAL][j] = (uint8_t)high;

      switch (low) {
        case 0xf4:
          lookupData[LOOKUP_SPOKE_LOW_BOTH][j] = 0xff;
          lookupData[LOOKUP_SPOKE_LOW_APPROACHING][j] = 0xff;
          break;

        case 0xe8:
          lookupData[LOOKUP_SPOKE_LOW_BOTH][j] = 0xfe;
          lookupData[LOOKUP_SPOKE_LOW_APPROACHING][j] = (uint8_t)low;
          break;

        default:
          lookupData[LOOKUP_SPOKE_LOW_BOTH][j] = (uint8_t)low;
          lookupData[LOOKUP_SPOKE_LOW_APPROACHING][j] = (uint8_t)low;
      }

      switch (high) {
        case 0xf4:
          lookupData[LOOKUP_SPOKE_HIGH_BOTH][j] = 0xff;
          lookupData[LOOKUP_SPOKE_HIGH_APPROACHING][j] = 0xff;
          break;

        case 0xe8:
          lookupData[LOOKUP_SPOKE_HIGH_BOTH][j] = 0xfe;
          lookupData[LOOKUP_SPOKE_HIGH_APPROACHING][j] = (uint8_t)high;
          break;

        default:
          lookupData[LOOKUP_SPOKE_HIGH_BOTH][j] = (uint8_t)high;
          lookupData[LOOKUP_SPOKE_HIGH_APPROACHING][j] = (uint8_t)high;
      }
    }
  }
}
"""
import time
import random
from pathlib import Path
import struct
import datetime

import numpy as np
import xarray as xr

FRAME_DELIMITER = b"FH"
FRAME_HEADER_FORMAT = "<LBHHH"
FRAME_HEADER_SIZE = struct.calcsize(FRAME_HEADER_FORMAT) #11

SPOKE_DATA_DELIMITER = b"SD"
SPOKE_DATA_FORMAT = "<HH512B"
SPOKE_DATA_SIZE = struct.calcsize(SPOKE_DATA_FORMAT)


def read_raw(raw_file: str, is4bits: bool) -> tuple[np.array, np.array, np.array, np.array]:
    with open(raw_file, "rb") as f:
        raw_data = f.read()

    return load_raw_data(raw_data, is4bits=is4bits)


def load_raw_data(raw_data: bytes, is4bits=True):
    frames = []

    for rf in raw_data.split(FRAME_DELIMITER)[1:]:
        frames.append(load_frame_data(raw_frame=rf, is4bits=is4bits))

    return frames


def load_frame_data(raw_frame: bytes, is4bits=True) -> xr.Dataset:
    """
    spoke_data.angle = _spoke_angle * 360 / 4096  # 0..4096 = 0..360
    """

    #frame_header = struct.unpack(FRAME_HEADER, raw_frame[:FRAME_HEADER_SIZE])  # Size of <lBHHH is 11

    raw_header, raw_spokes = raw_frame.split(SPOKE_DATA_DELIMITER)

    unpacked_header = struct.unpack(FRAME_HEADER_FORMAT, raw_header)

    frame_data = {
        "spoke_number": [],
        "azimuth": [],
        "radius": np.linspace(0, unpacked_header[2], 1024 if is4bits else 512),
        "intensity": []
    }

    byte_pointer = 0
    while byte_pointer + SPOKE_DATA_SIZE <= len(raw_spokes):
        _raw_spoke = raw_spokes[byte_pointer: byte_pointer + SPOKE_DATA_SIZE]
        unpacked_spoke = struct.unpack(SPOKE_DATA_FORMAT, _raw_spoke)
        byte_pointer += SPOKE_DATA_SIZE

        frame_data["spoke_number"].append(unpacked_spoke[0])
        frame_data["azimuth"].append(unpacked_spoke[1] * 360 / 4096)

        if is4bits:
            frame_data["intensity"].append(unpack_4bit_gray_scale(unpacked_spoke[2:]))
        else:
            frame_data["intensity"].append(unpacked_spoke[2:])

    for k in ["spoke_number", "azimuth", "intensity"]:
        frame_data[k] = np.array(frame_data[k])

    time = ["nat"] * frame_data['azimuth'].shape[0]
    time[-1] = datetime.datetime.fromtimestamp(unpacked_header[0], datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
    time = np.array(time, dtype=np.datetime64)

    dataset = xr.Dataset(
        {
            "intensity": (["spoke_number", "radius"], frame_data["intensity"]),
            "time": (["spoke_number"], time)
        },
        coords={
            "spoke_number": frame_data["spoke_number"],
            "azimuth": ("spoke_number", np.deg2rad(frame_data["azimuth"])),
            "radius": frame_data["radius"],
        },
        attrs={
            "number_of_spoke": unpacked_header[1],
            "max_range": unpacked_header[2],
            "heading": unpacked_header[3] / 10,
            "gain": unpacked_header[4],
        }
    )

    return dataset


def unpack_4bit_gray_scale(data):
    data_4bit = []
    for _bytes in data:
        low_nibble = _bytes & 0x0F
        high_nibble = (_bytes >> 4) & 0x0F

        data_4bit.extend([high_nibble, low_nibble])

    return data_4bit


def convert_rawsector_v0_to_raw_frames(raw_file, out_dir, freq=10):
    #to update TODO
    with open(raw_file, "rb") as f:
        raw_data = f.read()

    frame_counter = 0
    for rf in raw_data.split(FRAME_DELIMITER)[1:]:
        frame_counter += 1

        frame_header = rf[:11]
        raw_spoke = b"".join(rf[11:].split(SPOKE_DATA_DELIMITER))

        _ts = datetime.datetime.fromtimestamp(struct.unpack(FRAME_HEADER_FORMAT, frame_header)[0], datetime.UTC).strftime("%Y%m%dT%H%M%S%f")
        print(_ts, frame_counter, struct.unpack(FRAME_HEADER_FORMAT, frame_header)[0])

        _spokes_number = []

        for rs in rf[11:].split(SPOKE_DATA_DELIMITER)[1:]:
            _spokes_number.append(struct.unpack(SPOKE_DATA_FORMAT, rs)[0])

        first_spoke = _spokes_number[0]
        last_spoke = _spokes_number[-1]

        filename = f"{_ts}_{first_spoke}_{last_spoke}"

        with open(Path(out_dir).joinpath(filename).with_suffix(".raw"), "wb") as f:
            f.write(FRAME_DELIMITER + frame_header + SPOKE_DATA_DELIMITER + raw_spoke)

        time.sleep(1/freq)