"""Convert the final Keras model to TFLite and validate PC-side parity."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from dataset_audit import audit_csv


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
KERAS_PATH = MODEL_DIR / "final_model.keras"
NORMALIZATION_PATH = MODEL_DIR / "final_normalization.npz"
FLOAT_TFLITE_PATH = MODEL_DIR / "final_model_float32.tflite"
INT8_TFLITE_PATH = MODEL_DIR / "final_model_int8.tflite"
REPORT_PATH = REPORT_DIR / "tflite_conversion.txt"
PARITY_CSV_PATH = REPORT_DIR / "tflite_parity_windows.csv"
WINDOW_SIZE = 200
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}


def load_included_windows() -> tuple[np.ndarray, np.ndarray, list[dict]]:
    windows, labels, metadata = [], [], []
    for path in sorted(RAW_DIR.rglob("*.csv")):
        audit = audit_csv(path)
        if audit["status"] != "INCLUDED" or audit["class"] not in CLASS_TO_INDEX:
            continue
        rows = []
        with path.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
                raise ValueError(f"header mismatch: {path.name}")
            for row in reader:
                rows.append([float(row["x"]), float(row["y"]), float(row["z"])])
        count = len(rows) // WINDOW_SIZE
        if not count:
            continue
        values = np.asarray(rows[: count * WINDOW_SIZE], dtype=np.float32).reshape(count, WINDOW_SIZE, 3)
        windows.append(values)
        labels.extend([CLASS_TO_INDEX[audit["class"]]] * count)
        metadata.extend({"source_csv": path.name, "window_index": index, "true_class": audit["class"]} for index in range(count))
    if not windows:
        raise ValueError("No INCLUDED windows found")
    return np.concatenate(windows), np.asarray(labels, dtype=np.int64), metadata


def quantization(detail: dict) -> tuple[float, int]:
    params = detail.get("quantization_parameters", {})
    scales = params.get("scales", [])
    zero_points = params.get("zero_points", [])
    if len(scales) != 1 or len(zero_points) != 1 or float(scales[0]) == 0:
        scale, zero_point = detail.get("quantization", (0.0, 0))
    else:
        scale, zero_point = float(scales[0]), int(zero_points[0])
    if not scale:
        raise ValueError(f"Missing quantization parameters for tensor {detail.get('name')}")
    return float(scale), int(zero_point)


def invoke(interpreter, sample: np.ndarray) -> tuple[np.ndarray, dict, dict]:
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    tensor = sample.astype(np.float32)[None, ...]
    if input_detail["dtype"] == np.int8:
        scale, zero_point = quantization(input_detail)
        tensor = np.clip(np.round(tensor / scale + zero_point), -128, 127).astype(np.int8)
    elif input_detail["dtype"] != np.float32:
        raise ValueError(f"Unsupported input dtype: {input_detail['dtype']}")
    interpreter.set_tensor(input_detail["index"], tensor)
    interpreter.invoke()
    output = interpreter.get_tensor(output_detail["index"])
    if output_detail["dtype"] == np.int8:
        scale, zero_point = quantization(output_detail)
        output = (output.astype(np.float32) - zero_point) * scale
    return output[0], input_detail, output_detail


def model_contract(interpreter) -> str:
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    lines = [
        f"input_shape: {input_detail['shape'].tolist()}",
        f"input_dtype: {input_detail['dtype']}",
        f"output_shape: {output_detail['shape'].tolist()}",
        f"output_dtype: {output_detail['dtype']}",
    ]
    if input_detail["dtype"] == np.int8:
        scale, zero_point = quantization(input_detail)
        lines.extend([f"input_scale: {scale}", f"input_zero_point: {zero_point}"])
    if output_detail["dtype"] == np.int8:
        scale, zero_point = quantization(output_detail)
        lines.extend([f"output_scale: {scale}", f"output_zero_point: {zero_point}"])
    return "\n".join(lines)


def main() -> None:
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit("Missing TensorFlow. Install tensorflow to convert and validate TFLite models.") from exc
    if not KERAS_PATH.exists() or not NORMALIZATION_PATH.exists():
        raise FileNotFoundError("final_model.keras or final_normalization.npz is missing")

    model = tf.keras.models.load_model(KERAS_PATH)
    normalization = np.load(NORMALIZATION_PATH)
    mean = normalization["mean"].astype(np.float32)
    std = normalization["std"].astype(np.float32)
    windows, labels, metadata = load_included_windows()
    normalized = ((windows - mean) / std).astype(np.float32)

    float_converter = tf.lite.TFLiteConverter.from_keras_model(model)
    FLOAT_TFLITE_PATH.write_bytes(float_converter.convert())

    def representative_dataset():
        for sample in normalized:
            yield [sample[None, ...].astype(np.float32)]

    int8_converter = tf.lite.TFLiteConverter.from_keras_model(model)
    int8_converter.optimizations = [tf.lite.Optimize.DEFAULT]
    int8_converter.representative_dataset = representative_dataset
    int8_converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    int8_converter.inference_input_type = tf.int8
    int8_converter.inference_output_type = tf.int8
    try:
        INT8_TFLITE_PATH.write_bytes(int8_converter.convert())
    except Exception as exc:
        raise RuntimeError(f"Full INT8 conversion failed; no silent fallback was used: {exc}") from exc

    float_interpreter = tf.lite.Interpreter(model_path=str(FLOAT_TFLITE_PATH))
    int8_interpreter = tf.lite.Interpreter(model_path=str(INT8_TFLITE_PATH))
    float_interpreter.allocate_tensors()
    int8_interpreter.allocate_tensors()
    keras_probabilities = model.predict(normalized, verbose=0)
    float_probabilities, int8_probabilities = [], []
    parity_rows = []
    for index, sample in enumerate(normalized):
        float_output, _, _ = invoke(float_interpreter, sample)
        int8_output, _, _ = invoke(int8_interpreter, sample)
        float_probabilities.append(float_output)
        int8_probabilities.append(int8_output)
        parity_rows.append({
            **metadata[index],
            "keras_pred": CLASS_NAMES[int(np.argmax(keras_probabilities[index]))],
            "float_tflite_pred": CLASS_NAMES[int(np.argmax(float_output))],
            "int8_pred": CLASS_NAMES[int(np.argmax(int8_output))],
            "keras_confidence": float(np.max(keras_probabilities[index])),
            "float_confidence": float(np.max(float_output)),
            "int8_confidence": float(np.max(int8_output)),
        })
    float_probabilities = np.asarray(float_probabilities)
    int8_probabilities = np.asarray(int8_probabilities)
    keras_pred = np.argmax(keras_probabilities, axis=1)
    float_pred = np.argmax(float_probabilities, axis=1)
    int8_pred = np.argmax(int8_probabilities, axis=1)
    report_lines = [
        "MotorTinyML TFLite Conversion and Parity Report", "=" * 48,
        f"tensorflow_version: {tf.__version__}", f"keras_path: {KERAS_PATH}", f"float_tflite_path: {FLOAT_TFLITE_PATH}", f"int8_tflite_path: {INT8_TFLITE_PATH}",
        f"keras_size_bytes: {KERAS_PATH.stat().st_size}", f"float_tflite_size_bytes: {FLOAT_TFLITE_PATH.stat().st_size}", f"int8_tflite_size_bytes: {INT8_TFLITE_PATH.stat().st_size}",
        f"normalization_mean: {mean.tolist()}", f"normalization_std: {std.tolist()}", f"representative_window_count: {len(normalized)}", "class_mapping: 0 normal, 1 rotor_unbalance, 2 mechanical_looseness, 3 overload", "",
        "Float32 tensor contract:", model_contract(float_interpreter), "", "INT8 tensor contract:", model_contract(int8_interpreter), "",
        f"keras_vs_float_predicted_class_agreement: {np.mean(keras_pred == float_pred):.6f}", f"keras_vs_float_max_abs_probability_difference: {np.max(np.abs(keras_probabilities - float_probabilities)):.6f}", f"keras_vs_float_mean_abs_probability_difference: {np.mean(np.abs(keras_probabilities - float_probabilities)):.6f}",
        f"keras_vs_int8_predicted_class_agreement: {np.mean(keras_pred == int8_pred):.6f}", f"keras_vs_int8_changed_predictions: {int(np.sum(keras_pred != int8_pred))}", f"keras_vs_int8_max_abs_probability_difference: {np.max(np.abs(keras_probabilities - int8_probabilities)):.6f}", f"keras_vs_int8_mean_abs_probability_difference: {np.mean(np.abs(keras_probabilities - int8_probabilities)):.6f}", f"float_vs_int8_predicted_class_agreement: {np.mean(float_pred == int8_pred):.6f}",
        "", f"keras_training_sanity_accuracy: {np.mean(keras_pred == labels):.6f}", f"float_tflite_training_sanity_accuracy: {np.mean(float_pred == labels):.6f}", f"int8_tflite_training_sanity_accuracy: {np.mean(int8_pred == labels):.6f}", "These are NOT independent evaluation metrics; they are conversion sanity checks only.", "Independent generalization reference: LORO CV = 99.26% +/- 0.60%.",
        "", "Acceptance guidance: Float32 agreement should approach 100%; INT8 agreement ideally >= 99%. Agreement below 98% or a marked sanity-accuracy drop should block STM32 integration and require review.", "Known limitation: fan-related experimental confounding remains unresolved.",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    with PARITY_CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(parity_rows[0]))
        writer.writeheader()
        writer.writerows(parity_rows)
    print(f"Float agreement: {np.mean(keras_pred == float_pred):.4f}")
    print(f"INT8 agreement: {np.mean(keras_pred == int8_pred):.4f}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
