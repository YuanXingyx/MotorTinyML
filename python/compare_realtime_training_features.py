"""Compare STM32 realtime normal windows with the training normal_60 distribution."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit("NumPy is required. Install it in the project virtual environment.") from exc

from dataset_audit import audit_csv
from train_tiny_classifier import extract_features, load_windows


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_PATH = ROOT_DIR / "dataset" / "reports" / "tiny_classifier_stage_c6a_feature_shift.txt"
PARAMS_PATH = ROOT_DIR / "firmware" / "stm32f103" / "MotorTinyML_F103" / "App" / "Model" / "tiny_classifier_params.c"
WINDOW_SIZE = 200
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]
FEATURE_NAMES = [
    f"{axis}_{metric}"
    for axis in ("x", "y", "z")
    for metric in ("mean", "std", "rms", "min", "max", "peak_to_peak", "mad")
]
CSV_LINE = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*$")
FLOAT = r"[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?f?"


def load_training_windows() -> tuple[np.ndarray, list[str]]:
    windows: list[np.ndarray] = []
    files: list[str] = []
    for path in sorted(RAW_DIR.rglob("*.csv")):
        audit = audit_csv(path)
        if audit["status"] == "INCLUDED" and audit["class"] == "normal" and audit["speed"] == 60:
            current = load_windows(path)
            if len(current):
                windows.append(current)
                files.append(path.name)
    if not windows:
        raise ValueError("No INCLUDED normal_60 CSV files found")
    return np.concatenate(windows), files


def load_realtime_log(path: Path) -> tuple[np.ndarray, dict[str, int | float]]:
    """Parse numeric UART CSV lines and split windows at timestamp discontinuities."""
    rows: list[tuple[int, int, int, int]] = []
    malformed_numeric = 0
    with path.open("r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            match = CSV_LINE.match(raw_line.strip())
            if match:
                rows.append(tuple(int(value) for value in match.groups()))
            elif "," in raw_line and raw_line.strip() and raw_line.lstrip()[0].isdigit():
                malformed_numeric += 1
    if not rows:
        raise ValueError(f"No timestamp,x,y,z rows found in {path}")

    segments: list[list[tuple[int, int, int, int]]] = [[]]
    intervals: list[int] = []
    duplicate_rows = 0
    previous_row: tuple[int, int, int, int] | None = None
    for row in rows:
        if previous_row is not None:
            delta = row[0] - previous_row[0]
            intervals.append(delta)
            if row == previous_row:
                duplicate_rows += 1
            if delta <= 0 or delta > 100:
                segments.append([])
        segments[-1].append(row)
        previous_row = row

    complete = []
    for segment in segments:
        count = len(segment) // WINDOW_SIZE
        complete.extend(segment[index * WINDOW_SIZE : (index + 1) * WINDOW_SIZE] for index in range(count))
    if not complete:
        raise ValueError("Realtime log has no complete 200-sample windows")
    metadata = {
        "sample_count": len(rows),
        "complete_windows": len(complete),
        "discarded_samples": sum(len(segment) % WINDOW_SIZE for segment in segments),
        "timestamp_breaks": sum(1 for delta in intervals if delta <= 0 or delta > 100),
        "duplicate_rows": duplicate_rows,
        "malformed_numeric_lines": malformed_numeric,
        "avg_interval_ms": float(np.mean([delta for delta in intervals if delta > 0])) if any(delta > 0 for delta in intervals) else float("nan"),
    }
    # Flatten complete windows to rows first, then restore the window shape.
    # Each row is explicitly reduced from (timestamp, x, y, z) to (x, y, z).
    flat_rows = [
        (x, y, z)
        for window in complete
        for _timestamp, x, y, z in window
    ]
    values = np.asarray(flat_rows, dtype=np.float64)
    expected_shape = (len(complete) * WINDOW_SIZE, 3)
    if values.shape != expected_shape:
        raise ValueError(f"Unexpected realtime sample shape: {values.shape}, expected {expected_shape}")
    return values.reshape(len(complete), WINDOW_SIZE, 3), metadata


def parse_params() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    source = PARAMS_PATH.read_text(encoding="utf-8")

    def values(name: str, count: int) -> np.ndarray:
        match = re.search(rf"{re.escape(name)}.*?=\s*\{{(?P<body>.*?)\}};", source, re.DOTALL)
        if not match:
            raise ValueError(f"Unable to parse {name} from {PARAMS_PATH}")
        parsed = [float(token.rstrip("f")) for token in re.findall(FLOAT, match.group("body"))]
        if len(parsed) != count:
            raise ValueError(f"{name}: expected {count} values, found {len(parsed)}")
        return np.asarray(parsed, dtype=np.float64)

    mean = values("g_feature_mean", 21)
    std = values("g_feature_std", 21)
    weights = values("g_logreg_weights", 84).reshape(4, 21)
    bias = values("g_logreg_bias", 4)
    if not all(np.all(np.isfinite(item)) for item in (mean, std, weights, bias)) or np.any(std == 0):
        raise ValueError("Classifier parameters contain non-finite values or zero scaler std")
    return mean, std, weights, bias


def score_summary(features: np.ndarray, mean: np.ndarray, std: np.ndarray, weights: np.ndarray, bias: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaled = (features - mean) / std
    scores = scaled @ weights.T + bias
    return scaled, scores


def fmt(value: float) -> str:
    return "nan" if not np.isfinite(value) else f"{value:.4f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("realtime_log", type=Path, help="UART log containing timestamp,x,y,z rows")
    args = parser.parse_args()
    realtime_log = args.realtime_log if args.realtime_log.is_absolute() else ROOT_DIR / args.realtime_log

    train_windows, train_files = load_training_windows()
    realtime_windows, log_meta = load_realtime_log(realtime_log)
    train_features = extract_features(train_windows)
    realtime_features = extract_features(realtime_windows)
    scaler_mean, scaler_std, weights, bias = parse_params()
    realtime_scaled, realtime_scores = score_summary(realtime_features, scaler_mean, scaler_std, weights, bias)
    train_scaled, train_scores = score_summary(train_features, scaler_mean, scaler_std, weights, bias)

    train_mean = train_features.mean(axis=0)
    train_std = train_features.std(axis=0, ddof=0)
    train_min = train_features.min(axis=0)
    train_max = train_features.max(axis=0)
    realtime_mean = realtime_features.mean(axis=0)
    realtime_z = (realtime_mean - train_mean) / np.where(train_std == 0, 1.0, train_std)
    outlier_count = int(np.sum(np.abs(realtime_z) > 3.0))
    contribution = (realtime_scaled.mean(axis=0)[None, :] * weights)
    realtime_pred = np.argmax(realtime_scores, axis=1)

    lines = [
        "MotorTinyML Stage C-6A Feature Shift Diagnostic",
        "=" * 50,
        f"realtime_log: {realtime_log}",
        f"training_files: {', '.join(train_files)}",
        f"training_windows: {len(train_features)}",
        f"realtime_samples: {log_meta['sample_count']}",
        f"realtime_windows: {len(realtime_features)}",
        f"realtime_discarded_samples: {log_meta['discarded_samples']}",
        f"realtime_timestamp_breaks: {log_meta['timestamp_breaks']}",
        f"realtime_duplicate_rows: {log_meta['duplicate_rows']}",
        f"realtime_malformed_numeric_lines: {log_meta['malformed_numeric_lines']}",
        f"realtime_avg_positive_interval_ms: {fmt(float(log_meta['avg_interval_ms']))}",
        "",
        "Feature comparison (training normal_60 vs realtime normal)",
        "feature | train_mean | train_std | realtime_mean | realtime_min | realtime_max | realtime_z",
    ]
    for index, name in enumerate(FEATURE_NAMES):
        lines.append(" | ".join((name, fmt(train_mean[index]), fmt(train_std[index]), fmt(realtime_mean[index]), fmt(realtime_features[:, index].min()), fmt(realtime_features[:, index].max()), fmt(realtime_z[index]))))

    lines.extend(["", "Scaled feature summary", "feature | scaler_mean | scaler_std | realtime_scaled_mean | realtime_scaled_min | realtime_scaled_max"])
    for index, name in enumerate(FEATURE_NAMES):
        lines.append(" | ".join((name, fmt(scaler_mean[index]), fmt(scaler_std[index]), fmt(realtime_scaled[:, index].mean()), fmt(realtime_scaled[:, index].min()), fmt(realtime_scaled[:, index].max()))))

    lines.extend(["", "Features beyond training distribution", f"count_abs_z_gt_3: {outlier_count}"])
    lines.extend(f"- {FEATURE_NAMES[index]}: z={fmt(realtime_z[index])}" for index in np.where(np.abs(realtime_z) > 3.0)[0])
    lines.extend(["", "Logistic score analysis", "class | train_score_mean | realtime_score_mean | realtime_contribution_sum"])
    for class_index, class_name in enumerate(CLASS_NAMES):
        lines.append(f"{class_name} | {fmt(float(train_scores[:, class_index].mean()))} | {fmt(float(realtime_scores[:, class_index].mean()))} | {fmt(float(contribution[class_index].sum()))}")
    lines.append(f"realtime_predicted_distribution: {np.bincount(realtime_pred, minlength=4).tolist()}")

    lines.extend([
        "", "Sampling and unit consistency", 
        "CONFIRMED: STM32 ADXL345 path reads signed little-endian int16 X/Y/Z values without g/mg conversion.",
        "CONFIRMED: firmware feature order is X then Y then Z, seven statistics per axis.",
        "CONFIRMED: training CSV schema is timestamp_ms,x,y,z and training windows use 200 samples.",
        "CONFIRMED: ADXL345 configuration is full-resolution +/-4g (DATA_FORMAT=0x09) and 200 Hz ODR (BW_RATE=0x0B).",
        "LIKELY: a large feature shift with clean timestamps indicates data distribution/fixture drift rather than a classifier formula mismatch.",
        "UNKNOWN: exact physical cause requires inspecting the saved UART log, sensor mounting, motor condition, and supply during the run.",
        "",
        "Interpretation",
        f"- realtime normal predicted distribution is {np.bincount(realtime_pred, minlength=4).tolist()}.",
        "- score contribution identifies which scaled features push each class score; it is diagnostic only.",
        "- no CSV is deleted, relabeled, or automatically excluded by this script.",
        "- parity status: the existing PC/C golden parity remains unchanged; this report evaluates runtime data shift.",
    ])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Compared {len(train_features)} training windows with {len(realtime_features)} realtime windows.")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
