import struct
from pathlib import Path

from piradar.navico.navico_structure import *

#path = "C:\\Users\\guayj\\Documents\\workspace\\data\\radar_test_data\\report"
#path= "D:\\report"
path= "D:\\2025-05-13-bk\\report"

raw_reports = list(Path(path).glob("*.raw"))

_map = {
    "raw_report_0x12c4.raw": RadarReport12C4,
    "raw_report_0x1c4.raw": RadarReport01C4,
    "raw_report_0x2c4.raw": RadarReport02C4,
    "raw_report_0x3c4.raw": RadarReport03C4,
    "raw_report_0x4c4.raw": RadarReport04C4,
    "raw_report_0x6c4.raw": RadarReport06C4,
    "raw_report_0x8c4.raw": RadarReport08C4,
}

u_reports = {}

for raw_report in raw_reports:
    with open(raw_report, "rb") as f:
        u_reports[raw_report.name] = _map[raw_report.name](b''.join(f.readlines())).__dict__

for name, ur in u_reports.items():
    print(name)
    for k,v in ur.items():
        print("  ", k, v)
