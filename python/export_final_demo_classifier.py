"""Train and export the final-demo-only three-class pure-C classifier."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "dataset" / "raw" / "final_demo"
REPORT_DIR = ROOT / "dataset" / "reports"
MODEL_DIR = ROOT / "firmware" / "stm32f103" / "MotorTinyML_F103" / "App" / "Model"
REPORT_PATH = REPORT_DIR / "stage_d4c_final_model_export.txt"
WINDOW = 200
CLASSES = ("normal", "rotor_unbalance", "overload")
FILES = [(CLASSES[c], DATA_DIR / name) for c, name in [
    (0, "motor_final_normal_01.csv"), (0, "motor_final_normal_02.csv"), (0, "motor_final_normal_03.csv"),
    (1, "motor_final_rotor_unbalance_01.csv"), (1, "motor_final_rotor_unbalance_02.csv"), (1, "motor_final_rotor_unbalance_03.csv"),
    (2, "motor_overload_realtime_01.csv"), (2, "motor_overload_realtime_02.csv"), (2, "motor_overload_realtime_03.csv"),
]]


def read_windows(path: Path) -> np.ndarray:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["timestamp_ms", "x", "y", "z"]:
            raise ValueError(f"invalid header: {path.name}")
        rows = [[int(row[axis]) for axis in ("x", "y", "z")] for row in reader]
    if len(rows) < WINDOW or len(rows) % WINDOW:
        raise ValueError(f"{path.name}: expected complete 200-sample windows")
    return np.asarray(rows, dtype=np.int16).reshape(-1, WINDOW, 3)


def extract(windows: np.ndarray) -> np.ndarray:
    values = np.asarray(windows, dtype=np.float64)
    mean = values.mean(axis=1)
    centered = values - mean[:, None, :]
    result = np.stack((mean, values.std(axis=1, ddof=0),
                       np.sqrt(np.mean(values * values, axis=1)),
                       values.min(axis=1), values.max(axis=1),
                       values.max(axis=1) - values.min(axis=1),
                       np.mean(np.abs(centered), axis=1)), axis=2).reshape(-1, 21)
    if not np.all(np.isfinite(result)):
        raise ValueError("non-finite feature")
    return result


def c_features(windows: np.ndarray) -> np.ndarray:
    """Reproduce the float32 accumulation used by the generated C implementation."""
    output = []
    for window in windows:
        row = []
        for axis in range(3):
            values = window[:, axis]
            total = np.float32(0.0)
            squares = np.float32(0.0)
            minimum, maximum = int(values[0]), int(values[0])
            for raw in values:
                value = np.float32(raw)
                total = np.float32(total + value)
                squares = np.float32(squares + np.float32(value * value))
                minimum, maximum = min(minimum, int(raw)), max(maximum, int(raw))
            mean = np.float32(total / np.float32(WINDOW))
            variance = np.float32(0.0)
            mad = np.float32(0.0)
            for raw in values:
                delta = np.float32(np.float32(raw) - mean)
                variance = np.float32(variance + np.float32(delta * delta))
                mad = np.float32(mad + np.abs(delta))
            row.extend((mean, np.sqrt(np.float32(variance / WINDOW)),
                        np.sqrt(np.float32(squares / WINDOW)), minimum, maximum,
                        maximum - minimum, np.float32(mad / WINDOW)))
        output.append(row)
    return np.asarray(output, dtype=np.float64)


def f(value: float) -> str:
    return f"{float(np.float32(value)):.9g}f"


def write_c(mean: np.ndarray, std: np.ndarray, weights: np.ndarray, bias: np.ndarray) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    header = MODEL_DIR / "tiny_classifier_3class_final_params.h"
    source = MODEL_DIR / "tiny_classifier_3class_final_params.c"
    api_h = MODEL_DIR / "tiny_classifier_3class_final.h"
    api_c = MODEL_DIR / "tiny_classifier_3class_final.c"
    header_text = """#ifndef TINY_CLASSIFIER_3CLASS_FINAL_PARAMS_H
#define TINY_CLASSIFIER_3CLASS_FINAL_PARAMS_H
#define TINY3_FINAL_FEATURE_COUNT 21
#define TINY3_FINAL_CLASS_COUNT 3
#ifdef __cplusplus
extern \"C\" {
#endif
extern const float g_tiny3_final_feature_mean[21];
extern const float g_tiny3_final_feature_std[21];
extern const float g_tiny3_final_logreg_weights[3][21];
extern const float g_tiny3_final_logreg_bias[3];
#ifdef __cplusplus
}
#endif
#endif
"""
    source_text = '#include "tiny_classifier_3class_final_params.h"\n'
    source_text += "const float g_tiny3_final_feature_mean[21] = {" + ", ".join(f(v) for v in mean) + "};\n"
    source_text += "const float g_tiny3_final_feature_std[21] = {" + ", ".join(f(v) for v in std) + "};\n"
    source_text += "const float g_tiny3_final_logreg_weights[3][21] = {\n"
    source_text += "\n".join("{" + ", ".join(f(v) for v in row) + "}," for row in weights) + "\n};\n"
    source_text += "const float g_tiny3_final_logreg_bias[3] = {" + ", ".join(f(v) for v in bias) + "};\n"
    api_h_text = """#ifndef TINY_CLASSIFIER_3CLASS_FINAL_H
#define TINY_CLASSIFIER_3CLASS_FINAL_H
#include <stdint.h>
#define TINY3_FINAL_WINDOW_SIZE 200
#define TINY3_FINAL_CHANNELS 3
#define TINY3_FINAL_FEATURE_COUNT 21
#define TINY3_FINAL_CLASS_COUNT 3
void TinyClassifier3Final_ExtractFeatures(const int16_t raw_window[200][3], float features[21]);
int TinyClassifier3Final_Predict(const float features[21], float scores[3]);
#endif
"""
    api_c_text = """#include \"tiny_classifier_3class_final.h\"
#include \"tiny_classifier_3class_final_params.h\"
#include <math.h>
void TinyClassifier3Final_ExtractFeatures(const int16_t raw[200][3], float out[21]) {
  for (int axis=0; axis<3; ++axis) { float sum=0.0f, sq=0.0f, var=0.0f, mad=0.0f;
    int16_t lo=raw[0][axis], hi=lo;
    for (int i=0;i<200;++i) { float v=(float)raw[i][axis]; sum+=v; sq+=v*v; if(raw[i][axis]<lo)lo=raw[i][axis]; if(raw[i][axis]>hi)hi=raw[i][axis]; }
    float mean=sum/200.0f; for(int i=0;i<200;++i){float d=(float)raw[i][axis]-mean;var+=d*d;mad+=fabsf(d);}
    int b=axis*7; out[b]=mean; out[b+1]=sqrtf(var/200.0f); out[b+2]=sqrtf(sq/200.0f); out[b+3]=(float)lo; out[b+4]=(float)hi; out[b+5]=(float)hi-(float)lo; out[b+6]=mad/200.0f;
  }
}
int TinyClassifier3Final_Predict(const float features[21], float scores[3]) { int best=0; float best_score=-INFINITY;
  for(int c=0;c<3;++c){float score=g_tiny3_final_logreg_bias[c]; for(int i=0;i<21;++i){float z=(features[i]-g_tiny3_final_feature_mean[i])/g_tiny3_final_feature_std[i]; score+=g_tiny3_final_logreg_weights[c][i]*z;} scores[c]=score; if(score>best_score){best_score=score;best=c;}} return best;
}
"""
    temp = [(p, p.with_suffix(p.suffix + ".tmp"), text) for p, text in ((header, header_text), (source, source_text), (api_h, api_h_text), (api_c, api_c_text))]
    for _, temp_path, text in temp:
        temp_path.write_text(text, encoding="utf-8")
    for path, temp_path, _ in temp:
        temp_path.replace(path)


def main() -> None:
    blocks = [read_windows(path) for _, path in FILES]
    x = np.concatenate([extract(block) for block in blocks])
    y = np.concatenate([np.full(len(block), CLASSES.index(label), dtype=np.int64)
                        for (label, _), block in zip(FILES, blocks)])
    if len(x) != 135:
        raise ValueError(f"expected 135 windows, found {len(x)}")
    mean, std = x.mean(axis=0), x.std(axis=0, ddof=0)
    std = np.where(std == 0, 1.0, std)
    model = LogisticRegression(solver="lbfgs", max_iter=2000, random_state=42).fit((x - mean) / std, y)
    weights, bias = model.coef_, model.intercept_
    c_x = c_features(np.concatenate(blocks))
    c_mean, c_std = mean.astype(np.float32).astype(np.float64), std.astype(np.float32).astype(np.float64)
    c_weights, c_bias = weights.astype(np.float32).astype(np.float64), bias.astype(np.float32).astype(np.float64)
    c_scaled = (c_x - c_mean) / c_std
    c_scores = c_scaled @ c_weights.T + c_bias
    reference_scaled = (x - mean) / std
    reference_scores = model.decision_function(reference_scaled)
    c_pred, reference_pred = np.argmax(c_scores, axis=1), model.predict(reference_scaled)
    feature_diff = float(np.max(np.abs(c_x - x)))
    scaled_diff = float(np.max(np.abs(c_scaled - reference_scaled)))
    score_diff = float(np.max(np.abs(c_scores - reference_scores)))
    agreement = float(np.mean(c_pred == reference_pred))
    if agreement != 1.0 or not all(np.isfinite(v) for v in (feature_diff, scaled_diff, score_diff)):
        raise RuntimeError(f"PC/C parity failed: agreement={agreement}, score_diff={score_diff}")
    write_c(mean, std, weights, bias)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = [
        "MotorTinyML Stage D-4C Final Demo Model Export", "=" * 49,
        "source: dataset/raw/final_demo (9 explicitly listed CSV files)",
        "windows: 135", "class_mapping: 0=normal, 1=rotor_unbalance, 2=overload",
        "feature_order: x/y/z mean,std,rms,min,max,peak_to_peak,mad",
        "training: StandardScaler population mean/std + LogisticRegression(lbfgs, max_iter=2000)",
        "D-4B LORO overall_accuracy: 0.992593",
        "D-4B recalls: normal=1.000000, rotor_unbalance=1.000000, overload=0.977778",
        "D-4B confusion_matrix: [[45,0,0],[0,45,0],[1,0,44]]", "",
        f"feature_max_abs_diff: {feature_diff:.9g}", f"scaled_feature_max_abs_diff: {scaled_diff:.9g}",
        f"score_max_abs_diff: {score_diff:.9g}", f"predicted_class_agreement: {agreement:.9f}",
        "PC/C parity: PASS", "active STM32 model switch: NOT PERFORMED",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Exported final-demo model; PC/C agreement={agreement:.9f}")


if __name__ == "__main__":
    main()
