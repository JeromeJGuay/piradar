import datetime
from pathlib import Path
import pandas as pd


def make_raw_file_index(station, root_dir, out_dir):

    file_index = []

    for rf in Path(root_dir).rglob("*.raw"):

        scan_ts = datetime.datetime.strptime(rf.name.split("_")[0], "%Y%m%dT%H%M%S")

        file_index.append([station, scan_ts, rf])

    df = pd.DataFrame(file_index, columns=['station', 'timestamp', 'path'])
    df.to_csv(Path(out_dir).joinpath(f'{station}_raw_index.csv'))


if __name__ == "__main__":

    out_dir = r"E:\OPP\ppo-qmm_analyses\data\radar"

    station = "ivo"

    data_directories = {
        "ive": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ive_2025-07-30\data",
        "ivo": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\test_ivo_2025-07-30\data",
        "ir": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\ir_2025-07-25\data",
        "iap": r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023\iap_2025-07-16\data",
    }

    for station, root_dir in data_directories.items():
        make_raw_file_index(station=station, root_dir=root_dir, out_dir=out_dir)

