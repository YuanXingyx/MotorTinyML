"""Evaluate the nine final-demo runs with strict CSV-level LORO."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install numpy and scikit-learn before running this evaluator.") from exc


ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = ROOT / "dataset" / "raw" / "final_demo"
REPORT_PATH = ROOT / "dataset" / "reports" / "stage_d4b_final_demo_loro.txt"
WINDOW_SIZE = 200
CLASS_NAMES = ("normal", "rotor_unbalance", "overload")
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}
FEATURE_NAMES = [
    f"{axis}_{stat}"
    for axis in ("x", "y", "z")
    for stat in ("mean", "std", "rms", "min", "max", "peak_to_peak", "mad")
]


def paths() -> list[tuple[str, str, Path]]:
    result = []
    for class_name in ("normal", "rotor_unbalance"):
        for run in range(1, 4):
            result.append((class_name, f"{class_name}_{run:02d}",
                           FINAL_DIR / f"motor_final_{class_name}_{run:02d}.csv"))
    for run in range(1, 4):
        result.append(("overload", f"overload_{run:02d}",
                       FINAL_DIR / f"motor_overload_realtime_{run:02d}.csv"))
    return result


def read_samples(path: Path) -> list[tuple[int, int, int, int]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"{path.name}: invalid header {reader.fieldnames!r}")
        rows = []
        for row in reader:
            rows.append(tuple(int(row[key]) for key in ("timestamp_ms", "x", "y", "z")))
    return rows


def features(windows: np.ndarray) -> np.ndarray:
    values = np.asarray(windows, dtype=np.float64)
    if values.size == 0:
        return np.empty((0, 21), dtype=np.float64)
    mean = values.mean(axis=1)
    centered = values - mean[:, None, :]
    std = values.std(axis=1, ddof=0)
    rms = np.sqrt(np.mean(values * values, axis=1))
    minimum = values.min(axis=1)
    maximum = values.max(axis=1)
    p2p = maximum - minimum
    mad = np.mean(np.abs(centered), axis=1)
    result = np.stack((mean, std, rms, minimum, maximum, p2p, mad), axis=2).reshape(-1, 21)
    if not np.all(np.isfinite(result)):
        raise ValueError("non-finite feature detected")
    return result


def quality(rows: list[tuple[int, int, int, int]]) -> list[str]:
    if not rows:
        return ["sample_count: 0", "status: INVALID"]
    timestamps = [row[0] for row in rows]
    intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]
    positive = [value for value in intervals if value > 0]
    axes = [[row[index] for row in rows] for index in (1, 2, 3)]
    vibration = []
    for start in range(0, len(rows) - WINDOW_SIZE + 1, WINDOW_SIZE):
        window = np.asarray([[row[1], row[2], row[3]] for row in rows[start:start + WINDOW_SIZE]], dtype=np.float64)
        vibration.append(float(np.sqrt(np.mean(np.std(window, axis=0, ddof=0) ** 2))))
    lines = [
        f"sample_count: {len(rows)}",
        f"complete_windows: {len(rows) // WINDOW_SIZE}",
        f"discarded_samples: {len(rows) % WINDOW_SIZE}",
        f"duration_s: {(timestamps[-1] - timestamps[0]) / 1000.0:.3f}",
        f"avg_interval_ms: {statistics.mean(positive):.3f}" if positive else "avg_interval_ms: N/A",
        f"timestamp_breaks_nonpositive: {sum(value <= 0 for value in intervals)}",
        f"timestamp_breaks_over_100ms: {sum(value > 100 for value in intervals)}",
        f"duplicate_rows: {sum(a == b for a, b in zip(rows, rows[1:]))}",
    ]
    for axis, values in zip(("x", "y", "z"), axes):
        lines.extend([
            f"{axis}_mean: {statistics.mean(values):.3f}",
            f"{axis}_std: {statistics.pstdev(values):.3f}",
            f"{axis}_rms: {math.sqrt(statistics.mean(value * value for value in values)):.3f}",
            f"{axis}_min: {min(values)}",
            f"{axis}_max: {max(values)}",
        ])
    if vibration:
        lines.extend([
            f"vibration_metric_min: {min(vibration):.3f}",
            f"vibration_metric_mean: {statistics.mean(vibration):.3f}",
            f"vibration_metric_max: {max(vibration):.3f}",
        ])
    return lines


def main() -> None:
    expected = paths()
    missing = [path for _, _, path in expected if not path.exists()]
    if missing:
        print("Missing expected Stage D-4B CSV files:")
        for path in missing:
            print(f"- {path}")
        raise SystemExit(1)

    records = []
    report = [
        "MotorTinyML Stage D-4B Final Demo Dataset LORO",
        "===============================================",
        "",
        "Evaluation is limited to the nine explicitly selected final-demo runs.",
        "No historical training data is automatically added.",
        "Feature order: " + ", ".join(FEATURE_NAMES),
        "",
        "Run quality",
        "-----------",
    ]
    for class_name, run_name, path in expected:
        rows = read_samples(path)
        records.append((class_name, run_name, path, rows, features(
            np.asarray([[row[1], row[2], row[3]] for row in rows[:len(rows) // WINDOW_SIZE * WINDOW_SIZE]], dtype=np.float64
                       ).reshape(-1, WINDOW_SIZE, 3))))
        report.extend([f"[{class_name} / {run_name}] {path}", *quality(rows), ""])

    fold_results = []
    all_true, all_pred = [], []
    for test_index, (_, test_name, _, _, test_x) in enumerate(records):
        train_x = np.concatenate([item[4] for index, item in enumerate(records) if index != test_index])
        train_y = np.concatenate([
            np.full(len(item[4]), CLASS_TO_INDEX[item[0]], dtype=np.int64)
            for index, item in enumerate(records) if index != test_index
        ])
        test_y = np.full(len(test_x), CLASS_TO_INDEX[records[test_index][0]], dtype=np.int64)
        scaler = StandardScaler().fit(train_x)
        model = LogisticRegression(max_iter=2000, solver="lbfgs", random_state=42)
        model.fit(scaler.transform(train_x), train_y)
        pred = model.predict(scaler.transform(test_x))
        accuracy = float(np.mean(pred == test_y)) if len(test_y) else 0.0
        fold_results.append((test_name, accuracy, len(test_y), pred, test_y))
        all_true.extend(test_y.tolist())
        all_pred.extend(pred.tolist())

    y_true = np.asarray(all_true, dtype=np.int64)
    y_pred = np.asarray(all_pred, dtype=np.int64)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(3)))
    report.extend(["LORO results", "------------", "split: one complete CSV held out per fold; 9 folds", ""])
    for run_name, accuracy, support, pred, _ in fold_results:
        distribution = ", ".join(f"{CLASS_NAMES[i]}={int(np.sum(pred == i))}" for i in range(3))
        report.append(f"{run_name}: support={support}, accuracy={accuracy:.6f}, predicted=[{distribution}]")
    report.extend([
        "", f"overall_accuracy: {float(np.mean(y_true == y_pred)):.6f}",
        f"fold_accuracy_mean: {float(np.mean([item[1] for item in fold_results])):.6f}",
        f"fold_accuracy_std: {float(np.std([item[1] for item in fold_results])):.6f}",
        "aggregate_confusion_matrix:", str(cm), "",
        classification_report(y_true, y_pred, labels=list(range(3)), target_names=CLASS_NAMES, digits=6, zero_division=0),
        "Interpretation", "--------------",
        "The report is diagnostic only; no CSV is deleted, relabeled, or added to the historical training set.",
    ])
    accuracy = float(np.mean(y_true == y_pred))
    recalls = np.divide(np.diag(cm), cm.sum(axis=1),
                        out=np.zeros(3, dtype=float), where=cm.sum(axis=1) != 0)
    run_consistent = all(item[1] >= 0.90 for item in fold_results)
    recommend = accuracy >= 0.95 and run_consistent and bool(np.all(recalls >= 0.90))
    report.extend(["", "Recommendation rule: overall accuracy >= 0.95, every class recall >= 0.90, "
                   "and every run accuracy >= 0.90.",
                   f"RECOMMEND_FINAL_TRAIN: {'YES' if recommend else 'NO'}"])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Report written to: {REPORT_PATH}")
    print(f"Overall accuracy: {accuracy:.6f}")


if __name__ == "__main__":
    main()
