from pathlib import Path

from processing_L1 import radar_processing_L1


if __name__ == "__main__":
    root_path = Path(r"_output_root_dir__") ### CHANGE HERE ##

    stations = ["_station_"] ### change here ###

    for station in stations:
        print(f"L1 Processing | station: {station}")
        L0_file_index = root_path.joinpath("L0", f'{station}_L0_index.csv')
        if not L0_file_index.is_file():
            print(f"No L0_file_index for {station}")
            continue
        radar_processing_L1(
            station=station,
            L0_file_index=L0_file_index,
            out_root_dir=root_path,
        )
