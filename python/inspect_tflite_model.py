"""Inspect a frozen TFLite model for TFLite Micro integration planning."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "final_model_int8.tflite"
REPORT_PATH = ROOT_DIR / "dataset" / "reports" / "tflite_operator_list.txt"


def builtin_names(schema_module) -> dict[int, str]:
    names = {}
    for name in dir(schema_module.BuiltinOperator):
        if name.startswith("BuiltinOperator_"):
            value = getattr(schema_module.BuiltinOperator, name)
            if isinstance(value, int):
                names[value] = name.removeprefix("BuiltinOperator_")
    return names


def main() -> None:
    try:
        import tensorflow as tf
        from tensorflow.lite.python import schema_py_generated as schema
    except ImportError as exc:
        raise SystemExit("Missing TensorFlow. Install tensorflow to inspect the TFLite model.") from exc
    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    interpreter = tf.lite.Interpreter(model_path=str(MODEL_PATH))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    ops = interpreter._get_ops_details()

    model = schema.Model.GetRootAsModel(MODEL_PATH.read_bytes(), 0)
    names = builtin_names(schema)
    operator_codes = []
    for index in range(model.OperatorCodesLength()):
        code = model.OperatorCodes(index)
        builtin_code = code.BuiltinCode()
        operator_codes.append({
            "index": index,
            "builtin_code": builtin_code,
            "name": names.get(builtin_code, "UNKNOWN"),
            "version": code.Version(),
        })

    lines = [
        "MotorTinyML TFLite Operator Inspection",
        "=" * 42,
        f"model: {MODEL_PATH}",
        f"model_size_bytes: {MODEL_PATH.stat().st_size}",
        f"tensorflow_version: {tf.__version__}",
        "",
        "Input tensor contract:",
    ]
    for detail in input_details:
        lines.extend([
            f"  name: {detail['name']}",
            f"  shape: {detail['shape'].tolist()}",
            f"  dtype: {detail['dtype']}",
            f"  quantization: {detail['quantization']}",
        ])
    lines.append("Output tensor contract:")
    for detail in output_details:
        lines.extend([
            f"  name: {detail['name']}",
            f"  shape: {detail['shape'].tolist()}",
            f"  dtype: {detail['dtype']}",
            f"  quantization: {detail['quantization']}",
        ])
    lines.extend(["", "Operator codes from FlatBuffer:"])
    for code in operator_codes:
        lines.append(f"  index={code['index']}, builtin_code={code['builtin_code']}, name={code['name']}, version={code['version']}")
    lines.extend(["", "Interpreter operator execution list:"])
    for index, op in enumerate(ops):
        lines.append(f"  node={index}, op_name={op.get('op_name')}, inputs={op.get('inputs')}, outputs={op.get('outputs')}")
    lines.extend(["", "TFLite Micro integration note:", "Use only the operators listed above; do not use AllOpsResolver.", "Operator resolver selection requires a compatible TFLite Micro runtime version and kernel API."])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Operator list inspection complete.")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Inspection failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
