"""Generate complete STM32 golden vectors from the frozen INT8 TFLite model."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "final_model_int8.tflite"
NORMALIZATION_PATH = ROOT_DIR / "models" / "final_normalization.npz"
GOLDEN_PATH = ROOT_DIR / "dataset" / "reports" / "stm32_golden_vectors.txt"
WINDOW_SIZE = 200
CHANNELS = 3
INPUT_SCALE = 0.032843973487615585
INPUT_ZERO_POINT = -10
OUTPUT_SCALE = 0.00390625
OUTPUT_ZERO_POINT = -128
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]


def parse_existing_vectors() -> list[dict]:
    if not GOLDEN_PATH.exists():
        raise FileNotFoundError(GOLDEN_PATH)
    lines = GOLDEN_PATH.read_text(encoding="utf-8").splitlines()
    vectors = []
    current = None
    mode = None
    for line in lines:
        if line.startswith("class: "):
            current = {"class": line.split(":", 1)[1].strip(), "raw": []}
            vectors.append(current)
            mode = None
        elif current is not None and line == "raw_samples_x_y_z:":
            mode = "raw"
        elif current is not None and line == "quantized_input_x_y_z:":
            mode = "quantized"
        elif current is not None and line.startswith("expected_"):
            mode = None
        elif current is not None and mode == "raw" and re.fullmatch(r"-?\d+,-?\d+,-?\d+", line):
            current["raw"].append([int(value) for value in line.split(",")])
    if len(vectors) != 4 or any(len(vector["raw"]) != WINDOW_SIZE for vector in vectors):
        raise ValueError("Expected four golden vectors with 200 raw X/Y/Z samples each")
    return vectors


def quantize(raw: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    normalized = (raw.astype(np.float32) - mean) / std
    values = np.rint(normalized / INPUT_SCALE + INPUT_ZERO_POINT)
    return np.clip(values, -128, 127).astype(np.int8)


def run_interpreter(interpreter, quantized: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    if input_detail["dtype"] != np.int8 or output_detail["dtype"] != np.int8:
        raise ValueError("Model is not full INT8")
    input_params = input_detail["quantization"]
    output_params = output_detail["quantization"]
    if abs(input_params[0] - INPUT_SCALE) > 1e-9 or int(input_params[1]) != INPUT_ZERO_POINT:
        raise ValueError(f"Input quantization mismatch: {input_params}")
    if abs(output_params[0] - OUTPUT_SCALE) > 1e-9 or int(output_params[1]) != OUTPUT_ZERO_POINT:
        raise ValueError(f"Output quantization mismatch: {output_params}")
    interpreter.set_tensor(input_detail["index"], quantized[None, ...])
    interpreter.invoke()
    output = interpreter.get_tensor(output_detail["index"])[0].astype(np.int8)
    dequantized = (output.astype(np.float32) - OUTPUT_ZERO_POINT) * OUTPUT_SCALE
    return output, dequantized


def main() -> None:
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit("Missing TensorFlow. Install tensorflow to generate golden outputs.") from exc
    normalization = np.load(NORMALIZATION_PATH)
    mean = normalization["mean"].astype(np.float32)
    std = normalization["std"].astype(np.float32)
    vectors = parse_existing_vectors()
    interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
    interpreter.allocate_tensors()
    input_shape = interpreter.get_input_details()[0]["shape"].tolist()
    output_shape = interpreter.get_output_details()[0]["shape"].tolist()
    if input_shape != [1, WINDOW_SIZE, CHANNELS] or output_shape != [1, 4]:
        raise ValueError(f"Tensor shape mismatch: input={input_shape}, output={output_shape}")

    output_lines = [
        "MotorTinyML STM32 Golden Vectors",
        "================================",
        "Generated from final_model_int8.tflite using TensorFlow Lite Interpreter.",
        "These vectors are deployment parity tests, not independent accuracy metrics.",
        "",
    ]
    for vector in vectors:
        raw = np.asarray(vector["raw"], dtype=np.float32)
        quantized = quantize(raw, mean, std)
        output, dequantized = run_interpreter(interpreter, quantized)
        predicted = int(np.argmax(output))
        output_lines.extend([
            f"class: {vector['class']}",
            "window_index: 0",
            "raw_samples_x_y_z:",
            *[f"{int(row[0])},{int(row[1])},{int(row[2])}" for row in raw],
            "expected_quantized_input_x_y_z:",
            *[f"{int(row[0])},{int(row[1])},{int(row[2])}" for row in quantized],
            "expected_int8_output: " + ",".join(str(int(value)) for value in output),
            "expected_dequantized_output: " + ",".join(f"{float(value):.8f}" for value in dequantized),
            f"expected_predicted_class: {predicted} ({CLASS_NAMES[predicted]})",
            "",
        ])
    GOLDEN_PATH.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"Generated {len(vectors)} complete golden vectors.")
    print(f"Output: {GOLDEN_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Golden generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
