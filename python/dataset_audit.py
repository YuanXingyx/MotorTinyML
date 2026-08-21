"""Audit raw MotorTinyML CSV datasets without modifying source data."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_PATH = ROOT_DIR / "dataset" / "reports" / "dataset_audit.txt"
WINDOW_SIZE = 200
EXPECTED_HEADER = ["timestamp_ms", "x", "y", "z"]

EXCLUDED_FILES = {
    "mechanical_looseness_60_20260820_171626.csv",
    "motor_overload_40_20260820_175006.csv",
    "motor_overload_40_20260820_175354.csv",
    "motor_overload_40_20260820_175538.csv",
    "motor_overload_60_20260820_180641.csv",
    "sensor_idle_20260814_211156.csv",
}

CLASS_PATTERNS = (
    ("motor_normal", "normal"),
    ("rotor_unbalance", "rotor_unbalance"),
    ("mechanical_looseness", "mechanical_looseness"),
    ("motor_overload", "overload"),
)
FILENAME_PATTERN = re.compile(
    r"^(motor_normal|rotor_unbalance|mechanical_looseness|motor_overload)_(40|60|80)(?:_|\.)"
)


def identify_file(path: Path) -> tuple[str | None, int | None]:
    """Return training class and speed parsed from a raw CSV filename."""
    match = FILENAME_PATTERN.match(path.name)
    if not match:
        return None, None
    prefix, speed_text = match.groups()
    class_name = dict(CLASS_PATTERNS)[prefix]
    return class_name, int(speed_text)


def audit_csv(path: Path) -> dict:
    result = {
        "file": path.name,
        "class": None,
        "speed": None,
        "status": "NON_TRAINING",
        "sample_count": 0,
        "avg_interval_ms": None,
        "sampling_frequency_hz": None,
        "complete_windows": 0,
        "discarded_samples": 0,
        "reason": "",
    }
    result["class"], result["speed"] = identify_file(path)

    if path.name in EXCLUDED_FILES:
        result["status"] = "EXCLUDED"
        result["reason"] = "explicit exclusion list"
    elif result["class"] is not None:
        result["status"] = "INCLUDED"
    elif path.name.startswith("sensor_idle_"):
        result["reason"] = "sensor_idle is a non-training baseline"
    else:
        result["reason"] = "filename does not match a supported training class"

    timestamps: list[int] = []
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames != EXPECTED_HEADER:
                result["status"] = "INVALID"
                result["reason"] = f"header mismatch: {reader.fieldnames!r}"
                return result
            for line_number, row in enumerate(reader, start=2):
                if any(row.get(field) in (None, "") for field in EXPECTED_HEADER):
                    raise ValueError(f"missing field at line {line_number}")
                timestamps.append(int(row["timestamp_ms"]))
                int(row["x"])
                int(row["y"])
                int(row["z"])
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        result["status"] = "INVALID"
        result["reason"] = str(exc)
        return result

    result["sample_count"] = len(timestamps)
    result["complete_windows"], result["discarded_samples"] = divmod(
        len(timestamps), WINDOW_SIZE
    )
    if len(timestamps) < 2:
        result["status"] = "INVALID"
        result["reason"] = "fewer than two timestamp samples"
        return result

    intervals = [later - earlier for earlier, later in zip(timestamps, timestamps[1:])]
    if any(interval <= 0 for interval in intervals):
        result["status"] = "INVALID"
        result["reason"] = "timestamp is not strictly increasing"
        return result

    result["avg_interval_ms"] = mean(intervals)
    result["sampling_frequency_hz"] = 1000.0 / result["avg_interval_ms"]
    return result


def format_number(value: float | int | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_summary(results: list[dict]) -> dict:
    summary = defaultdict(lambda: {"csv_count": 0, "total_samples": 0, "complete_windows": 0})
    for item in results:
        if item["status"] != "INCLUDED":
            continue
        entry = summary[item["class"]]
        entry["csv_count"] += 1
        entry["total_samples"] += item["sample_count"]
        entry["complete_windows"] += item["complete_windows"]
    return summary


def expected_warnings(summary: dict) -> list[str]:
    expected = {
        "normal": (9, 135),
        "rotor_unbalance": (6, 90),
        "mechanical_looseness": (6, 90),
        "overload": (6, 90),
    }
    warnings = []
    for class_name, (expected_csv, expected_windows) in expected.items():
        actual = summary.get(class_name, {})
        csv_count = actual.get("csv_count", 0)
        windows = actual.get("complete_windows", 0)
        if (csv_count, windows) != (expected_csv, expected_windows):
            warnings.append(
                f"{class_name}: expected {expected_csv} CSV/{expected_windows} windows, "
                f"found {csv_count} CSV/{windows} windows"
            )
    return warnings


def render_report(results: list[dict], summary: dict, warnings: list[str]) -> str:
    lines = ["MotorTinyML Dataset Audit", "=" * 26, ""]
    lines.append("Per-file audit")
    lines.append("-" * 26)
    for item in results:
        lines.append(
            f"{item['status']:12} {item['file']} | class={item['class'] or '-'} "
            f"speed={item['speed'] or '-'} samples={item['sample_count']} "
            f"interval_ms={format_number(item['avg_interval_ms'])} "
            f"frequency_hz={format_number(item['sampling_frequency_hz'])} "
            f"windows={item['complete_windows']} discarded={item['discarded_samples']}"
        )
        if item["reason"]:
            lines.append(f"  reason: {item['reason']}")

    lines.extend(["", "Included training summary", "-" * 26])
    lines.append("class | speed | csv_count | total_samples | complete_windows | excluded_csv_count")
    lines.append("-" * 80)
    excluded_by_class = defaultdict(int)
    for item in results:
        if item["status"] == "EXCLUDED" and item["class"]:
            excluded_by_class[item["class"]] += 1
    for class_name in ("normal", "rotor_unbalance", "mechanical_looseness", "overload"):
        entry = summary.get(class_name, {})
        speeds = sorted({item["speed"] for item in results if item["class"] == class_name and item["status"] == "INCLUDED"})
        lines.append(
            f"{class_name} | {','.join(map(str, speeds)) or '-'} | {entry.get('csv_count', 0)} | "
            f"{entry.get('total_samples', 0)} | {entry.get('complete_windows', 0)} | "
            f"{excluded_by_class[class_name]}"
        )
    total_csv = sum(entry.get("csv_count", 0) for entry in summary.values())
    total_windows = sum(entry.get("complete_windows", 0) for entry in summary.values())
    lines.extend(["", "Four-class training candidate total", f"CSV files: {total_csv}", f"Windows: {total_windows}"])
    lines.append("Classes: normal, rotor_unbalance, mechanical_looseness, overload")
    if warnings:
        lines.extend(["", "WARNING", "-" * 26, *warnings])
    else:
        lines.extend(["", "No differences from expected dataset counts."])
    return "\n".join(lines) + "\n"


def main() -> None:
    paths = sorted(RAW_DIR.rglob("*.csv")) if RAW_DIR.exists() else []
    results = [audit_csv(path) for path in paths]
    summary = build_summary(results)
    warnings = expected_warnings(summary)
    report = render_report(results, summary, warnings)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    included = sum(item["status"] == "INCLUDED" for item in results)
    invalid = sum(item["status"] == "INVALID" for item in results)
    excluded = sum(item["status"] == "EXCLUDED" for item in results)
    non_training = sum(item["status"] == "NON_TRAINING" for item in results)
    total_windows = sum(item["complete_windows"] for item in results if item["status"] == "INCLUDED")
    print(f"Audited {len(results)} CSV files: INCLUDED={included}, EXCLUDED={excluded}, "
          f"NON_TRAINING={non_training}, INVALID={invalid}")
    print(f"Four-class candidates: {included} CSV, {total_windows} windows")
    print(f"Report: {REPORT_PATH}")
    if warnings:
        print(f"WARNING: {len(warnings)} expected-count difference(s); see report.")


if __name__ == "__main__":
    main()
