"""Compare statistical consistency of raw dataset runs without changing data."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev

from dataset_audit import audit_csv


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_PATH = ROOT_DIR / "dataset" / "reports" / "run_consistency_report.txt"
FEATURE_NAMES = ["x_std", "y_std", "z_std", "x_p2p", "y_p2p", "z_p2p"]
TRAINING_CLASSES = {"normal", "rotor_unbalance", "mechanical_looseness", "overload"}


def read_run(path: Path) -> dict:
    values = {"x": [], "y": [], "z": []}
    timestamps = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        expected = ["timestamp_ms", "x", "y", "z"]
        if reader.fieldnames != expected:
            raise ValueError(f"header mismatch: {reader.fieldnames!r}")
        for row in reader:
            timestamps.append(int(row["timestamp_ms"]))
            for axis in values:
                values[axis].append(float(row[axis]))
    if len(timestamps) < 2:
        raise ValueError("fewer than two samples")
    intervals = [later - earlier for earlier, later in zip(timestamps, timestamps[1:])]
    if any(interval <= 0 for interval in intervals):
        raise ValueError("timestamp is not strictly increasing")
    stats = {}
    for axis, samples in values.items():
        stats[axis] = {
            "mean": mean(samples),
            "std": pstdev(samples),
            "min": min(samples),
            "max": max(samples),
            "peak_to_peak": max(samples) - min(samples),
        }
    average_interval = mean(intervals)
    stats.update(
        sample_count=len(timestamps),
        duration_s=(timestamps[-1] - timestamps[0]) / 1000.0,
        avg_interval_ms=average_interval,
        sampling_frequency_hz=1000.0 / average_interval if average_interval else 0.0,
    )
    return stats


def fmt(value) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def group_key(item: dict) -> str:
    return f"{item['class']}_{item['speed']}"


def feature_vector(item: dict) -> list[float]:
    return [
        item["stats"]["x"]["std"], item["stats"]["y"]["std"], item["stats"]["z"]["std"],
        item["stats"]["x"]["peak_to_peak"], item["stats"]["y"]["peak_to_peak"], item["stats"]["z"]["peak_to_peak"],
    ]


def analyze_group(items: list[dict]) -> dict:
    vectors = [feature_vector(item) for item in items]
    columns = list(zip(*vectors))
    averages = [mean(column) for column in columns]
    deviations = [pstdev(column) if len(column) > 1 else 0.0 for column in columns]
    normalized = []
    for vector in vectors:
        normalized.append([(value - avg) / deviation if deviation else 0.0 for value, avg, deviation in zip(vector, averages, deviations)])
    centroid = [mean(column) for column in zip(*normalized)] if normalized else [0.0] * len(FEATURE_NAMES)
    centroid_distances = [math.sqrt(sum((value - center) ** 2 for value, center in zip(vector, centroid))) for vector in normalized]
    pairwise = [[0.0 for _ in items] for _ in items]
    for left in range(len(items)):
        for right in range(left + 1, len(items)):
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(normalized[left], normalized[right])))
            pairwise[left][right] = pairwise[right][left] = distance
    median_distance = sorted(centroid_distances)[len(centroid_distances) // 2] if centroid_distances else 0.0
    for index, item in enumerate(items):
        item["centroid_distance"] = centroid_distances[index]
        item["normalized_features"] = normalized[index]
        item["status"] = "CONSISTENT"
        if len(items) >= 3 and median_distance > 0 and centroid_distances[index] > median_distance * 1.5:
            item["status"] = "POTENTIAL_OUTLIER"
        elif len(items) >= 3 and median_distance > 0 and centroid_distances[index] > median_distance * 1.2:
            item["status"] = "REVIEW"
    return {"means": averages, "stds": deviations, "normalized": normalized, "centroid_distances": centroid_distances, "pairwise": pairwise}


def render_group(lines: list[str], key: str, items: list[dict], analysis: dict) -> None:
    lines.extend(["", f"Group: {key}", "=" * (7 + len(key))])
    lines.append("feature means / std / CV:")
    for name, average, deviation in zip(FEATURE_NAMES, analysis["means"], analysis["stds"]):
        cv = deviation / abs(average) if abs(average) > 1e-12 else None
        lines.append(f"  {name}: mean={fmt(average)}, std={fmt(deviation)}, CV={fmt(cv)}")
    lines.append("runs:")
    for item in items:
        stats = item["stats"]
        lines.append(
            f"  {item['path'].name}: status={item['status']}, sample_count={stats['sample_count']}, "
            f"duration_s={fmt(stats['duration_s'])}, avg_interval_ms={fmt(stats['avg_interval_ms'])}, "
            f"sampling_frequency_hz={fmt(stats['sampling_frequency_hz'])}, "
            f"std=({fmt(stats['x']['std'])}, {fmt(stats['y']['std'])}, {fmt(stats['z']['std'])}), "
            f"p2p=({fmt(stats['x']['peak_to_peak'])}, {fmt(stats['y']['peak_to_peak'])}, {fmt(stats['z']['peak_to_peak'])}), "
            f"centroid_distance={fmt(item['centroid_distance'])}"
        )
    lines.append("pairwise normalized distance matrix:")
    lines.append("  " + " | ".join(item["path"].stem for item in items))
    for item, row in zip(items, analysis["pairwise"]):
        lines.append("  " + item["path"].stem + " | " + " | ".join(fmt(value) for value in row))
    if len(items) > 1:
        best_pair = min(((analysis["pairwise"][left][right], items[left], items[right]) for left in range(len(items)) for right in range(left + 1, len(items))), key=lambda value: value[0])
        lines.append(f"most similar pair: {best_pair[1]['path'].name} <-> {best_pair[2]['path'].name}, distance={fmt(best_pair[0])}")
    lines.append("Note: outlier flags are diagnostic only; no file is automatically removed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare consistency of dataset runs.")
    parser.add_argument("--diagnostic", nargs="*", default=[], help="Excluded CSV basenames to include for diagnostic comparison only.")
    args = parser.parse_args()
    diagnostic_names = set(args.diagnostic)
    items = []
    errors = []
    for path in sorted(RAW_DIR.glob("*.csv")):
        audit = audit_csv(path)
        is_diagnostic = path.name in diagnostic_names
        if audit["class"] not in TRAINING_CLASSES:
            continue
        if audit["status"] != "INCLUDED" and not is_diagnostic:
            continue
        try:
            item = {"path": path, "class": audit["class"], "speed": audit["speed"], "stats": read_run(path)}
            item["diagnostic_status"] = "EXCLUDED_FROM_TRAINING" if audit["status"] != "INCLUDED" else "INCLUDED"
            items.append(item)
        except (OSError, ValueError) as exc:
            errors.append(f"{path.name}: INVALID ({exc})")

    groups = defaultdict(list)
    for item in items:
        groups[group_key(item)].append(item)
    lines = [
        "MotorTinyML Run Consistency Report", "=" * 35,
        "Purpose: detect experimental run consistency; this is not a model-accuracy-based data selection tool.",
        "Training data was not modified, deleted, or reclassified.",
        "",
    ]
    for key in sorted(groups):
        official = [item for item in groups[key] if item["diagnostic_status"] == "INCLUDED"]
        diagnostic = [item for item in groups[key] if item["diagnostic_status"] != "INCLUDED"]
        analysis = analyze_group(groups[key])
        render_group(lines, key, groups[key], analysis)
        if diagnostic:
            lines.append("diagnostic candidates: " + ", ".join(item["path"].name for item in diagnostic) + " (EXCLUDED_FROM_TRAINING)")
        if key.startswith("mechanical_looseness_60") and official:
            lines.append("official 60% runs are compared together; excluded candidates are shown only diagnostically.")
    lines.extend(["", "重点 mechanical_looseness summary", "-" * 32])
    for key in ("mechanical_looseness_40", "mechanical_looseness_60"):
        if key in groups:
            flagged = [item["path"].name for item in groups[key] if item.get("status") != "CONSISTENT"]
            lines.append(f"{key}: centroid distances and most similar pair are reported above; review candidates={flagged or 'none'}")
    if "mechanical_looseness_60" in groups and any(item["path"].stem.endswith("171626") for item in groups["mechanical_looseness_60"]):
        lines.append("171626: included only when explicitly requested with --diagnostic; remains EXCLUDED_FROM_TRAINING because it is an excluded/unstable-power-condition run.")
    if errors:
        lines.extend(["", "INVALID / unreadable files", *errors])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Compared {len(items)} runs across {len(groups)} class+speed groups.")
    print(f"Report: {REPORT_PATH}")
    if errors:
        print(f"WARNING: {len(errors)} file(s) could not be analyzed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Comparison failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
