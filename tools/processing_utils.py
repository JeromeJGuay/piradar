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


def sel_file_by_time_slice(dataframe: pd.DataFrame, start_time: str = None, end_time: str = None) -> pd.DataFrame:

    if "timestamp" in dataframe:
        dataframe['timestamp'] = dataframe['timestamp'].astype("datetime64[s]")
        dataframe = dataframe[
            dataframe['timestamp'].between(
                start_time or dataframe['timestamp'].min(), end_time or dataframe['timestamp'].max()
            )
        ]
    elif "start_time" in dataframe and 'end_time' in dataframe:
        dataframe['start_time'] = dataframe['start_time'].astype("datetime64[s]")
        dataframe['end_time'] = dataframe['end_time'].astype("datetime64[s]")
        dataframe = dataframe[
            ((start_time or dataframe['start_time'].min()) <= dataframe['end_time'])
            &
            ((end_time or dataframe['end_time'].max()) >= dataframe['start_time'])
        ]
    else:
        raise ValueError("`timestamps` or `start_time` and `end_time` are required to slice.")

    if dataframe.empty:
        raise ValueError("No values exist for the given start_time and end_time")

    return dataframe
