import argparse
import csv
import sys
from pathlib import Path


SAMPLE_RATE_HZ = 200
WINDOW_SECONDS = 1
WINDOW_SIZE = SAMPLE_RATE_HZ * WINDOW_SECONDS
OVERLAP = 0
EXPECTED_HEADER = ["timestamp_ms", "x", "y", "z"]
MIN_ACCEPTABLE_RATE_HZ = 180.0
MAX_ACCEPTABLE_RATE_HZ = 220.0


def load_samples(csv_path: Path) -> list[tuple[int, int, int, int]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV 文件不存在: {csv_path}")
    if csv_path.stat().st_size == 0:
        raise ValueError(f"CSV 文件为空: {csv_path}")

    samples: list[tuple[int, int, int, int]] = []
    previous_timestamp: int | None = None

    with csv_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if header != EXPECTED_HEADER:
            raise ValueError(
                f"CSV 表头错误，期望 {EXPECTED_HEADER}，实际 {header}"
            )

        for line_number, row in enumerate(reader, start=2):
            if len(row) != 4:
                raise ValueError(f"第 {line_number} 行字段数错误: {row}")
            try:
                sample = tuple(int(value.strip()) for value in row)
            except ValueError as exc:
                raise ValueError(f"第 {line_number} 行包含非法整数: {row}") from exc

            timestamp = sample[0]
            if previous_timestamp is not None and timestamp <= previous_timestamp:
                raise ValueError(
                    f"第 {line_number} 行 timestamp 非单调递增: "
                    f"{previous_timestamp} -> {timestamp}"
                )
            samples.append(sample)
            previous_timestamp = timestamp

    if not samples:
        raise ValueError(f"CSV 没有有效数据: {csv_path}")
    return samples


def calculate_timing(samples: list[tuple[int, int, int, int]]) -> tuple[float, float]:
    intervals = [
        current[0] - previous[0]
        for previous, current in zip(samples, samples[1:])
    ]
    if not intervals:
        return 0.0, 0.0

    average_interval_ms = sum(intervals) / len(intervals)
    estimated_rate_hz = (
        1000.0 / average_interval_ms if average_interval_ms > 0 else 0.0
    )
    return average_interval_ms, estimated_rate_hz


def write_processed_csv(
    output_path: Path,
    samples: list[tuple[int, int, int, int]],
    label: str,
) -> tuple[int, int]:
    complete_windows = len(samples) // WINDOW_SIZE
    discarded_samples = len(samples) % WINDOW_SIZE

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["window_index", "label", "sample_index", "timestamp_ms", "x", "y", "z"]
        )
        for window_index in range(complete_windows):
            start = window_index * WINDOW_SIZE
            window = samples[start : start + WINDOW_SIZE]
            for sample_index, (timestamp, x, y, z) in enumerate(window):
                writer.writerow(
                    [window_index, label, sample_index, timestamp, x, y, z]
                )

    return complete_windows, discarded_samples


def write_metadata(
    metadata_path: Path,
    source_path: Path,
    label: str,
    samples: list[tuple[int, int, int, int]],
    complete_windows: int,
    discarded_samples: int,
    average_interval_ms: float,
    estimated_rate_hz: float,
) -> None:
    with metadata_path.open("w", encoding="utf-8") as file:
        file.write(f"source_file: {source_path}\n")
        file.write(f"label: {label}\n")
        file.write(f"sample_rate_hz: {SAMPLE_RATE_HZ}\n")
        file.write(f"total_samples: {len(samples)}\n")
        file.write(f"window_size: {WINDOW_SIZE}\n")
        file.write(f"window_seconds: {WINDOW_SECONDS}\n")
        file.write(f"complete_windows: {complete_windows}\n")
        file.write(f"discarded_samples: {discarded_samples}\n")
        file.write(f"average_interval_ms: {average_interval_ms:.3f}\n")
        file.write(f"estimated_sample_rate_hz: {estimated_rate_hz:.3f}\n")


def process(csv_path: Path, label: str) -> tuple[Path, Path, int, int]:
    if not label.strip():
        raise ValueError("label 不能为空")
    samples = load_samples(csv_path)
    average_interval_ms, estimated_rate_hz = calculate_timing(samples)
    if not MIN_ACCEPTABLE_RATE_HZ <= estimated_rate_hz <= MAX_ACCEPTABLE_RATE_HZ:
        raise ValueError(
            f"估算采样频率 {estimated_rate_hz:.3f} Hz 偏离目标 200 Hz"
        )
    if len(samples) < WINDOW_SIZE:
        raise ValueError(
            f"样本数量 {len(samples)} 少于一个完整 window ({WINDOW_SIZE})"
        )

    output_dir = csv_path.parents[1] / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = output_dir / f"{csv_path.stem}_windows.csv"
    output_meta = output_dir / f"{csv_path.stem}_windows_meta.txt"
    complete_windows, discarded_samples = write_processed_csv(
        output_csv, samples, label
    )
    write_metadata(
        output_meta,
        csv_path,
        label,
        samples,
        complete_windows,
        discarded_samples,
        average_interval_ms,
        estimated_rate_hz,
    )
    print(f"total_samples: {len(samples)}")
    print(f"window_size: {WINDOW_SIZE}")
    print(f"complete_windows: {complete_windows}")
    print(f"discarded_samples: {discarded_samples}")
    print(f"shape: ({complete_windows}, {WINDOW_SIZE}, 3)")
    print(f"processed_csv: {output_csv}")
    print(f"metadata: {output_meta}")
    return output_csv, output_meta, complete_windows, discarded_samples


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert raw ADXL345 CSV to fixed windows")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    try:
        process(args.csv_path, args.label)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
