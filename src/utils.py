"""
utils.py — Shared utility functions.

Covers:
  - Design base name extraction (strip extension)
  - Output filename construction following the naming convention
  - LogEntry dataclass
  - CSV log generation
  - Console progress printing
"""

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

def get_design_base_name(filename: str) -> str:
    return Path(filename).stem


def build_output_filename(base_name: str, mock_id: str, output_format: str) -> str:
    ext = output_format.lstrip(".")
    return f"{base_name}_{mock_id}.{ext}"


@dataclass
class LogEntry:
    design_name: str
    mock_id: str
    mock_label: str
    status: str
    output_filename: str = ""
    drive_file_id: str = ""
    error: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))


CSV_HEADERS = ["timestamp","design_name","mock_id","mock_label","status","output_filename","drive_file_id","error"]


def build_csv_log(entries: list) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_HEADERS, lineterminator="\n")
    writer.writeheader()
    for entry in entries:
        writer.writerow({"timestamp":entry.timestamp,"design_name":entry.design_name,"mock_id":entry.mock_id,"mock_label":entry.mock_label,"status":entry.status,"output_filename":entry.output_filename,"drive_file_id":entry.drive_file_id,"error":entry.error})
    return output.getvalue()


def print_summary(entries: list) -> None:
    total = len(entries)
    successes = sum(1 for e in entries if e.status == "SUCCESS")
    print(f"\n  Summary: {total} operations | {successes} succeeded | {total - successes} failed")


def print_progress(current: int, total: int, design_name: str) -> None:
    pct = int(current / total * 100)
    print(f"\n  [{pct}:3d}%  ({current}/{total})  Processing: {design_name}")
