import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CSV_FILE = PROJECT_ROOT / "dataset" / "raw" / "motor_overload_60_20260820_181249.csv"
PLOTS_DIR = PROJECT_ROOT / "dataset" / "plots"
REPORTS_DIR = PROJECT_ROOT / "dataset" / "reports"
EXPECTED_HEADER = ["timestamp_ms", "x", "y", "z"]


def load_samples(csv_file: Path) -> tuple[list[int], list[int], list[int], list[int]]:
    """Load timestamp and raw XYZ samples from one ADXL345 CSV file."""
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_file}")
    if csv_file.stat().st_size == 0:
        raise ValueError(f"CSV 文件为空: {csv_file}")

    timestamps: list[int] = []
    x_values: list[int] = []
    y_values: list[int] = []
    z_values: list[int] = []

    with csv_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if header != EXPECTED_HEADER:
            raise ValueError(
                f"CSV 表头错误，期望 {EXPECTED_HEADER}，实际 {header}"
            )

        for line_number, row in enumerate(reader, start=2):
            if len(row) != 4:
                raise ValueError(f"第 {line_number} 行列数错误: {row}")
            try:
                timestamp_ms, x, y, z = (int(value.strip()) for value in row)
            except ValueError as exc:
                raise ValueError(f"第 {line_number} 行包含非整数数据: {row}") from exc

            timestamps.append(timestamp_ms)
            x_values.append(x)
            y_values.append(y)
            z_values.append(z)

    if not timestamps:
        raise ValueError(f"CSV 没有有效数据: {csv_file}")

    return timestamps, x_values, y_values, z_values


def calculate_statistics(
    timestamps: list[int],
    axes: dict[str, list[int]],
) -> dict:
    """Calculate basic axis and timing statistics once for reuse."""
    statistics = {
        "sample_count": len(timestamps),
        "axes": {},
        "duration_s": (timestamps[-1] - timestamps[0]) / 1000.0,
        "avg_interval_ms": None,
        "sampling_frequency_hz": None,
    }

    for axis, values in axes.items():
        mean = sum(values) / len(values)
        minimum = min(values)
        maximum = max(values)
        peak_to_peak = maximum - minimum
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        standard_deviation = math.sqrt(variance)
        statistics["axes"][axis.upper()] = {
            "mean": mean,
            "min": minimum,
            "max": maximum,
            "peak_to_peak": peak_to_peak,
            "std": standard_deviation,
        }

    intervals = [
        current - previous
        for previous, current in zip(timestamps, timestamps[1:])
    ]
    if intervals:
        average_interval_ms = sum(intervals) / len(intervals)
        statistics["avg_interval_ms"] = average_interval_ms
        statistics["sampling_frequency_hz"] = (
            1000.0 / average_interval_ms if average_interval_ms > 0 else 0.0
        )

    return statistics


def print_statistics(statistics: dict) -> None:
    """Print basic statistics and timing information for the recording."""
    print(f"样本数量: {statistics['sample_count']}")
    for axis, values in statistics["axes"].items():
        print(
            f"{axis}: mean={values['mean']:.3f}, min={values['min']}, "
            f"max={values['max']}, peak-to-peak={values['peak_to_peak']}, "
            f"std={values['std']:.3f}"
        )

    print(f"采集总时长: {statistics['duration_s']:.3f} s")
    if statistics["avg_interval_ms"] is not None:
        print(f"相邻时间戳平均间隔: {statistics['avg_interval_ms']:.3f} ms")
        print(
            f"估算平均采样频率: "
            f"{statistics['sampling_frequency_hz']:.3f} Hz"
        )
    else:
        print("相邻时间戳平均间隔: 无（样本不足）")
        print("估算平均采样频率: 无（样本不足）")


def save_statistics_report(statistics: dict, csv_file: Path) -> Path:
    """Save the calculated statistics beside the raw data as a TXT report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{csv_file.stem}_stats.txt"

    with report_file.open("w", encoding="utf-8") as file:
        file.write(f"sample_count: {statistics['sample_count']}\n")
        for axis in ("X", "Y", "Z"):
            values = statistics["axes"][axis]
            file.write(f"{axis}:\n")
            file.write(f"  mean: {values['mean']:.3f}\n")
            file.write(f"  min: {values['min']}\n")
            file.write(f"  max: {values['max']}\n")
            file.write(f"  peak_to_peak: {values['peak_to_peak']}\n")
            file.write(f"  std: {values['std']:.3f}\n")

        file.write(f"duration_s: {statistics['duration_s']:.3f}\n")
        if statistics["avg_interval_ms"] is None:
            file.write("avg_interval_ms: N/A\n")
            file.write("sampling_frequency_hz: N/A\n")
        else:
            file.write(
                f"avg_interval_ms: {statistics['avg_interval_ms']:.3f}\n"
            )
            file.write(
                "sampling_frequency_hz: "
                f"{statistics['sampling_frequency_hz']:.3f}\n"
            )

    print(f"统计结果已保存到: {report_file}")
    return report_file


def plot_samples(
    timestamps: list[int],
    x_values: list[int],
    y_values: list[int],
    z_values: list[int],
) -> None:
    """Plot raw ADXL345 XYZ acceleration against elapsed time."""
    start_timestamp = timestamps[0]
    time_s = [(timestamp - start_timestamp) / 1000.0 for timestamp in timestamps]

    plt.plot(time_s, x_values, label="X")
    plt.plot(time_s, y_values, label="Y")
    plt.plot(time_s, z_values, label="Z")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (raw)")
    plt.title("ADXL345 Raw Acceleration")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_file = PLOTS_DIR / f"{CSV_FILE.stem}.png"
    plt.savefig(plot_file, dpi=150, bbox_inches="tight")
    print(f"图片已保存到: {plot_file}")
    plt.show()


def main() -> int:
    try:
        samples = load_samples(CSV_FILE)
        timestamps, x_values, y_values, z_values = samples
        statistics = calculate_statistics(
            timestamps,
            {"x": x_values, "y": y_values, "z": z_values},
        )
        print_statistics(statistics)
        save_statistics_report(statistics, CSV_FILE)
        plot_samples(*samples)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
