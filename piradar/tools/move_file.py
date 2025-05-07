import time
import shutil

from pathlib import Path

"C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\test_2025-05-05\\processed"
in_dir = Path("C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\test_2025-05-05\\processed")
#in_dir = Path("D:\\data")
out_dir = Path("C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\test_2025-05-05")

while True:
    for f in sorted(list(in_dir.glob("*.raw"))):
        print(f, out_dir / f.name)
        shutil.copyfile(f, out_dir / f.name)
        time.sleep(1)
