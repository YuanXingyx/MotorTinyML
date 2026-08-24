"""Capture one reproducible overload UART run without mixing debug lines."""

from __future__ import annotations

import csv
import math
import statistics
from datetime import datetime
from pathlib import Path

import serial


SERIAL_PORT = "COM7"
BAUDRATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
TARGET_SAMPLES = 3000
MIN_SAMPLES = 3000
MAX_SAMPLES = 4000
WINDOW_SIZE = 200

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "raw" / "overload_realtime"
REPORT_PATH = PROJECT_ROOT / "dataset" / "reports" / "stage_d3_overload_recollection.txt"


def parse_sample(line: str) -> tuple[int, int, int, int] | None:
    """Accept only timestamp,x,y,z integer rows; ignore every debug line."""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 4:
        return None
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def ask_run_number() -> int:
    while True:
        value = input("Overload run number (1-3): ").strip()
        if value in {"1", "2", "3"}:
            return int(value)
        print("Please enter 1, 2, or 3.")


def summarize(samples: list[tuple[int, int, int, int]]) -> list[str]:
    if not samples:
        return ["sample_count: 0", "status: NO_VALID_SAMPLES"]
    timestamps = [row[0] for row in samples]
    axes = [[row[index] for row in samples] for index in (1, 2, 3)]
    intervals = [later - earlier for earlier, later in zip(timestamps, timestamps[1:])]
    positive_intervals = [delta for delta in intervals if delta > 0]
    vibration_values = []
    for start in range(0, len(samples) - WINDOW_SIZE + 1, WINDOW_SIZE):
        window_axes = [[row[index] for row in samples[start : start + WINDOW_SIZE]] for index in (1, 2, 3)]
        centered_std = [statistics.pstdev(axis) for axis in window_axes]
        vibration_values.append(math.sqrt(sum(value * value for value in centered_std) / 3.0))

    lines = [
        f"sample_count: {len(samples)}",
        f"duration_s: {(timestamps[-1] - timestamps[0]) / 1000.0:.3f}",
        f"avg_interval_ms: {statistics.mean(positive_intervals):.3f}" if positive_intervals else "avg_interval_ms: N/A",
        f"timestamp_nonpositive_jumps: {sum(delta <= 0 for delta in intervals)}",
        f"timestamp_large_jumps_over_100ms: {sum(delta > 100 for delta in intervals)}",
        f"duplicate_rows: {sum(first == second for first, second in zip(samples, samples[1:]))}",
        f"complete_windows: {len(samples) // WINDOW_SIZE}",
        f"discarded_samples: {len(samples) % WINDOW_SIZE}",
    ]
    for axis_name, values in zip(("x", "y", "z"), axes):
        lines.extend([
            f"{axis_name}_min: {min(values)}",
            f"{axis_name}_max: {max(values)}",
            f"{axis_name}_mean: {statistics.mean(values):.3f}",
            f"{axis_name}_std_population: {statistics.pstdev(values):.3f}",
            f"{axis_name}_rms: {math.sqrt(statistics.mean(value * value for value in values)):.3f}",
        ])
    if vibration_values:
        lines.extend([
            f"vibration_metric_mean: {statistics.mean(vibration_values):.3f}",
            f"vibration_metric_min: {min(vibration_values):.3f}",
            f"vibration_metric_max: {max(vibration_values):.3f}",
        ])
    return lines


def append_report(run_number: int, output_file: Path, samples: list[tuple[int, int, int, int]]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_report = not REPORT_PATH.exists()
    with REPORT_PATH.open("a", encoding="utf-8") as report:
        if new_report:
            report.write("MotorTinyML Stage D-3 Overload Recollection\n")
            report.write("=========================================\n\n")
            report.write("Collection constraints\n-----------------------\n")
            report.write("Use a fixed, repeatable resistance method; do not press the motor by hand unpredictably.\n")
            report.write("The motor must continue rotating; complete stall is not allowed.\n")
            report.write("Each run must be independently started with the same resistance position and method.\n\n")
        report.write(f"Run {run_number}: {output_file}\n")
        report.write("-" * 48 + "\n")
        report.write("\n".join(summarize(samples)) + "\n")
        report.write("result: PENDING_MANUAL_REVIEW\n\n")
        report.write("Comparison with normal realtime: PENDING\n")
        report.write("Training inclusion decision: PENDING; no automatic inclusion or deletion.\n\n")


def main() -> None:
    run_number = ask_run_number()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"motor_overload_realtime_{run_number:02d}.csv"
    samples: list[tuple[int, int, int, int]] = []
    print(f"Capture run {run_number} using {SERIAL_PORT} @ {BAUDRATE}.")
    print("Use a fixed overload method; keep the motor rotating and do not stall it.")
    print(f"Target: {TARGET_SAMPLES}-{MAX_SAMPLES} valid samples. Press Ctrl+C to stop.")
    try:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT_SECONDS) as ser, output_file.open("w", newline="", encoding="utf-8") as csv_file:
            ser.reset_input_buffer()
            writer = csv.writer(csv_file)
            writer.writerow(["timestamp_ms", "x", "y", "z"])
            while len(samples) < MAX_SAMPLES:
                raw_line = ser.readline()
                if not raw_line:
                    continue
                sample = parse_sample(raw_line.decode("utf-8", errors="ignore").strip())
                if sample is None:
                    continue
                samples.append(sample)
                writer.writerow(sample)
                if len(samples) % 200 == 0:
                    csv_file.flush()
                    print(f"valid_samples={len(samples)}")
                if len(samples) >= TARGET_SAMPLES:
                    print("Target sample count reached; stop this run or continue manually up to 4000.")
                    break
    except KeyboardInterrupt:
        print("Capture stopped by user.")
    except (serial.SerialException, OSError) as exc:
        print(f"Capture error: {exc}")
    finally:
        append_report(run_number, output_file, samples)
        print(f"Saved: {output_file}")
        print(f"Valid samples: {len(samples)}")
        print(f"Report: {REPORT_PATH}")
        if len(samples) < MIN_SAMPLES:
            print("WARNING: fewer than 3000 valid samples; do not treat this run as formal data yet.")


if __name__ == "__main__":
    main()
