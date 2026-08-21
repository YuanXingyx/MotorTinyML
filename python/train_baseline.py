"""Experimental class+speed aware, CSV-level 3-fold baseline trainer."""

from __future__ import annotations

import csv
import argparse
import random
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Missing NumPy. Install tensorflow, numpy, scikit-learn and matplotlib.") from exc

try:
    from dataset_audit import audit_csv
except ImportError as exc:
    raise SystemExit("Run from the project root: py python/train_baseline.py") from exc

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
MODEL_DIR = ROOT_DIR / "models"
REPORT_PATH = REPORT_DIR / "baseline_cv_training.txt"
WINDOW_SIZE = 200
SEED = 42
N_FOLDS = 3
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}


def load_windows(csv_path: Path) -> np.ndarray:
    samples = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            samples.append([float(row["x"]), float(row["y"]), float(row["z"])])
    count = len(samples) // WINDOW_SIZE
    if count == 0:
        return np.empty((0, WINDOW_SIZE, 3), dtype=np.float32)
    values = np.asarray(samples[: count * WINDOW_SIZE], dtype=np.float32)
    return values.reshape(count, WINDOW_SIZE, 3)


def build_groups(speeds: set[int] | None = None) -> tuple[dict[tuple[str, int], list[Path]], list[str]]:
    groups: dict[tuple[str, int], list[Path]] = defaultdict(list)
    for csv_path in sorted(RAW_DIR.rglob("*.csv")):
        result = audit_csv(csv_path)
        if result["status"] == "INCLUDED" and result["class"] in CLASS_TO_INDEX and (speeds is None or result["speed"] in speeds):
            groups[(result["class"], result["speed"])].append(csv_path)
    warnings = []
    for key, files in sorted(groups.items()):
        if len(files) != N_FOLDS:
            warnings.append(f"{key[0]}_{key[1]} has {len(files)} INCLUDED CSV files; expected 3.")
        if len(files) < N_FOLDS:
            raise ValueError(f"{key[0]}_{key[1]} needs at least 3 INCLUDED CSV files, found {len(files)}")
    return groups, warnings


def build_fold_files(groups: dict[tuple[str, int], list[Path]], fold_index: int) -> dict[str, dict[str, list[Path]]]:
    split = {class_name: {"train": [], "validation": [], "test": []} for class_name in CLASS_NAMES}
    for (class_name, _speed), source_files in sorted(groups.items()):
        files = sorted(source_files)
        rng = random.Random(SEED + sum(ord(char) for char in f"{class_name}_{_speed}"))
        rng.shuffle(files)
        test_index = fold_index % len(files)
        validation_index = (fold_index + 1) % len(files)
        for index, path in enumerate(files):
            role = "test" if index == test_index else "validation" if index == validation_index else "train"
            split[class_name][role].append(path)
    return split


def build_loro_fold_files(groups: dict[tuple[str, int], list[Path]], fold_index: int) -> dict[str, dict[str, list[Path]]]:
    split = {class_name: {"train": [], "validation": [], "test": []} for class_name in CLASS_NAMES}
    for (class_name, _speed), source_files in sorted(groups.items()):
        files = sorted(source_files)
        rng = random.Random(SEED + sum(ord(char) for char in f"{class_name}_{_speed}"))
        rng.shuffle(files)
        test_index = fold_index % len(files)
        for index, path in enumerate(files):
            split[class_name]["test" if index == test_index else "train"].append(path)
    return split


def collect_split(split_files: dict[str, list[Path]]) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    windows, labels, metadata = [], [], []
    for class_name in CLASS_NAMES:
        for csv_path in split_files[class_name]:
            class_windows = load_windows(csv_path)
            if len(class_windows):
                windows.append(class_windows)
                labels.extend([CLASS_TO_INDEX[class_name]] * len(class_windows))
                metadata.extend({"source_csv": csv_path.name, "class": class_name, "speed": audit_csv(csv_path)["speed"]} for _ in range(len(class_windows)))
    if not windows:
        return np.empty((0, WINDOW_SIZE, 3), dtype=np.float32), np.empty(0, dtype=np.int64), []
    return np.concatenate(windows), np.asarray(labels, dtype=np.int64), metadata


def normalize(train_x: np.ndarray, val_x: np.ndarray, test_x: np.ndarray):
    mean = train_x.reshape(-1, 3).mean(axis=0)
    std = train_x.reshape(-1, 3).std(axis=0)
    std[std == 0] = 1.0
    return (train_x - mean) / std, (val_x - mean) / std, (test_x - mean) / std, mean, std


def normalize_train_test(train_x: np.ndarray, test_x: np.ndarray):
    mean = train_x.mean(axis=(0, 1))
    std = train_x.std(axis=(0, 1))
    std[std == 0] = 1.0
    return (train_x - mean) / std, (test_x - mean) / std, mean, std


def create_model():
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit("Missing TensorFlow. Install tensorflow, numpy, scikit-learn and matplotlib.") from exc
    tf.random.set_seed(SEED)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(WINDOW_SIZE, 3)),
        tf.keras.layers.Conv1D(16, 5, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(32, 5, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(4, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model, tf


def describe_split(split_files, split_data) -> list[str]:
    lines = []
    for role in ("train", "validation", "test"):
        if role not in split_data:
            continue
        files = [path.name for class_name in CLASS_NAMES for path in split_files[class_name][role]]
        labels = split_data[role][1]
        class_counts = {name: int(np.sum(labels == index)) for name, index in CLASS_TO_INDEX.items()}
        speed_counts = defaultdict(int)
        for class_name in CLASS_NAMES:
            for path in split_files[class_name][role]:
                speed_counts[audit_csv(path)["speed"]] += 1
        lines.append(f"{role}: csv_count={len(files)}, window_count={len(labels)}, class_counts={class_counts}, speed_csv_counts={dict(speed_counts)}")
        lines.extend(f"  - {name}" for name in files)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Train MotorTinyML baseline with CSV-level 3-fold CV.")
    parser.add_argument("--speeds", nargs="+", type=int, choices=(40, 60, 80), help="Restrict the experiment to these speeds.")
    parser.add_argument("--cv-mode", choices=("standard", "leave-one-run-out"), default="standard")
    parser.add_argument("--epochs", type=int, default=25, help="Fixed training epochs for leave-one-run-out mode.")
    args = parser.parse_args()
    selected_speeds = set(args.speeds) if args.speeds else None
    balanced_mode = selected_speeds == {40, 60} and args.cv_mode == "standard"
    loro_mode = args.cv_mode == "leave-one-run-out"
    if args.speeds and not balanced_mode:
        print("Note: only --speeds 40 60 enables the balanced_40_60 output mode.")
    experiment_mode = "leave-one-run-out" if loro_mode else ("balanced_40_60" if balanced_mode else "full_40_60_80")
    output_prefix = "baseline_loro" if loro_mode else ("baseline_40_60" if balanced_mode else "baseline")
    report_path = REPORT_DIR / ("baseline_loro_training.txt" if loro_mode else ("baseline_cv_40_60_training.txt" if balanced_mode else "baseline_cv_training.txt"))
    if args.epochs <= 0:
        raise ValueError("--epochs must be positive")
    try:
        import matplotlib.pyplot as plt
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError as exc:
        raise SystemExit("Missing dependency. Install tensorflow, numpy, scikit-learn and matplotlib.") from exc

    np.random.seed(SEED)
    groups, warnings = build_groups(selected_speeds)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fold_results, accuracies, aggregate_true, aggregate_pred, oof_records = [], [], [], [], []

    for fold_index in range(N_FOLDS):
        fold_number = fold_index + 1
        split_files = build_loro_fold_files(groups, fold_index) if loro_mode else build_fold_files(groups, fold_index)
        active_roles = ("train", "test") if loro_mode else ("train", "validation", "test")
        split_data = {role: collect_split({name: split_files[name][role] for name in CLASS_NAMES}) for role in active_roles}
        train_x, train_y, _ = split_data["train"]
        test_x, test_y, test_metadata = split_data["test"]
        if loro_mode:
            train_x, test_x, mean, std = normalize_train_test(train_x, test_x)
        else:
            val_x, val_y, _ = split_data["validation"]
            train_x, val_x, test_x, mean, std = normalize(train_x, val_x, test_x)
        model, tf = create_model()
        if loro_mode:
            history = model.fit(train_x, train_y, epochs=args.epochs, batch_size=16, verbose=1)
        else:
            callback = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True)
            history = model.fit(train_x, train_y, validation_data=(val_x, val_y), epochs=50, batch_size=16, callbacks=[callback], verbose=1)
        _, test_accuracy = model.evaluate(test_x, test_y, verbose=0)
        probabilities = model.predict(test_x, verbose=0)
        predictions = np.argmax(probabilities, axis=1)
        for metadata, true_label, predicted_label, probability in zip(test_metadata, test_y, predictions, probabilities):
            oof_records.append({
                **metadata,
                "true_label": CLASS_NAMES[int(true_label)],
                "predicted_label": CLASS_NAMES[int(predicted_label)],
                "prediction_confidence": float(np.max(probability)),
            })
        model.save(MODEL_DIR / f"{output_prefix}_fold{fold_number}.keras")
        np.savez(MODEL_DIR / f"{output_prefix}_fold{fold_number}_normalization.npz", mean=mean, std=std, class_names=np.asarray(CLASS_NAMES))
        best_index = int(np.argmin(history.history["val_loss"])) if not loro_mode else args.epochs - 1
        accuracies.append(float(test_accuracy))
        aggregate_true.extend(test_y.tolist())
        aggregate_pred.extend(predictions.tolist())
        fold_results.append({"fold": fold_number, "split_lines": describe_split(split_files, split_data), "mean": mean, "std": std, "best_epoch": best_index + 1, "train_accuracy": history.history["accuracy"][best_index], "validation_accuracy": None if loro_mode else history.history["val_accuracy"][best_index], "test_accuracy": float(test_accuracy), "test_true": test_y, "test_pred": predictions, "parameter_count": model.count_params()})

    aggregate_true = np.asarray(aggregate_true)
    aggregate_pred = np.asarray(aggregate_pred)
    aggregate_matrix = confusion_matrix(aggregate_true, aggregate_pred, labels=list(range(4)))
    aggregate_report = classification_report(aggregate_true, aggregate_pred, labels=list(range(4)), target_names=CLASS_NAMES, zero_division=0)
    aggregate_metrics = {}
    for index, class_name in enumerate(CLASS_NAMES):
        class_report = classification_report(aggregate_true, aggregate_pred, labels=[index], target_names=[class_name], output_dict=True, zero_division=0)[class_name]
        aggregate_metrics[class_name] = class_report
    mean_accuracy, std_accuracy = float(np.mean(accuracies)), float(np.std(accuracies))
    lines = ["MotorTinyML Baseline 3-Fold Cross-Validation Report", "=" * 52, f"experiment_mode: {experiment_mode}", f"included_speeds: {sorted(selected_speeds) if selected_speeds else [40, 60, 80]}", "excluded_by_experiment_speed: 80" if balanced_mode else "excluded_by_experiment_speed: none", f"timestamp: {datetime.now().isoformat(timespec='seconds')}", f"random_seed: {SEED}", "class_mapping: " + ", ".join(f"{i}={name}" for i, name in enumerate(CLASS_NAMES)), "split_unit: original CSV file; windows from one CSV never cross splits", ""]
    if loro_mode:
        lines.extend(["fixed_epochs: " + str(args.epochs), "validation: disabled", "Fixed epochs are used because a file-level validation split would leave only one training run per class+speed.", "Test data is not used for early stopping.", ""])
    lines.extend(f"WARNING: {warning}" for warning in warnings)
    for result in fold_results:
        validation_lines = [] if loro_mode else [f"validation_accuracy: {result['validation_accuracy']:.4f}"]
        lines.extend(["", f"Fold {result['fold']}", "-" * 20, *result["split_lines"], f"normalization_mean: {result['mean'].tolist()}", f"normalization_std: {result['std'].tolist()}", f"model_parameter_count: {result['parameter_count']}", f"best_epoch: {result['best_epoch']}", f"train_accuracy: {result['train_accuracy']:.4f}", *validation_lines, f"test_accuracy: {result['test_accuracy']:.4f}", "confusion_matrix:", np.array2string(confusion_matrix(result["test_true"], result["test_pred"], labels=list(range(4)))), "classification_report:", classification_report(result["test_true"], result["test_pred"], labels=list(range(4)), target_names=CLASS_NAMES, zero_division=0)])
    lines.extend(["", "Aggregate Cross-Validation", "-" * 28, f"fold_test_accuracies: {[round(value, 4) for value in accuracies]}", f"cv_mean_test_accuracy: {mean_accuracy:.4f}", f"cv_std_test_accuracy: {std_accuracy:.4f}", f"aggregate_test_window_count: {len(aggregate_true)}", "aggregate_confusion_matrix:", np.array2string(aggregate_matrix), "aggregate_classification_report:", aggregate_report, "", "Known dataset limitation:", "normal / mechanical_looseness and rotor_unbalance / overload may have fan-related experimental confounding.", "Cross-validation reduces speed distribution mismatch and split bias but cannot eliminate hardware-configuration confounding."])
    if loro_mode:
        lines.extend(["", "LORO reference", "previous 1-train/1-validation/1-test aggregate accuracy: approximately 0.8889", "previous mechanical_looseness recall: approximately 0.73", "Leave-one-run-out improves training coverage while keeping each test CSV fully unseen.", "This remains an experimental baseline with only three runs per class+speed."])
    if mean_accuracy >= 0.98:
        lines.extend(["", "WARNING: Very high aggregate accuracy may indicate an easy dataset or experimental confounding.", "Do not treat this baseline as final deployment evidence."])
    if balanced_mode:
        lines.extend(["", "Comparison target", "-" * 20, "previous full-speed CV: mean accuracy = 0.8691", "previous full-speed CV: mechanical_looseness recall = 0.54", f"balanced_40_60 CV mean accuracy: {mean_accuracy:.4f}", f"balanced_40_60 mechanical_looseness precision: {aggregate_metrics['mechanical_looseness']['precision']:.4f}", f"balanced_40_60 mechanical_looseness recall: {aggregate_metrics['mechanical_looseness']['recall']:.4f}", f"balanced_40_60 mechanical_looseness F1: {aggregate_metrics['mechanical_looseness']['f1-score']:.4f}", f"balanced_40_60 normal recall: {aggregate_metrics['normal']['recall']:.4f}", f"balanced_40_60 overload recall: {aggregate_metrics['overload']['recall']:.4f}"])
    if balanced_mode:
        lines.extend(["", "Balanced speed limitation:", "balanced_40_60 reduces speed distribution mismatch but cannot eliminate mechanical accessory configuration differences or fan-related experimental confounding."])
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    error_lines = [
        "MotorTinyML Out-of-Fold Error Localization Report",
        "=" * 48,
        "This diagnostic is for error localization only.",
        "No CSV is automatically excluded based on model performance.",
        "Each formal CSV is expected to appear once in aggregate test; source metadata is retained per test window.",
        "",
        "Class + speed metrics",
        "-" * 24,
    ]
    by_speed = defaultdict(list)
    by_csv = defaultdict(list)
    for record in oof_records:
        by_speed[(record["class"], record["speed"])].append(record)
        by_csv[record["source_csv"]].append(record)
    for (class_name, speed), records in sorted(by_speed.items()):
        predicted_counts = {name: sum(record["predicted_label"] == name for record in records) for name in CLASS_NAMES}
        correct = sum(record["true_label"] == record["predicted_label"] for record in records)
        error_lines.extend([
            f"{class_name}_{speed}:",
            f"  support = {len(records)}",
            f"  correct = {correct}",
            f"  accuracy = {correct / len(records):.4f}" if records else "  accuracy = N/A",
            f"  recall = {correct / len(records):.4f}" if records else "  recall = N/A",
            f"  predicted = {predicted_counts}",
        ])
    error_lines.extend(["", "Per-CSV test results", "-" * 24])
    for source_csv, records in sorted(by_csv.items()):
        predicted_counts = {name: sum(record["predicted_label"] == name for record in records) for name in CLASS_NAMES if any(record["predicted_label"] == name for record in records)}
        correct = sum(record["true_label"] == record["predicted_label"] for record in records)
        first = records[0]
        error_lines.append(f"{source_csv}: class={first['class']}, speed={first['speed']}, window_count={len(records)}, correct_windows={correct}, accuracy={correct / len(records):.4f}, predicted={predicted_counts}")
    error_lines.extend(["", "Aggregate out-of-fold prediction records", "-" * 38])
    for record in oof_records:
        error_lines.append(f"source_csv={record['source_csv']}, true_class={record['class']}, speed={record['speed']}, true_label={record['true_label']}, predicted_label={record['predicted_label']}, prediction_confidence={record['prediction_confidence']:.6f}")
    error_lines.extend(["", "Mechanical looseness focus", "-" * 26])
    for key in ("mechanical_looseness_40", "mechanical_looseness_60"):
        class_name, speed_text = key.rsplit("_", 1)
        related = by_speed.get((class_name, int(speed_text)), [])
        if related:
            flagged = sorted({record["source_csv"] for record in related if record["true_label"] != record["predicted_label"]})
            error_lines.append(f"{key}: misclassified source CSVs = {flagged or 'none'}")
    error_lines.append("Excluded diagnostic candidate 171626 remains outside training and is not included unless explicitly requested by another tool.")
    (REPORT_DIR / ("baseline_loro_error_by_speed.txt" if loro_mode else "baseline_cv_error_by_speed.txt")).write_text("\n".join(error_lines) + "\n", encoding="utf-8")

    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(range(1, N_FOLDS + 1), accuracies, marker="o")
    plt.axhline(mean_accuracy, linestyle="--", label=f"mean={mean_accuracy:.3f}")
    plt.xlabel("Fold"); plt.ylabel("Test Accuracy"); plt.title("Baseline Cross-Validation Accuracy")
    plt.xticks(range(1, N_FOLDS + 1)); plt.grid(True); plt.legend(); plt.tight_layout()
    plt.savefig(REPORT_DIR / ("baseline_loro_accuracy.png" if loro_mode else ("baseline_cv_40_60_accuracy.png" if balanced_mode else "baseline_cv_accuracy.png")), dpi=150, bbox_inches="tight"); plt.close()
    plt.figure(); plt.imshow(aggregate_matrix, interpolation="nearest", cmap="Blues"); plt.title("Baseline Aggregate Confusion Matrix"); plt.colorbar()
    ticks = np.arange(len(CLASS_NAMES)); plt.xticks(ticks, CLASS_NAMES, rotation=45, ha="right"); plt.yticks(ticks, CLASS_NAMES); plt.xlabel("Predicted"); plt.ylabel("True"); plt.tight_layout()
    plt.savefig(REPORT_DIR / ("baseline_loro_confusion_matrix.png" if loro_mode else ("baseline_cv_40_60_confusion_matrix.png" if balanced_mode else "baseline_cv_confusion_matrix.png")), dpi=150, bbox_inches="tight"); plt.close()
    print(f"3-fold cross-validation complete. Mean test accuracy: {mean_accuracy:.4f} +/- {std_accuracy:.4f}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Training cannot start: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
