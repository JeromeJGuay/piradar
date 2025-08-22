from pathlib import Path
from processing_L0 import radar_processing_L0

if __name__ == "__main__":
    root_path = Path(r"E:\OPP\ppo-qmm_analyses\data\radar_2")

    stations_metadata = {
        'ive': {
            'raw_file_index': 'ive_raw_index.csv',
            'start_time': '2025-06-13T14:30:00',
            'end_time': '2025-07-30T13:18:00',
            'heading': 103.0,
            'lon': -69.423985,
            'lat': 48.051246,
            'time_offset': 0
        },
        'ivo': {
            'raw_file_index': 'ivo_raw_index.csv',
            'start_time': '2025-06-13T17:55:00',
            'end_time': '2025-07-30T14:13:00',
            'heading': -42.0,
            'lon': -69.483108,
            'lat': 47.995305,
            'time_offset': 0
        },
        'ir': {
            'raw_file_index': 'ir_raw_index.csv',
            'start_time': '2025-06-06T16:52:00',
            'end_time': '2025-07-25T18:13:00',
            'heading': -26.5,
            'lon': -69.554446,
            'lat': 48.069522,
            'time_offset': 39
        },
        'iap': {
            'raw_file_index': 'iap_raw_index.csv',
            'start_time': '2025-06-05T21:55:00',
            'end_time': '2025-07-16T12:00:00',
            'heading': -98.5,
            'lon': -69.321692,
            'lat': 48.106456,
            'time_offset': 0
        }
    }

    for station, metadata in stations_metadata.items():
        print(f"L0 Processing | station: {station}")
        radar_processing_L0(
            raw_file_index=root_path.joinpath(metadata['raw_file_index']),
            out_root_dir=root_path.joinpath('L0'),
            station=station,
            start_time=metadata['start_time'],
            end_time=metadata['end_time'],
            heading=metadata['heading'],
            lat=metadata['lat'],
            lon=metadata['lon'],
        )
