"""Train the MotorTinyML final Keras deployment candidate on all INCLUDED windows."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Missing NumPy. Install tensorflow and numpy to run final training.") from exc

from dataset_audit import audit_csv


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
MODEL_PATH = MODEL_DIR / "final_model.keras"
NORMALIZATION_PATH = MODEL_DIR / "final_normalization.npz"
REPORT_PATH = REPORT_DIR / "final_model_training.txt"
WINDOW_SIZE = 200
CHANNELS = 3
EPOCHS = 25
BATCH_SIZE = 16
SEED = 42
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}


def load_windows(path: Path) -> np.ndarray:
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"header mismatch in {path.name}: {reader.fieldnames!r}")
        for row in reader:
            rows.append([float(row["x"]), float(row["y"]), float(row["z"])])
    complete_count = len(rows) // WINDOW_SIZE
    if complete_count == 0:
        return np.empty((0, WINDOW_SIZE, CHANNELS), dtype=np.float32)
    values = np.asarray(rows[: complete_count * WINDOW_SIZE], dtype=np.float32)
    return values.reshape(complete_count, WINDOW_SIZE, CHANNELS)


def collect_included() -> tuple[np.ndarray, np.ndarray, list[dict]]:
    windows = []
    labels = []
    metadata = []
    for path in sorted(RAW_DIR.rglob("*.csv")):
        audit = audit_csv(path)
        if audit["status"] != "INCLUDED" or audit["class"] not in CLASS_TO_INDEX:
            continue
        current = load_windows(path)
        if len(current) == 0:
            continue
        class_name = audit["class"]
        windows.append(current)
        labels.extend([CLASS_TO_INDEX[class_name]] * len(current))
        metadata.append({"file": path.name, "class": class_name, "speed": audit["speed"], "windows": len(current)})
    if not windows:
        raise ValueError("No INCLUDED training windows found")
    return np.concatenate(windows), np.asarray(labels, dtype=np.int64), metadata


def create_model():
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit("Missing TensorFlow. Install tensorflow and numpy to run final training.") from exc
    tf.random.set_seed(SEED)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(WINDOW_SIZE, CHANNELS)),
        tf.keras.layers.Conv1D(16, 5, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(32, 5, activation="relu", padding="same"),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(len(CLASS_NAMES), activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def write_report(metadata, labels, mean, std, model, history) -> None:
    class_counts = Counter(CLASS_NAMES[int(label)] for label in labels)
    speed_counts = Counter(str(item["speed"]) for item in metadata)
    lines = [
        "MotorTinyML Final Model Training Report",
        "=" * 42,
        f"timestamp: {datetime.now().isoformat(timespec='seconds')}",
        "training_scope: all dataset_audit.py INCLUDED four-class windows",
        f"included_csv_count: {len(metadata)}",
        f"window_count: {len(labels)}",
        f"class_distribution: {dict(class_counts)}",
        f"speed_distribution_csv_count: {dict(speed_counts)}",
        "class_mapping: 0=normal, 1=rotor_unbalance, 2=mechanical_looseness, 3=overload",
        "",
        "normalization_mean: " + str(mean.tolist()),
        "normalization_std: " + str(std.tolist()),
        "normalization_contract: normalized = (raw - mean) / std",
        "",
        "model_architecture: Input(200,3) -> Conv1D(16,5,relu,same) -> MaxPooling1D(2) -> Conv1D(32,5,relu,same) -> MaxPooling1D(2) -> GlobalAveragePooling1D -> Dense(16,relu) -> Dense(4,softmax)",
        f"parameter_count: {model.count_params()}",
        f"epochs: {EPOCHS}",
        f"batch_size: {BATCH_SIZE}",
        "optimizer: Adam",
        "loss: sparse_categorical_crossentropy",
        f"random_seed: {SEED}",
        f"final_training_loss: {history.history['loss'][-1]:.6f}",
        f"final_training_accuracy: {history.history['accuracy'][-1]:.6f}",
        "",
        "model_input_contract:",
        "  input_shape: (1, 200, 3)",
        "  input_order: X, Y, Z",
        "  dtype_before_future_quantization: float32",
        "  class_order: 0 normal, 1 rotor_unbalance, 2 mechanical_looseness, 3 overload",
        "",
        "Evaluation interpretation:",
        "Training accuracy is NOT an independent test metric.",
        "Independent experimental evaluation reference: LORO CV mean accuracy = 0.9926, std = 0.0060, mechanical_looseness recall = 0.97.",
        "",
        "Known limitations:",
        "Only three independent runs per class+speed were collected.",
        "LORO results represent CSV-level run generalization on the current experimental dataset, not unknown real-device generalization.",
        "fan-related experimental confounding remains unresolved.",
        "No TFLite conversion, quantization, STM32 integration, or C-array generation is performed by this script.",
        "",
        "Included source files:",
    ]
    lines.extend(f"  - {item['file']} ({item['class']}, speed={item['speed']}, windows={item['windows']})" for item in metadata)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    np.random.seed(SEED)
    windows, labels, metadata = collect_included()
    mean = windows.reshape(-1, CHANNELS).mean(axis=0)
    std = windows.reshape(-1, CHANNELS).std(axis=0)
    std[std == 0] = 1.0
    normalized = (windows - mean) / std
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(NORMALIZATION_PATH, mean=mean, std=std, class_names=np.asarray(CLASS_NAMES))
    model = create_model()
    model.summary()
    history = model.fit(normalized, labels, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)
    model.save(MODEL_PATH)
    write_report(metadata, labels, mean, std, model, history)
    print(f"Final model training complete. Training accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"Model: {MODEL_PATH}")
    print(f"Normalization: {NORMALIZATION_PATH}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Final training cannot start: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
