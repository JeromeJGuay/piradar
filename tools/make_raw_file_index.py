from pathlib import Path
from tools.processing_utils import make_raw_file_index

root_dirs = {
    "__station__name__" : "__path_to_raw_file__"
}

for station, sub_dir in root_dirs.items():
    make_raw_file_index(
        station=station,
        root_dir="__path_to_raw_file__",
        out_dir=r"__out__dir__root__"
    )