"""Export the augmented three-class candidate without touching active parameters."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from evaluate_overload_retrain import NEW_FILES, included_groups, load_feature_file


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "firmware" / "stm32f103" / "MotorTinyML_F103" / "App" / "Model"
REPORT = ROOT / "dataset" / "reports" / "stage_d3c_augmented_model_export.txt"
CLASS_NAMES = ["normal", "rotor_unbalance", "overload"]
CLASS_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}


def c_float(value: float) -> str:
    return f"{float(np.float32(value)):.9g}f"


def collect() -> tuple[np.ndarray, np.ndarray, list[Path]]:
    groups = included_groups()
    groups[("overload", "realtime")] = NEW_FILES
    features: list[np.ndarray] = []
    labels: list[int] = []
    files: list[Path] = []
    for key, paths in sorted(groups.items()):
        label = "overload" if key == ("overload", "realtime") else key[0]
        for path in sorted(paths):
            current = load_feature_file(path)
            features.append(current)
            labels.extend([CLASS_INDEX[label]] * len(current))
            files.append(path)
    return np.concatenate(features), np.asarray(labels, dtype=np.int64), files


def write_c_files(mean: np.ndarray, std: np.ndarray, weights: np.ndarray, bias: np.ndarray) -> tuple[Path, Path, Path, Path]:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    header = MODEL_DIR / "tiny_classifier_3class_aug_params.h"
    source = MODEL_DIR / "tiny_classifier_3class_aug_params.c"
    api_header = MODEL_DIR / "tiny_classifier_3class_aug.h"
    api_source = MODEL_DIR / "tiny_classifier_3class_aug.c"
    header.write_text("""#ifndef TINY_CLASSIFIER_3CLASS_AUG_PARAMS_H\n#define TINY_CLASSIFIER_3CLASS_AUG_PARAMS_H\n#define TINY3_AUG_FEATURE_COUNT 21\n#define TINY3_AUG_CLASS_COUNT 3\n#ifdef __cplusplus\nextern \"C\" {\n#endif\nextern const float g_tiny3_aug_feature_mean[21];\nextern const float g_tiny3_aug_feature_std[21];\nextern const float g_tiny3_aug_logreg_weights[3][21];\nextern const float g_tiny3_aug_logreg_bias[3];\n#ifdef __cplusplus\n}\n#endif\n#endif\n""", encoding="utf-8")
    source_lines = [
        '#include "tiny_classifier_3class_aug_params.h"',
        "const float g_tiny3_aug_feature_mean[21] = {" + ", ".join(c_float(v) for v in mean) + "};",
        "const float g_tiny3_aug_feature_std[21] = {" + ", ".join(c_float(v) for v in std) + "};",
        "const float g_tiny3_aug_logreg_weights[3][21] = {",
    ]
    source_lines.extend("{" + ", ".join(c_float(v) for v in row) + "}," for row in weights)
    source_lines.extend(["};", "const float g_tiny3_aug_logreg_bias[3] = {" + ", ".join(c_float(v) for v in bias) + "};"])
    source.write_text("\n".join(source_lines) + "\n", encoding="utf-8")
    api_header.write_text("""#ifndef TINY_CLASSIFIER_3CLASS_AUG_H\n#define TINY_CLASSIFIER_3CLASS_AUG_H\n#include <stdint.h>\n#define TINY3_AUG_WINDOW_SIZE 200\n#define TINY3_AUG_CHANNELS 3\n#define TINY3_AUG_FEATURE_COUNT 21\n#define TINY3_AUG_CLASS_COUNT 3\nvoid TinyClassifier3Aug_ExtractFeatures(const int16_t raw_window[200][3], float features[21]);\nint TinyClassifier3Aug_Predict(const float features[21], float scores[3]);\n#endif\n""", encoding="utf-8")
    api_source.write_text("""#include \"tiny_classifier_3class_aug.h\"\n#include \"tiny_classifier_3class_aug_params.h\"\n#include <math.h>\nvoid TinyClassifier3Aug_ExtractFeatures(const int16_t raw_window[200][3], float features[21]) {\n  for (int axis = 0; axis < 3; ++axis) {\n    float sum = 0.0f, sum_square = 0.0f, variance = 0.0f, mad = 0.0f;\n    int16_t minimum = raw_window[0][axis], maximum = minimum;\n    for (int sample = 0; sample < 200; ++sample) { float value = (float)raw_window[sample][axis]; sum += value; sum_square += value * value; if (raw_window[sample][axis] < minimum) minimum = raw_window[sample][axis]; if (raw_window[sample][axis] > maximum) maximum = raw_window[sample][axis]; }\n    float mean = sum / 200.0f;\n    for (int sample = 0; sample < 200; ++sample) { float delta = (float)raw_window[sample][axis] - mean; variance += delta * delta; mad += fabsf(delta); }\n    int base = axis * 7; features[base] = mean; features[base + 1] = sqrtf(variance / 200.0f); features[base + 2] = sqrtf(sum_square / 200.0f); features[base + 3] = (float)minimum; features[base + 4] = (float)maximum; features[base + 5] = (float)maximum - (float)minimum; features[base + 6] = mad / 200.0f;\n  }\n}\nint TinyClassifier3Aug_Predict(const float features[21], float scores[3]) { int best = 0; float best_score = -INFINITY; for (int class_index = 0; class_index < 3; ++class_index) { float score = g_tiny3_aug_logreg_bias[class_index]; for (int feature_index = 0; feature_index < 21; ++feature_index) { float scaled = (features[feature_index] - g_tiny3_aug_feature_mean[feature_index]) / g_tiny3_aug_feature_std[feature_index]; score += g_tiny3_aug_logreg_weights[class_index][feature_index] * scaled; } scores[class_index] = score; if (score > best_score) { best_score = score; best = class_index; } } return best; }\n""", encoding="utf-8")
    return header, source, api_header, api_source


def main() -> None:
    features, labels, files = collect()
    mean = features.mean(axis=0)
    std = np.where(features.std(axis=0, ddof=0) == 0, 1.0, features.std(axis=0, ddof=0))
    scaled = (features - mean) / std
    model = LogisticRegression(solver="lbfgs", max_iter=2000, random_state=42).fit(scaled, labels)
    weights = model.coef_.astype(np.float64)
    bias = model.intercept_.astype(np.float64)
    c_mean, c_std = mean.astype(np.float32).astype(np.float64), std.astype(np.float32).astype(np.float64)
    c_weights, c_bias = weights.astype(np.float32).astype(np.float64), bias.astype(np.float32).astype(np.float64)
    c_scaled = (features - c_mean) / c_std
    c_scores = c_scaled @ c_weights.T + c_bias
    py_scores = scaled @ weights.T + bias
    py_pred = np.argmax(py_scores, axis=1)
    c_pred = np.argmax(c_scores, axis=1)
    agreement = float(np.mean(py_pred == c_pred))
    if agreement != 1.0:
        raise SystemExit(f"PC/C parity failed: agreement={agreement}")
    paths = write_c_files(mean, std, weights, bias)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "MotorTinyML Stage D-3C Augmented Candidate Export", "=" * 52,
        "candidate_model: augmented three-class Logistic Regression",
        "active_model_overwritten: NO",
        "purpose: improve compatibility with the fixed manual-overload interview demonstration",
        "class_mapping: 0=normal, 1=rotor_unbalance, 2=overload",
        f"included_feature_rows: {len(features)}", f"source_csv_count: {len(files)}",
        "reference_loro_mean_accuracy: 0.983333",
        "reference_new_overload_per_run_accuracy: 1.000000, 1.000000, 1.000000",
        "feature_max_abs_diff: 0.0 (same raw feature matrix)",
        f"scaled_feature_max_abs_diff: {float(np.max(np.abs(c_scaled - scaled))):.9g}",
        f"score_max_abs_diff: {float(np.max(np.abs(c_scores - py_scores))):.9g}",
        f"predicted_class_agreement: {agreement:.9f}", f"generated: {', '.join(str(path) for path in paths)}",
        "STM32 active model switch: NOT PERFORMED; awaiting explicit approval.",
    ]) + "\n", encoding="utf-8")
    print(f"PC/C parity agreement: {agreement:.9f}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
