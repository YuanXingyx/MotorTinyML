"""Compare looseness-60 windows with normal-60 and overload-60 references."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Missing NumPy. Install numpy to run this diagnostic.") from exc

from dataset_audit import audit_csv


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
REPORT_PATH = REPORT_DIR / "looseness_60_reference_comparison.txt"
WINDOW_SIZE = 200
SAMPLE_RATE_HZ = 200.0
AXES = ("x", "y", "z")
FEATURE_NAMES = ["y_std", "y_rms", "y_peak_to_peak", "y_dominant_frequency", "y_dominant_amplitude", "y_spectral_centroid", "y_spectral_energy"]
FILES = {
    "looseness": [
        "mechanical_looseness_60_20260820_170815.csv",
        "mechanical_looseness_60_20260820_171323.csv",
        "mechanical_looseness_60_20260820_172224.csv",
    ],
    "normal": [
        "motor_normal_60_20260819_204215.csv",
        "motor_normal_60_20260819_230403.csv",
        "motor_normal_60_20260819_230612.csv",
    ],
    "overload": [
        "motor_overload_60_20260820_180954.csv",
        "motor_overload_60_20260820_181115.csv",
        "motor_overload_60_20260820_181249.csv",
    ],
}


def load_windows(path: Path) -> np.ndarray:
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"header mismatch: {reader.fieldnames!r}")
        for row in reader:
            rows.append([float(row[axis]) for axis in AXES])
    values = np.asarray(rows, dtype=np.float64)
    count = len(values) // WINDOW_SIZE
    if count == 0:
        raise ValueError("no complete 200-sample windows")
    return values[: count * WINDOW_SIZE].reshape(count, WINDOW_SIZE, 3)


def fft_features(signal: np.ndarray) -> tuple[float, float, float, float]:
    spectrum = np.abs(np.fft.rfft(signal - np.mean(signal))) / len(signal)
    if len(spectrum) > 2:
        spectrum[1:-1] *= 2.0
    frequencies = np.fft.rfftfreq(len(signal), d=1.0 / SAMPLE_RATE_HZ)
    non_dc = spectrum.copy()
    non_dc[0] = 0.0
    dominant = int(np.argmax(non_dc))
    energy = spectrum ** 2
    total_energy = float(np.sum(energy))
    centroid = float(np.sum(frequencies * energy) / total_energy) if total_energy else 0.0
    return float(frequencies[dominant]), float(spectrum[dominant]), centroid, total_energy


def window_features(windows: np.ndarray) -> np.ndarray:
    feature_rows = []
    for window in windows:
        y = window[:, 1]
        dominant_frequency, dominant_amplitude, centroid, energy = fft_features(y)
        feature_rows.append([
            float(np.std(y)),
            float(np.sqrt(np.mean(y ** 2))),
            float(np.ptp(y)),
            dominant_frequency,
            dominant_amplitude,
            centroid,
            energy,
        ])
    return np.asarray(feature_rows, dtype=np.float64)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def feature_summary(values: np.ndarray) -> list[str]:
    lines = []
    for index, name in enumerate(FEATURE_NAMES):
        column = values[:, index]
        lines.append(f"  {name}: mean={fmt(float(np.mean(column)))}, std={fmt(float(np.std(column)))}, min={fmt(float(np.min(column)))}, max={fmt(float(np.max(column)))}")
    return lines


def main() -> None:
    loaded: dict[str, list[tuple[str, np.ndarray]]] = {key: [] for key in FILES}
    for role, names in FILES.items():
        for name in names:
            path = RAW_DIR / name
            if not path.exists():
                raise FileNotFoundError(path)
            audit = audit_csv(path)
            if audit["status"] != "INCLUDED":
                raise ValueError(f"{name} is not INCLUDED according to dataset_audit.py: {audit['status']}")
            loaded[role].append((name, window_features(load_windows(path))))

    reference_windows = np.concatenate([features for role in ("normal", "overload") for _, features in loaded[role]])
    scale = np.std(reference_windows, axis=0)
    scale[scale == 0] = 1.0
    centroids = {role: np.mean(np.concatenate([features for _, features in loaded[role]]), axis=0) for role in ("normal", "overload", "looseness")}
    normalized_centroids = {role: centroid / scale for role, centroid in centroids.items()}

    lines = [
        "MotorTinyML Looseness-60 Reference Comparison",
        "=" * 50,
        "All files were required to be INCLUDED by dataset_audit.py.",
        "This is a diagnostic comparison only; no CSV is deleted, relabeled, or excluded automatically.",
        f"window_size: {WINDOW_SIZE}",
        f"sample_rate_hz: {SAMPLE_RATE_HZ}",
        "",
        "Reference distributions: normal_60 and overload_60",
        "-" * 44,
    ]
    for role in ("normal", "overload"):
        reference = np.concatenate([features for _, features in loaded[role]])
        lines.append(role + ":")
        lines.extend(feature_summary(reference))

    lines.extend(["", "Looseness run comparisons", "-" * 28])
    result_rows = []
    for name, features in loaded["looseness"]:
        run_centroid = np.mean(features, axis=0)
        distances = {role: float(np.linalg.norm((run_centroid - centroids[role]) / scale)) for role in ("normal", "overload", "looseness")}
        window_distances = np.stack([
            np.linalg.norm((features - centroids[role]) / scale, axis=1) for role in ("normal", "overload", "looseness")
        ], axis=1)
        nearest = np.argmin(window_distances, axis=1)
        counts = {role: int(np.sum(nearest == index)) for index, role in enumerate(("normal", "overload", "looseness"))}
        dominant_role = max(counts, key=counts.get)
        dominant_count = counts[dominant_role]
        if dominant_count >= 12:
            state = {"normal": "NORMAL_LIKE", "overload": "OVERLOAD_LIKE", "looseness": "DISTINCT_FROM_REFERENCES"}[dominant_role]
        elif dominant_count >= 8:
            state = "MIXED"
        else:
            state = "REVIEW"
        lines.extend([
            "", name,
            f"  centroid distance: normal={fmt(distances['normal'])}, overload={fmt(distances['overload'])}, looseness={fmt(distances['looseness'])}",
            f"  window nearest reference: closer_to_normal={counts['normal']}, closer_to_overload={counts['overload']}, closer_to_looseness_reference={counts['looseness']}",
            f"  diagnostic state: {state}",
            "  Y dominant frequency: mean=" + fmt(float(np.mean(features[:, 3]))) + ", std=" + fmt(float(np.std(features[:, 3]))) + ", range=" + fmt(float(np.min(features[:, 3]))) + ".." + fmt(float(np.max(features[:, 3]))),
        ])
        result_rows.append((name, distances, counts, state))

    lines.extend(["", "Reference Y dominant frequency", "-" * 34])
    for role in ("normal", "overload", "looseness"):
        all_features = np.concatenate([features for _, features in loaded[role]])
        values = all_features[:, 3]
        lines.append(f"{role}_60: mean={fmt(float(np.mean(values)))}, std={fmt(float(np.std(values)))}, range={fmt(float(np.min(values)))}..{fmt(float(np.max(values)))}")

    lines.extend(["", "Interpretation", "-" * 16,
                  "170815 model overload-like tendency: this tool can only report distance and window evidence; it does not establish an overload label.",
                  "172224 model normal-like tendency: proximity to a reference is diagnostic and does not change its looseness label.",
                  "171323 looseness recognition tendency: window-level nearest-reference counts show whether it is internally mixed or closer to the looseness reference.",
                  "Different distances may indicate different operating states, looseness strengths, or fixture conditions; they are not sufficient grounds for deleting data.",
                  "No evidence from this script authorizes re-collecting or excluding mechanical_looseness_60 files."])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Compared {sum(len(value) for value in loaded.values())} INCLUDED runs.")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Comparison failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
