from pathlib import Path
from tools.processing_utils import make_raw_file_index

root_path = Path(r"\\nas4\DATA\measurements\radars\2025-10-14_IML-2025-053_PPO_Perley")

root_dirs = {
    "iap": r"IAP",
    "ir": r"IR",
    "ive": r"IV-E",
    "ivo": r"IV-O",
}

for station, sub_dir in root_dirs.items():
    make_raw_file_index(
        station=station,
        root_dir=root_path.joinpath(sub_dir, 'data'),
        out_dir=r"E:\OPP\ppo-qmm_analyses\data\radar_2025-10-14"
    )