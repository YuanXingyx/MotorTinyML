"""Generate STM32 C golden-vector data from the Stage C-2 text artifact."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "dataset" / "reports" / "tiny_classifier_golden_vectors.txt"
MODEL_DIR = ROOT / "firmware" / "stm32f103" / "MotorTinyML_F103" / "App" / "Model"
HEADER = MODEL_DIR / "tiny_classifier_golden_data.h"
SOURCE = MODEL_DIR / "tiny_classifier_golden_data.c"
CLASSES = ("normal", "rotor_unbalance", "mechanical_looseness", "overload")


def parse() -> tuple[list[list[list[int]]], list[list[float]], list[list[float]], list[int]]:
    text = INPUT.read_text(encoding="utf-8")
    windows: list[list[list[int]]] = []
    features: list[list[float]] = []
    scores: list[list[float]] = []
    expected: list[int] = []
    for class_name in CLASSES:
        match = re.search(
            rf"\[{re.escape(class_name)}\].*?raw_window\[200\]\[3\]:\n(?P<raw>(?:  -?\d+,-?\d+,-?\d+\n){{200}})"
            rf"expected_features\[21\]: (?P<features>[^\n]+)\n"
            rf"expected_scaled_features\[21\]: [^\n]+\n"
            rf"expected_scores\[4\]: (?P<scores>[^\n]+)\n"
            rf"expected_class: (?P<class>\d+)", text, re.S,
        )
        if not match:
            raise ValueError(f"Could not parse golden vector for {class_name}")
        raw = [[int(value) for value in line.strip().split(",")] for line in match.group("raw").splitlines()]
        if len(raw) != 200 or any(len(row) != 3 for row in raw):
            raise ValueError(f"Invalid raw window shape for {class_name}")
        parsed_features = [float(value.rstrip("f")) for value in match.group("features").split(",")]
        parsed_scores = [float(value.rstrip("f")) for value in match.group("scores").split(",")]
        if len(parsed_features) != 21 or len(parsed_scores) != 4:
            raise ValueError(f"Invalid expected vector shape for {class_name}")
        windows.append(raw)
        features.append(parsed_features)
        scores.append(parsed_scores)
        expected.append(int(match.group("class")))
    return windows, features, scores, expected


def c_float(value: float) -> str:
    text = f"{value:.9g}"
    if all(marker not in text for marker in (".", "e", "E")):
        text += ".0"
    return text + "f"


def main() -> None:
    windows, features, scores, expected = parse()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    HEADER.write_text(
        """#ifndef TINY_CLASSIFIER_GOLDEN_DATA_H\n#define TINY_CLASSIFIER_GOLDEN_DATA_H\n\n#include <stdint.h>\n\n#define TINY_CLASSIFIER_GOLDEN_CASE_COUNT 4\n\n#ifdef __cplusplus\nextern \"C\" {\n#endif\n\nextern const int16_t g_tiny_classifier_golden_raw[4][200][3];\nextern const float g_tiny_classifier_golden_features[4][21];\nextern const float g_tiny_classifier_golden_scores[4][4];\nextern const int g_tiny_classifier_golden_expected_class[4];\n\n#ifdef __cplusplus\n}\n#endif\n\n#endif /* TINY_CLASSIFIER_GOLDEN_DATA_H */\n""", encoding="utf-8"
    )
    lines = [
        '#include "tiny_classifier_golden_data.h"',
        "",
        "/* Generated from dataset/reports/tiny_classifier_golden_vectors.txt. */",
        "const int16_t g_tiny_classifier_golden_raw[4][200][3] = {",
    ]
    for window in windows:
        lines.append("    {")
        lines.extend("        {" + ", ".join(str(value) for value in row) + "}," for row in window)
        lines.append("    },")
    lines.append("};")
    lines.append("const float g_tiny_classifier_golden_features[4][21] = {")
    lines.extend("    {" + ", ".join(c_float(value) for value in row) + "}," for row in features)
    lines.append("};")
    lines.append("const float g_tiny_classifier_golden_scores[4][4] = {")
    lines.extend("    {" + ", ".join(c_float(value) for value in row) + "}," for row in scores)
    lines.extend([
        "};",
        "const int g_tiny_classifier_golden_expected_class[4] = {" + ", ".join(map(str, expected)) + "};",
        "",
    ])
    SOURCE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {HEADER}")
    print(f"Generated {SOURCE}")


if __name__ == "__main__":
    main()
