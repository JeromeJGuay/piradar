import datetime
from pathlib import Path
import pandas as pd


def make_raw_file_index(station, root_dir, out_dir):
    file_index = []

    for rf in Path(root_dir).rglob("*.raw"):
        scan_ts = datetime.datetime.strptime(rf.stem.split("_")[0], "%Y%m%dT%H%M%S")

        file_index.append([station, scan_ts, rf])

    df = pd.DataFrame(file_index, columns=['station', 'timestamp', 'path'])

    df.to_csv(Path(out_dir).joinpath(f'{station}_raw_index.csv'), index=False)


def load_raw_file_index(path) -> pd.DataFrame:
    required_cols = ["station", "timestamp", "path"]

    dataframe = pd.read_csv(path)

    for col in required_cols:
        if not col in dataframe:
            raise ValueError(f"On or more column is missing from raw index file. Required: {required_cols}")
    return dataframe


def sel_raw_file_by_time(dataframe: pd.DataFrame, start_time: str = None, end_time: str = None) -> pd.DataFrame:
    dataframe['timestamp'] = dataframe['timestamp'].astype("datetime64[s]")
    dataframe = dataframe[
        dataframe['timestamp'].between(
            start_time or dataframe['timestamp'].min(), end_time or dataframe['timestamp'].max()
        )
    ]

    if dataframe.empty:
        raise ValueError("No values exist for the given start_time and end_time")

    return dataframe


if __name__ == "__main__":
    out_dir = r"E:\OPP\ppo-qmm_analyses\data\radar"

    station = "ivo"

    starp_stop_times = {
        "ive": ("2025-06-13T14:30:00", "2025-07-30T13:18:00"),
        "ivo": ("2025-06-13T17:55:00", "2025-07-30T14:13:00"),
        "ir": ("2025-06-06T16:52:00", "2025-07-25T18:13:00"),
        "iap": ("2025-06-05T21:55:00", "2025-07-16T12:00:00")
    }

    data_directories = {
        "ive": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ive_2025-07-30\data",
        "ivo": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ivo_2025-07-30\data",
        "ir": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\ir_2025-07-25\data",
        "iap": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\iap_2025-07-16\data",
    }

    #for station, root_dir in data_directories.items():
    #    make_raw_file_index(station=station, root_dir=root_dir, out_dir=out_dir)

    # indexf = Path(out_dir).joinpath(f'{station}_raw_index.csv')
    #
    # start_time, end_time = starp_stop_times[station]
    # df = load_raw_file_index(indexf)
    #
    # df = sel_raw_file_by_time(df, start_time, end_time)
