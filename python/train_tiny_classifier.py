"""Stage C-1: lightweight, CSV-level LORO fault classifier experiment.

This experiment deliberately avoids TensorFlow/TFLite.  It extracts statistics
that can be reproduced with small integer accumulators on the STM32F103 and
compares simple scikit-learn classifiers using strict CSV-level isolation.
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - dependency message
    raise SystemExit("Missing NumPy. Install numpy and scikit-learn to run this experiment.") from exc

try:
    from dataset_audit import audit_csv
except ImportError as exc:  # pragma: no cover - invocation guidance
    raise SystemExit("Run from the project root: py python/train_tiny_classifier.py") from exc


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "dataset" / "raw"
REPORT_DIR = ROOT_DIR / "dataset" / "reports"
REPORT_PATH = REPORT_DIR / "tiny_classifier_loro.txt"
CONFUSION_PATH = REPORT_DIR / "tiny_classifier_confusion_matrix.png"
IMPORTANCE_PATH = REPORT_DIR / "tiny_classifier_feature_importance.txt"
WINDOW_SIZE = 200
SEED = 42
N_FOLDS = 3
CLASS_NAMES = ["normal", "rotor_unbalance", "mechanical_looseness", "overload"]
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}

FEATURE_NAMES = [
    f"{axis}_{stat}"
    for axis in ("x", "y", "z")
    for stat in ("mean", "std", "rms", "min", "max", "peak_to_peak", "mad")
]


def load_windows(csv_path: Path, window_size: int = WINDOW_SIZE) -> np.ndarray:
    """Load complete raw windows without changing the source CSV."""
    samples: list[list[float]] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        expected = ["timestamp_ms", "x", "y", "z"]
        if reader.fieldnames != expected:
            raise ValueError(f"{csv_path.name}: header must be {expected!r}")
        for row in reader:
            samples.append([float(row["x"]), float(row["y"]), float(row["z"])])
    complete = len(samples) // window_size
    if complete == 0:
        return np.empty((0, window_size, 3), dtype=np.float32)
    values = np.asarray(samples[: complete * window_size], dtype=np.float32)
    return values.reshape(complete, window_size, 3)


def extract_features(windows: np.ndarray) -> np.ndarray:
    """Return 21 per-axis statistics for every 200-sample window."""
    if len(windows) == 0:
        return np.empty((0, len(FEATURE_NAMES)), dtype=np.float64)
    windows = np.asarray(windows, dtype=np.float64)
    mean = windows.mean(axis=1)
    centered = windows - mean[:, None, :]
    std = windows.std(axis=1, ddof=0)
    rms = np.sqrt(np.mean(np.square(windows), axis=1))
    minimum = windows.min(axis=1)
    maximum = windows.max(axis=1)
    peak_to_peak = maximum - minimum
    mad = np.mean(np.abs(centered), axis=1)
    # Keep axis-major ordering aligned with FEATURE_NAMES and future C export:
    # x_mean..x_mad, y_mean..y_mad, z_mean..z_mad.
    features = np.stack((mean, std, rms, minimum, maximum, peak_to_peak, mad), axis=2).reshape(
        len(windows), 21
    )
    if not np.all(np.isfinite(features)):
        raise ValueError("Feature extraction produced NaN or Inf values.")
    return features


def build_groups(speeds: set[int] | None) -> tuple[dict[tuple[str, int], list[Path]], list[str]]:
    """Select only dataset_audit.py INCLUDED files and group by class/speed."""
    groups: dict[tuple[str, int], list[Path]] = defaultdict(list)
    for path in sorted(RAW_DIR.rglob("*.csv")):
        result = audit_csv(path)
        if (
            result["status"] == "INCLUDED"
            and result["class"] in CLASS_TO_INDEX
            and (speeds is None or result["speed"] in speeds)
        ):
            groups[(result["class"], result["speed"])].append(path)
    warnings: list[str] = []
    for key, files in sorted(groups.items()):
        if len(files) != N_FOLDS:
            warnings.append(f"{key[0]}_{key[1]} has {len(files)} INCLUDED CSV files; expected 3.")
        if len(files) < N_FOLDS:
            raise ValueError(f"{key[0]}_{key[1]} needs at least 3 INCLUDED CSV files, found {len(files)}")
    if not groups:
        raise ValueError("No INCLUDED four-class CSV files were found.")
    return groups, warnings


def fold_files(groups: dict[tuple[str, int], list[Path]], fold_index: int) -> tuple[list[Path], list[Path]]:
    """Use the same deterministic per-group rotation as the CNN LORO experiment."""
    train_files: list[Path] = []
    test_files: list[Path] = []
    for (class_name, speed), source_files in sorted(groups.items()):
        files = sorted(source_files)
        rng = random.Random(SEED + sum(ord(char) for char in f"{class_name}_{speed}"))
        rng.shuffle(files)
        test_index = fold_index % len(files)
        test_files.append(files[test_index])
        train_files.extend(path for index, path in enumerate(files) if index != test_index)
    return train_files, test_files


def collect(files: list[Path]) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    feature_rows: list[np.ndarray] = []
    labels: list[int] = []
    metadata: list[dict[str, object]] = []
    for path in files:
        audit = audit_csv(path)
        windows = load_windows(path)
        features = extract_features(windows)
        class_name = str(audit["class"])
        feature_rows.append(features)
        labels.extend([CLASS_TO_INDEX[class_name]] * len(features))
        metadata.extend(
            {"source_csv": path.name, "class": class_name, "speed": int(audit["speed"])}
            for _ in range(len(features))
        )
    if not feature_rows:
        return np.empty((0, len(FEATURE_NAMES))), np.empty(0, dtype=np.int64), []
    return np.concatenate(feature_rows), np.asarray(labels, dtype=np.int64), metadata


def make_classifiers():
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import LinearSVC
        from sklearn.tree import DecisionTreeClassifier
    except ImportError as exc:  # pragma: no cover - dependency message
        raise SystemExit("Missing scikit-learn. Install scikit-learn to run Stage C-1.") from exc
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=2000, solver="lbfgs", random_state=SEED
        ),
        "Linear SVM": LinearSVC(C=1.0, random_state=SEED, max_iter=5000),
        "Decision Tree": DecisionTreeClassifier(max_depth=4, min_samples_leaf=2, random_state=SEED),
    }


def fit_scale(train_x: np.ndarray, other_x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Standardize from train only; returned mean/std are deployment metadata."""
    mean = train_x.mean(axis=0)
    std = train_x.std(axis=0)
    std[std == 0] = 1.0
    return (train_x - mean) / std, (other_x - mean) / std, mean, std


def model_importance(model) -> np.ndarray:
    if hasattr(model, "coef_"):
        return np.mean(np.abs(np.asarray(model.coef_, dtype=float)), axis=0)
    if hasattr(model, "feature_importances_"):
        return np.asarray(model.feature_importances_, dtype=float)
    return np.zeros(len(FEATURE_NAMES), dtype=float)


def format_distribution(values: np.ndarray) -> str:
    return ", ".join(
        f"{CLASS_NAMES[index]}={int(np.sum(values == index))}" for index in range(len(CLASS_NAMES))
    )


def evaluate_models(groups: dict[tuple[str, int], list[Path]], classifier_names: list[str]):
    from sklearn.metrics import accuracy_score

    results: dict[str, dict[str, object]] = {}
    for name in classifier_names:
        fold_records = []
        aggregate_true: list[int] = []
        aggregate_pred: list[int] = []
        importances: list[np.ndarray] = []
        for fold_index in range(N_FOLDS):
            train_files, test_files = fold_files(groups, fold_index)
            train_x, train_y, _ = collect(train_files)
            test_x, test_y, test_metadata = collect(test_files)
            train_scaled, test_scaled, mean, std = fit_scale(train_x, test_x)
            model = make_classifiers()[name]
            model.fit(train_scaled, train_y)
            predictions = model.predict(test_scaled)
            accuracy = float(accuracy_score(test_y, predictions))
            aggregate_true.extend(test_y.tolist())
            aggregate_pred.extend(predictions.tolist())
            importances.append(model_importance(model))
            fold_records.append(
                {
                    "fold": fold_index + 1,
                    "train_files": train_files,
                    "test_files": test_files,
                    "train_windows": len(train_y),
                    "test_windows": len(test_y),
                    "accuracy": accuracy,
                    "mean": mean,
                    "std": std,
                    "true": test_y,
                    "pred": predictions,
                    "metadata": test_metadata,
                    "model": model,
                }
            )
        fold_accuracies = np.asarray([record["accuracy"] for record in fold_records], dtype=float)
        results[name] = {
            "folds": fold_records,
            "fold_accuracies": fold_accuracies,
            "mean_accuracy": float(fold_accuracies.mean()),
            "std_accuracy": float(fold_accuracies.std()),
            "true": np.asarray(aggregate_true),
            "pred": np.asarray(aggregate_pred),
            "importance": np.mean(importances, axis=0),
        }
    return results


def choose_model(results: dict[str, dict[str, object]]) -> str:
    """Accuracy first; when within one point, prefer linear/simple deployment."""
    best_accuracy = max(float(item["mean_accuracy"]) for item in results.values())
    close = [name for name, item in results.items() if best_accuracy - float(item["mean_accuracy"]) <= 0.01]
    simplicity = {"Logistic Regression": 0, "Linear SVM": 1, "Decision Tree": 2}
    return min(close, key=lambda name: simplicity[name])


def render_confusion(results: dict[str, dict[str, object]], model_name: str) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import confusion_matrix
    except ImportError:
        return False
    item = results[model_name]
    matrix = confusion_matrix(item["true"], item["pred"], labels=list(range(4)))
    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(xticks=range(4), yticks=range(4), xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
             xlabel="Predicted", ylabel="True", title=f"Tiny classifier LORO: {model_name}")
    for row in range(4):
        for column in range(4):
            axis.text(column, row, int(matrix[row, column]), ha="center", va="center")
    figure.tight_layout()
    figure.savefig(CONFUSION_PATH, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return True


def render_reports(groups, warnings, results, best_name, speeds) -> None:
    from sklearn.metrics import classification_report, confusion_matrix

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    best = results[best_name]
    lines = [
        "MotorTinyML Stage C-1 Tiny Classifier LORO Experiment",
        "=" * 55,
        "",
        "experiment: feature extraction + lightweight classifier (no TensorFlow/TFLite)",
        f"included_speeds: {', '.join(map(str, sorted(speeds))) if speeds else '40, 60, 80'}",
        f"window_size: {WINDOW_SIZE}",
        f"feature_count: {len(FEATURE_NAMES)}",
        "features: " + ", ".join(FEATURE_NAMES),
        "feature_definition: per-axis mean, population std, RMS, min, max, peak_to_peak, mean absolute deviation",
        "split: CSV-level leave-one-run-out; each class+speed has one unseen test CSV per fold",
        "scaling: mean/std fit only on each fold's train windows, then applied to test windows",
        "",
        "Dataset groups",
        "-" * 20,
    ]
    for key, files in sorted(groups.items()):
        lines.append(f"{key[0]}_{key[1]}: {len(files)} INCLUDED CSV files")
    if warnings:
        lines.extend(["", "Warnings", *[f"- {warning}" for warning in warnings]])

    lines.extend(["", "Classifier results", "-" * 20])
    for name, item in results.items():
        lines.extend([
            f"\n{name}",
            f"configuration: {item['folds'][0]['model'].get_params()}",
            "fold accuracies: " + ", ".join(f"{value:.4f}" for value in item["fold_accuracies"]),
            f"LORO mean accuracy: {item['mean_accuracy']:.4f}",
            f"LORO std accuracy: {item['std_accuracy']:.4f}",
            "aggregate confusion matrix:",
            str(confusion_matrix(item["true"], item["pred"], labels=list(range(4)))),
            "aggregate classification report:",
            classification_report(item["true"], item["pred"], labels=list(range(4)), target_names=CLASS_NAMES, zero_division=0),
        ])
        for fold in item["folds"]:
            lines.append(
                f"fold {fold['fold']}: train_csv={len(fold['train_files'])}, train_windows={fold['train_windows']}, "
                f"test_csv={len(fold['test_files'])}, test_windows={fold['test_windows']}, "
                f"test_accuracy={fold['accuracy']:.4f}"
            )
            lines.append("  train: " + ", ".join(path.name for path in fold["train_files"]))
            lines.append("  test: " + ", ".join(path.name for path in fold["test_files"]))
    best_report = classification_report(best["true"], best["pred"], labels=list(range(4)), target_names=CLASS_NAMES, output_dict=True, zero_division=0)
    lines.extend([
        "Model selection",
        "-" * 20,
        f"best_classifier: {best_name}",
        "selection_rule: LORO mean accuracy first; within 0.010, prefer Logistic Regression, then Linear SVM, then small Decision Tree.",
        f"mechanical_looseness recall: {best_report['mechanical_looseness']['recall']:.4f}",
        "",
        "CNN reference (existing experiment)",
        "-" * 20,
        "CNN LORO mean accuracy: 0.9926",
        "CNN LORO std accuracy: 0.0060",
        "CNN mechanical_looseness recall: 0.97",
        "The CNN figures are an independent reference, not a target used to fit this experiment.",
        "",
        "STM32F103 implementation estimate",
        "-" * 20,
        "Feature extraction: 21 statistics over 200x3 samples; integer sums/sums-of-squares and min/max are pure-C friendly.",
        "Logistic/linear model: 4*21 weights + 4 biases = 88 parameters (about 352 bytes at float32, before optional fixed-point packing).",
        "Decision Tree (max_depth=4): at most 31 nodes; estimated <1.5 KiB including thresholds, feature indices and leaf outputs.",
        "Runtime RAM: approximately 1.2 KiB for a retained int16 200x3 window, plus <0.5 KiB feature/scaler/model working state; streaming accumulation can reduce this.",
        "Compute: one pass over 600 samples plus 84 feature-weight products for a linear classifier; no FFT or dynamic allocation required.",
        "These are engineering estimates; C fixed-point representation and compiler layout must be measured in Stage C-2.",
        "",
        "Known limitations",
        "- only three independent runs per class+speed are available",
        "- fan-related experimental confounding remains unresolved",
        "- diagnostic accuracy does not establish unknown-device generalization",
    ])
    png_status = render_confusion(results, best_name)
    lines.append(f"confusion_matrix_png: {CONFUSION_PATH if png_status else 'not generated (matplotlib unavailable)'}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    importance_lines = [
        f"Best classifier: {best_name}",
        "Feature importance is mean absolute coefficient (linear models) or split importance (tree), averaged across LORO folds.",
        "",
    ]
    for index in np.argsort(-best["importance"]):
        importance_lines.append(f"{FEATURE_NAMES[index]}: {best['importance'][index]:.8f}")
    IMPORTANCE_PATH.write_text("\n".join(importance_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train lightweight pure-C-friendly classifiers with CSV-level LORO CV.")
    parser.add_argument("--speeds", nargs="+", type=int, choices=(40, 60, 80), help="Restrict included speeds.")
    args = parser.parse_args()
    speeds = set(args.speeds) if args.speeds else None
    np.random.seed(SEED)
    groups, warnings = build_groups(speeds)
    results = evaluate_models(groups, ["Logistic Regression", "Linear SVM", "Decision Tree"])
    best_name = choose_model(results)
    render_reports(groups, warnings, results, best_name, speeds)
    best = results[best_name]
    print(f"Best classifier: {best_name}")
    print(f"Feature count: {len(FEATURE_NAMES)}")
    print(f"LORO mean/std accuracy: {best['mean_accuracy']:.4f} / {best['std_accuracy']:.4f}")
    print(f"Report: {REPORT_PATH}")
    print(f"Feature importance: {IMPORTANCE_PATH}")
    print(f"Confusion matrix: {CONFUSION_PATH}")


if __name__ == "__main__":
    main()
