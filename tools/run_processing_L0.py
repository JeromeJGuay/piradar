from pathlib import Path
from processing_L0 import radar_processing_L0

if __name__ == "__main__":
    root_path = Path(r"__output_root_dir__") ### CHANGE HERE ###

    stations_metadata = { ### change here ####
        '__station__': {
            'start_time': '2025-06-13T14:30:00',
            'end_time': '2025-07-30T13:18:00',
            'heading': 103.0,
            'lon': -69.423985,
            'lat': 48.051246,
            'time_offset': 0
        }
    }

    for station, metadata in stations_metadata.items():
        print(f"L0 Processing | station: {station}")

        radar_processing_L0(
            raw_file_index=root_path.joinpath(f"{station}_raw_index.csv"),
            out_root_dir=root_path,
            station=station,
            start_time=metadata['start_time'],
            end_time=metadata['end_time'],
            heading=metadata['heading'],
            lat=metadata['lat'],
            lon=metadata['lon'],
            time_offset=metadata['time_offset']
        )
