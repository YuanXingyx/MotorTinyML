"""Evaluate new overload realtime runs without changing deployment parameters."""

from __future__ import annotations

import csv
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

from dataset_audit import audit_csv
from train_tiny_classifier import extract_features, load_windows


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "dataset" / "raw"
NEW_DIR = RAW / "overload_realtime"
REPORT = ROOT / "dataset" / "reports" / "stage_d3b_overload_retrain_evaluation.txt"
WINDOW_SIZE = 200
SEED = 42
CLASS_NAMES = ["normal", "rotor_unbalance", "overload"]
CLASS_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}
NEW_FILES = [NEW_DIR / f"motor_overload_realtime_{index:02d}.csv" for index in range(1, 4)]


def quality(path: Path) -> tuple[dict[str, object], np.ndarray]:
    rows: list[tuple[int, int, int, int]] = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        expected = ["timestamp_ms", "x", "y", "z"]
        if reader.fieldnames != expected:
            raise ValueError(f"{path.name}: header must be {expected!r}")
        for row in reader:
            rows.append(tuple(int(row[field]) for field in expected))
    timestamps = [row[0] for row in rows]
    intervals = [later - earlier for earlier, later in zip(timestamps, timestamps[1:])]
    values = np.asarray([[row[1], row[2], row[3]] for row in rows], dtype=np.float64)
    windows = values[: len(values) // WINDOW_SIZE * WINDOW_SIZE].reshape(-1, WINDOW_SIZE, 3)
    window_metrics = []
    for window in windows:
        std = np.std(window, axis=0, ddof=0)
        window_metrics.append(float(np.sqrt(np.mean(std * std))))
    summary = {
        "sample_count": len(rows),
        "complete_windows": len(windows),
        "discarded_samples": len(values) % WINDOW_SIZE,
        "avg_interval_ms": statistics.mean([delta for delta in intervals if delta > 0]) if any(delta > 0 for delta in intervals) else None,
        "timestamp_breaks": sum(delta <= 0 or delta > 100 for delta in intervals),
        "duplicate_rows": sum(first == second for first, second in zip(rows, rows[1:])),
        "axis_mean": np.mean(values, axis=0) if len(values) else np.zeros(3),
        "axis_std": np.std(values, axis=0, ddof=0) if len(values) else np.zeros(3),
        "axis_rms": np.sqrt(np.mean(values * values, axis=0)) if len(values) else np.zeros(3),
        "axis_min": np.min(values, axis=0) if len(values) else np.zeros(3),
        "axis_max": np.max(values, axis=0) if len(values) else np.zeros(3),
        "window_metrics": window_metrics,
    }
    return summary, windows


def included_groups() -> dict[tuple[str, str], list[Path]]:
    groups: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for path in sorted(RAW.rglob("*.csv")):
        result = audit_csv(path)
        if result["status"] == "INCLUDED" and result["class"] in CLASS_INDEX:
            groups[(result["class"], str(result["speed"]))].append(path)
    for key, paths in groups.items():
        if len(paths) != 3:
            raise ValueError(f"{key}: expected 3 files for LORO, found {len(paths)}")
    return groups


def load_feature_file(path: Path) -> np.ndarray:
    return extract_features(load_windows(path))


def evaluate(groups: dict[tuple[str, str], list[Path]]) -> dict[str, object]:
    cache = {path: load_feature_file(path) for paths in groups.values() for path in paths}
    labels_by_path = {
        path: ("overload" if key == ("overload", "realtime") else key[0])
        for key, paths in groups.items()
        for path in paths
    }
    fold_accuracy: list[float] = []
    truth_all: list[np.ndarray] = []
    pred_all: list[np.ndarray] = []
    per_run: dict[str, list[float]] = defaultdict(list)
    for fold in range(3):
        train_files: list[Path] = []
        test_files: list[Path] = []
        for key, source in sorted(groups.items()):
            ordered = list(sorted(source))
            rng = random.Random(SEED + sum(ord(char) for char in f"{key[0]}_{key[1]}"))
            rng.shuffle(ordered)
            test_files.append(ordered[fold])
            train_files.extend(ordered[index] for index in range(3) if index != fold)
        train_x = np.concatenate([cache[path] for path in train_files])
        train_y = np.concatenate([np.full(len(cache[path]), CLASS_INDEX[labels_by_path[path]]) for path in train_files])
        test_x = np.concatenate([cache[path] for path in test_files])
        test_labels = []
        for path in test_files:
            label = labels_by_path[path]
            test_labels.extend([CLASS_INDEX[label]] * len(cache[path]))
        test_y = np.asarray(test_labels, dtype=np.int64)
        mean = train_x.mean(axis=0)
        std = np.where(train_x.std(axis=0, ddof=0) == 0, 1.0, train_x.std(axis=0, ddof=0))
        model = LogisticRegression(solver="lbfgs", max_iter=2000, random_state=SEED)
        model.fit((train_x - mean) / std, train_y)
        prediction = model.predict((test_x - mean) / std)
        fold_accuracy.append(float(np.mean(prediction == test_y)))
        truth_all.append(test_y)
        pred_all.append(prediction)
        for path in test_files:
            start = sum(len(cache[item]) for item in test_files[: test_files.index(path)])
            stop = start + len(cache[path])
            per_run[path.name].append(float(np.mean(prediction[start:stop] == test_y[start:stop])))
    truth = np.concatenate(truth_all)
    prediction = np.concatenate(pred_all)
    return {"accuracies": fold_accuracy, "matrix": confusion_matrix(truth, prediction, labels=[0, 1, 2]), "report": classification_report(truth, prediction, labels=[0, 1, 2], target_names=CLASS_NAMES, zero_division=0), "per_run": per_run}


def main() -> None:
    new_quality: dict[str, dict[str, object]] = {}
    for path in NEW_FILES:
        if not path.exists():
            raise ValueError(f"Missing new overload file: {path}")
        new_quality[path.name], _ = quality(path)

    base = included_groups()
    augmented = {key: list(paths) for key, paths in base.items()}
    augmented[("overload", "realtime")] = NEW_FILES
    base_result = evaluate(base)
    augmented_result = evaluate(augmented)
    base_recall = np.diag(base_result["matrix"]) / np.maximum(base_result["matrix"].sum(axis=1), 1)
    augmented_recall = np.diag(augmented_result["matrix"]) / np.maximum(augmented_result["matrix"].sum(axis=1), 1)
    overload_improved = augmented_recall[2] > base_recall[2]
    other_not_lower = augmented_recall[0] >= base_recall[0] and augmented_recall[1] >= base_recall[1]
    recommend = overload_improved and other_not_lower

    lines = ["MotorTinyML Stage D-3B Overload Retrain Evaluation", "=" * 54, "", "New files are explicit evaluation candidates; dataset_audit.py and current C parameters are unchanged.", ""]
    for name, item in new_quality.items():
        lines.extend([name, "-" * len(name), f"sample_count: {item['sample_count']}", f"complete_windows: {item['complete_windows']}", f"discarded_samples: {item['discarded_samples']}", f"avg_interval_ms: {item['avg_interval_ms']}", f"timestamp_breaks: {item['timestamp_breaks']}", f"duplicate_rows: {item['duplicate_rows']}", f"axis_mean: {item['axis_mean']}", f"axis_std: {item['axis_std']}", f"axis_rms: {item['axis_rms']}", f"axis_min: {item['axis_min']}", f"axis_max: {item['axis_max']}", f"window_vibration_metric: {item['window_metrics']}", ""])

    for label, result in (("A_original_three_class", base_result), ("B_original_plus_new_overload", augmented_result)):
        lines.extend([label, "-" * len(label), f"fold_accuracies: {result['accuracies']}", f"mean_accuracy: {np.mean(result['accuracies']):.6f}", f"confusion_matrix:\n{result['matrix']}", "classification_report:", result["report"], "per_run_accuracy:"])
        lines.extend(f"  {name}: {values}" for name, values in sorted(result["per_run"].items()))
        lines.append("")
    lines.extend([f"base_recall_normal: {base_recall[0]:.6f}", f"base_recall_rotor_unbalance: {base_recall[1]:.6f}", f"base_recall_overload: {base_recall[2]:.6f}", f"augmented_recall_normal: {augmented_recall[0]:.6f}", f"augmented_recall_rotor_unbalance: {augmented_recall[1]:.6f}", f"augmented_recall_overload: {augmented_recall[2]:.6f}", f"RECOMMEND_RETRAIN: {'YES' if recommend else 'NO'}", "No C parameters were exported or overwritten."])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {REPORT}")
    print(f"RECOMMEND_RETRAIN: {'YES' if recommend else 'NO'}")


if __name__ == "__main__":
    main()
