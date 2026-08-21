"""Analyze features of correct and misclassified looseness-60 windows."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Missing NumPy. Install numpy to run this diagnostic.") from exc


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
OOF_REPORT = REPORT_DIR / "baseline_cv_error_by_speed.txt"
ANALYSIS_REPORT = REPORT_DIR / "looseness_60_prediction_feature_analysis.txt"
WINDOW_REPORT = REPORT_DIR / "looseness_60_window_predictions.csv"
WINDOW_SIZE = 200
SAMPLE_RATE_HZ = 200.0
TARGET_RUNS = [
    "mechanical_looseness_60_20260820_170815.csv",
    "mechanical_looseness_60_20260820_171323.csv",
    "mechanical_looseness_60_20260820_172224.csv",
]
Y_FEATURES = ["y_std", "y_rms", "y_peak_to_peak", "y_mad", "y_dominant_frequency", "y_dominant_amplitude", "y_spectral_centroid", "y_spectral_energy"]


def read_oof_predictions() -> dict[tuple[str, int], dict]:
    if not OOF_REPORT.exists():
        raise FileNotFoundError(f"Missing {OOF_REPORT}; run train_baseline.py first to create OOF predictions.")
    pattern = re.compile(r"source_csv=(.*?), true_class=(.*?), speed=(\d+), true_label=(.*?), predicted_label=(.*?), prediction_confidence=([0-9.]+)")
    predictions = {}
    for line in OOF_REPORT.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            source_csv, true_class, speed, true_label, predicted_label, confidence = match.groups()
            key = (source_csv, len([key for key in predictions if key[0] == source_csv]))
            predictions[key] = {"true_class": true_class, "speed": int(speed), "true_label": true_label, "predicted_label": predicted_label, "confidence": float(confidence)}
    return predictions


def fft_features(signal: np.ndarray) -> tuple[float, float, float, float]:
    spectrum = np.abs(np.fft.rfft(signal - np.mean(signal))) / len(signal)
    if len(spectrum) > 2:
        spectrum[1:-1] *= 2.0
    frequencies = np.fft.rfftfreq(len(signal), d=1.0 / SAMPLE_RATE_HZ)
    non_dc = spectrum.copy()
    non_dc[0] = 0.0
    index = int(np.argmax(non_dc))
    energy = spectrum ** 2
    total = float(np.sum(energy))
    centroid = float(np.sum(frequencies * energy) / total) if total else 0.0
    return float(frequencies[index]), float(spectrum[index]), centroid, total


def window_features(signal: np.ndarray, prefix: str) -> dict:
    median = float(np.median(signal))
    dominant_frequency, dominant_amplitude, centroid, energy = fft_features(signal)
    return {
        f"{prefix}_std": float(np.std(signal)),
        f"{prefix}_rms": float(np.sqrt(np.mean(signal ** 2))),
        f"{prefix}_peak_to_peak": float(np.ptp(signal)),
        f"{prefix}_mad": float(np.median(np.abs(signal - median))),
        f"{prefix}_dominant_frequency": dominant_frequency,
        f"{prefix}_dominant_amplitude": dominant_amplitude,
        f"{prefix}_spectral_centroid": centroid,
        f"{prefix}_spectral_energy": energy,
    }


def load_run(path: Path) -> list[dict]:
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"header mismatch: {reader.fieldnames!r}")
        for row in reader:
            rows.append([float(row[axis]) for axis in ("x", "y", "z")])
    count = len(rows) // WINDOW_SIZE
    output = []
    for index in range(count):
        window = np.asarray(rows[index * WINDOW_SIZE : (index + 1) * WINDOW_SIZE], dtype=np.float64)
        features = {}
        for axis_index, axis in enumerate(("x", "y", "z")):
            features.update(window_features(window[:, axis_index], axis))
        output.append(features)
    return output


def fmt(value) -> str:
    return "UNKNOWN" if value is None else f"{value:.4f}"


def group_summary(records: list[dict], feature_names: list[str]) -> str:
    if not records:
        return "count=0"
    values = {name: np.asarray([record[name] for record in records]) for name in feature_names}
    return "; ".join(f"{name}: mean={fmt(float(np.mean(series)))}, std={fmt(float(np.std(series)))}" for name, series in values.items())


def correlation(records: list[dict], feature: str) -> float | None:
    if len(records) < 3 or len({record["error"] for record in records}) < 2:
        return None
    x = np.asarray([record[feature] for record in records], dtype=float)
    y = np.asarray([record["error"] for record in records], dtype=float)
    if np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main() -> None:
    predictions = read_oof_predictions()
    records = []
    for run_name in TARGET_RUNS:
        features = load_run(RAW_DIR / run_name)
        for index, feature_row in enumerate(features):
            prediction = predictions.get((run_name, index))
            if prediction is None:
                raise ValueError(f"No OOF prediction found for {run_name} window {index}")
            records.append({"run": run_name, "window_index": index, "prediction": prediction["predicted_label"], "confidence": prediction["confidence"], "true_label": prediction["true_label"], "error": int(prediction["predicted_label"] != prediction["true_label"]), **feature_row})

    csv_fields = ["run", "window_index", "true_label", "prediction", "confidence", *[f"{axis}_{name}" for axis in ("x", "y", "z") for name in ("std", "rms", "peak_to_peak", "mad", "dominant_frequency", "dominant_amplitude", "spectral_centroid", "spectral_energy")]]
    WINDOW_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with WINDOW_REPORT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows({field: record.get(field, "") for field in csv_fields} for record in records)

    lines = ["MotorTinyML Looseness-60 Prediction Feature Analysis", "=" * 55, "Predictions are reused from aggregate out-of-fold CV output; no retraining was performed.", "No CSV, label, or exclusion list was modified.", ""]
    for run_name in TARGET_RUNS:
        run_records = [record for record in records if record["run"] == run_name]
        correct = [record for record in run_records if not record["error"]]
        wrong = [record for record in run_records if record["error"]]
        lines.extend(["", run_name, "-" * len(run_name), f"windows={len(run_records)}, correct={len(correct)}, incorrect={len(wrong)}"])
        for label, subset in (("correct_looseness", correct), ("predicted_normal", [r for r in wrong if r["prediction"] == "normal"]), ("predicted_overload", [r for r in wrong if r["prediction"] == "overload"])):
            lines.append(f"{label}: count={len(subset)}")
            lines.append("  " + group_summary(subset, Y_FEATURES))
        lines.append("prediction-feature error correlations (UNKNOWN means insufficient evidence):")
        for feature in Y_FEATURES:
            lines.append(f"  {feature}: {fmt(correlation(run_records, feature))}")
        lines.append("window-level records are saved in looseness_60_window_predictions.csv")

    lines.extend(["", "Focused interpretation", "-" * 24, "170815: compare overload-predicted windows against correct looseness windows; frequency-only causation is UNKNOWN unless feature correlations support it.", "172224: compare normal-predicted windows against correct looseness windows; lower energy/amplitude or a distinct waveform signature should be treated as evidence, not a relabeling decision.", "171323: its correct windows should be compared across all listed features; dominant frequency alone is not sufficient to explain recognition.", "No evidence from this diagnostic proves any CSV label is wrong.", "The observed pattern is more consistent with a dataset-coverage or CNN-generalization question than an automatic label correction.", "Recommended next step: B/C/D (increase looseness intra-class coverage, consider training/model adjustments after review, or mark uncertain relationships UNKNOWN); do not automatically delete data."])
    ANALYSIS_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Analyzed {len(records)} windows across {len(TARGET_RUNS)} runs.")
    print(f"Window table: {WINDOW_REPORT}")
    print(f"Report: {ANALYSIS_REPORT}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
