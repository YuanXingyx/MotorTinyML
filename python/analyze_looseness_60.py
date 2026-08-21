"""Focused statistical and FFT analysis for the three official looseness-60 runs."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path
from statistics import mean, pstdev

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Missing NumPy. Install numpy to run this analysis.") from exc


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
REPORT_PATH = REPORT_DIR / "mechanical_looseness_60_analysis.txt"
WINDOW_SIZE = 200
SAMPLE_RATE_HZ = 200.0
RUN_NAMES = [
    "mechanical_looseness_60_20260820_170815.csv",
    "mechanical_looseness_60_20260820_171323.csv",
    "mechanical_looseness_60_20260820_172224.csv",
]
AXES = ("x", "y", "z")


def read_csv(path: Path) -> np.ndarray:
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"header mismatch: {reader.fieldnames!r}")
        for row in reader:
            rows.append([float(row[axis]) for axis in AXES])
    values = np.asarray(rows, dtype=np.float64)
    if len(values) < WINDOW_SIZE:
        raise ValueError("fewer than one complete 200-sample window")
    return values[: len(values) // WINDOW_SIZE * WINDOW_SIZE].reshape(-1, WINDOW_SIZE, 3)


def scalar_stats(values: np.ndarray) -> dict[str, float]:
    flat = values.reshape(-1)
    median = float(np.median(flat))
    return {
        "mean": float(np.mean(flat)),
        "std": float(np.std(flat)),
        "rms": float(np.sqrt(np.mean(flat ** 2))),
        "min": float(np.min(flat)),
        "max": float(np.max(flat)),
        "peak_to_peak": float(np.ptp(flat)),
        "mad": float(np.median(np.abs(flat - median))),
    }


def fft_stats(window: np.ndarray) -> dict[str, float]:
    n = len(window)
    frequencies = np.fft.rfftfreq(n, d=1.0 / SAMPLE_RATE_HZ)
    spectrum = np.abs(np.fft.rfft(window - np.mean(window))) / n
    if n > 1:
        spectrum[1:-1] *= 2.0
    non_dc = spectrum.copy()
    if len(non_dc) > 1:
        non_dc[0] = 0.0
    dominant_index = int(np.argmax(non_dc))
    weights = spectrum ** 2
    total_energy = float(np.sum(weights))
    centroid = float(np.sum(frequencies * weights) / total_energy) if total_energy else 0.0
    return {
        "dominant_frequency": float(frequencies[dominant_index]),
        "dominant_amplitude": float(spectrum[dominant_index]),
        "spectral_centroid": centroid,
        "spectral_energy": total_energy,
    }


def summarize_window_metric(values: list[float]) -> dict[str, float]:
    average = mean(values)
    deviation = pstdev(values) if len(values) > 1 else 0.0
    return {
        "mean": average,
        "std": deviation,
        "min": min(values),
        "max": max(values),
        "cv": deviation / abs(average) if abs(average) > 1e-12 else math.nan,
    }


def analyze_run(path: Path) -> dict:
    windows = read_csv(path)
    base = {axis: scalar_stats(windows[:, :, index]) for index, axis in enumerate(AXES)}
    window_stats = {axis: {"std": [], "rms": [], "peak_to_peak": []} for axis in AXES}
    frequency_stats = {axis: {"dominant_frequency": [], "dominant_amplitude": [], "spectral_centroid": [], "spectral_energy": []} for axis in AXES}
    for window in windows:
        for index, axis in enumerate(AXES):
            signal = window[:, index]
            window_stats[axis]["std"].append(float(np.std(signal)))
            window_stats[axis]["rms"].append(float(np.sqrt(np.mean(signal ** 2))))
            window_stats[axis]["peak_to_peak"].append(float(np.ptp(signal)))
            for name, value in fft_stats(signal).items():
                frequency_stats[axis][name].append(value)
    window_summary = {axis: {metric: summarize_window_metric(values) for metric, values in metrics.items()} for axis, metrics in window_stats.items()}
    frequency_summary = {axis: {metric: summarize_window_metric(values) for metric, values in metrics.items()} for axis, metrics in frequency_stats.items()}
    return {"path": path, "windows": windows, "base": base, "window_summary": window_summary, "frequency_summary": frequency_summary}


def fmt(value: float) -> str:
    return "N/A" if math.isnan(value) else f"{value:.3f}"


def run_vector(result: dict) -> list[float]:
    y = result["base"]["y"]
    y_frequency = result["frequency_summary"]["y"]
    return [y["std"], y["rms"], y["peak_to_peak"], y_frequency["dominant_frequency"]["mean"], y_frequency["spectral_energy"]["mean"]]


def main() -> None:
    results = []
    for name in RUN_NAMES:
        path = RAW_DIR / name
        if not path.exists():
            raise FileNotFoundError(path)
        results.append(analyze_run(path))

    lines = [
        "MotorTinyML mechanical_looseness_60 Analysis",
        "=" * 48,
        "Purpose: compare experimental states; do not delete or select data from model accuracy.",
        f"window_size: {WINDOW_SIZE}",
        f"sample_rate_hz: {SAMPLE_RATE_HZ}",
        "",
    ]
    for result in results:
        lines.extend(["", result["path"].name, "-" * len(result["path"].name), "base statistics"])
        for axis in AXES:
            lines.append(f"{axis}: " + ", ".join(f"{name}={fmt(value)}" for name, value in result["base"][axis].items()))
        lines.append("window statistics (15 complete windows)")
        for axis in AXES:
            for metric, summary in result["window_summary"][axis].items():
                lines.append(f"{axis}_{metric}: " + ", ".join(f"{name}={fmt(value)}" for name, value in summary.items()))
        lines.append("frequency statistics; Y axis is the primary focus")
        for axis in AXES:
            for metric, summary in result["frequency_summary"][axis].items():
                lines.append(f"{axis}_{metric}: " + ", ".join(f"{name}={fmt(value)}" for name, value in summary.items()))

    vectors = np.asarray([run_vector(result) for result in results], dtype=np.float64)
    scales = np.std(vectors, axis=0)
    scales[scales == 0] = 1.0
    normalized = (vectors - np.mean(vectors, axis=0)) / scales
    distances = np.sqrt(np.sum((normalized[:, None, :] - normalized[None, :, :]) ** 2, axis=2))
    lines.extend(["", "Run comparison", "-" * 24, "comparison vector: Y std, Y RMS, Y peak-to-peak, Y dominant frequency, Y spectral energy"])
    for left in range(len(results)):
        for right in range(left + 1, len(results)):
            lines.append(f"{results[left]['path'].stem} vs {results[right]['path'].stem}: normalized_distance={distances[left, right]:.3f}")
    centroid = np.mean(normalized, axis=0)
    centroid_distances = np.sqrt(np.sum((normalized - centroid) ** 2, axis=1))
    lines.append("centroid distances: " + ", ".join(f"{result['path'].stem}={distance:.3f}" for result, distance in zip(results, centroid_distances)))
    median_distance = float(np.median(centroid_distances))
    label = "CONSISTENT_PATTERN" if max(distances[np.triu_indices(3, 1)]) < 2.0 else "REVIEW"
    if median_distance > 0 and max(centroid_distances) > median_distance * 2.0:
        label = "DIFFERENT_OPERATING_STATE"
    lines.extend(["", f"diagnostic_pattern: {label}", "This label is diagnostic only; it does not authorize exclusion or relabeling."])
    lines.extend(["", "Interpretation prompts", "-" * 24, "170815 overload-like assessment: REVIEW; compare with overload reference statistics before making any conclusion.", "172224 normal-like assessment: REVIEW; similarity to normal cannot be established from this script alone.", "171323 intermediate-state assessment: REVIEW; inspect its Y-axis window and spectral distributions.", "The three runs may reflect different looseness strengths or fixture states; this tool reports evidence rather than making a deletion decision."])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Analyzed {len(results)} runs.")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
