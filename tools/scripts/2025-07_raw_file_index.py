from pathlib import Path
from tools.processing_utils import make_raw_file_index

root_path = Path(r"\\nas4\DATA\measurements\radars\2025-05_IML-2025-023")

root_dirs = {
    "iap": r"iap_2025-07-16",
    "ir": r"ir_2025-07-25",
    "ive": r"test_ive_2025-07-30",
    "ivo": r"test_ivo_2025-07-30",
}

for station, sub_dir in root_dirs.items():
    make_raw_file_index(
        station=station,
        root_dir=root_path.joinpath(sub_dir, 'data'),
        out_dir=r"E:\OPP\ppo-qmm_analyses\data\radar_2025-07-25"
    )