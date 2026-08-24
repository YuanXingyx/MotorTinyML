"""Final UART CSV capture entry point for MotorTinyML demo datasets."""

from __future__ import annotations

import csv
from pathlib import Path

import serial

from capture_overload_realtime import summarize

SERIAL_PORT = "COM7"
BAUDRATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
TARGET_SAMPLES = 3000
MAX_TIMESTAMP_DELTA_MS = 100
FINAL_DEMO_CLASSES = ("normal", "rotor_unbalance", "overload")
FINAL_DEMO_RUNS = (1, 2, 3)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "raw" / "final_demo"
REPORT_PATH = PROJECT_ROOT / "dataset" / "reports" / "stage_d4_final_demo_collection.txt"


def parse_sample(line: str) -> tuple[int, int, int, int] | None:
    """Parse only timestamp,x,y,z integer rows; ignore all UART diagnostics."""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 4:
        return None
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def ask_condition() -> str:
    while True:
        value = input("Condition (normal/rotor_unbalance/overload): ").strip().lower()
        if value in FINAL_DEMO_CLASSES:
            return value
        print("Please enter normal, rotor_unbalance, or overload.")


def ask_run_number() -> int:
    while True:
        value = input("Run number (1-3): ").strip()
        if value in {str(run) for run in FINAL_DEMO_RUNS}:
            return int(value)
        print("Please enter 1, 2, or 3.")


def append_report(condition: str, run_number: int, output_file: Path,
                  samples: list[tuple[int, int, int, int]], dataset_usable: bool) -> None:
    """Append the shared capture quality summary to the final-demo report."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_report = not REPORT_PATH.exists()
    with REPORT_PATH.open("a", encoding="utf-8") as report:
        if new_report:
            report.write("MotorTinyML Stage D-4 Final Demo Dataset Collection\n")
            report.write("===============================================\n\n")
            report.write("Recommended capture entry: python/serial_logger.py\n")
            report.write("Historical capture_overload_realtime.py is retained for diagnostics.\n\n")
            report.write("Fixed baseline: one fan blade, ADXL345 position/orientation, I2C, "
                         "200 Hz, UART 115200, and Motor_SetSpeed(60).\n")
            report.write("Each class requires three independently started runs.\n\n")
        report.write(f"Condition: {condition}\nRun: {run_number}\nCSV: {output_file}\n")
        report.write("-" * 60 + "\n")
        report.write("\n".join(summarize(samples)) + "\n")
        report.write(f"dataset_usable: {'YES' if dataset_usable else 'NO'}\n\n")


def quality_passed(samples: list[tuple[int, int, int, int]]) -> bool:
    """Require a complete, continuous 3000-sample run before promotion."""
    if len(samples) != TARGET_SAMPLES:
        return False
    if any(later[0] - earlier[0] <= 0 or
           later[0] - earlier[0] > MAX_TIMESTAMP_DELTA_MS
           for earlier, later in zip(samples, samples[1:])):
        return False
    return not any(first == second for first, second in zip(samples, samples[1:]))


def main() -> None:
    condition = ask_condition()
    run_number = ask_run_number()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"motor_final_{condition}_{run_number:02d}.csv"
    if output_file.exists():
        raise FileExistsError(f"Refusing to overwrite existing formal CSV: {output_file}")
    partial_file = output_file.with_suffix(".partial")
    if partial_file.exists():
        raise FileExistsError(f"Refusing to overwrite existing partial capture: {partial_file}")

    samples: list[tuple[int, int, int, int]] = []
    candidate_sample: tuple[int, int, int, int] | None = None
    first_timestamp_ms: int | None = None
    last_timestamp_ms: int | None = None
    formal_collection_started = False
    dataset_usable = False
    print(f"Capture {condition} run {run_number}: {SERIAL_PORT} @ {BAUDRATE} 8-N-1")
    print(f"Target: {TARGET_SAMPLES} valid samples")
    print("Keep the approved mechanical configuration unchanged. Press Ctrl+C to stop.")

    try:
        with serial.Serial(port=SERIAL_PORT, baudrate=BAUDRATE,
                           bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=SERIAL_TIMEOUT_SECONDS) as ser, \
             partial_file.open("w", newline="", encoding="utf-8") as csv_file:
            ser.reset_input_buffer()
            writer = csv.writer(csv_file)
            writer.writerow(["timestamp_ms", "x", "y", "z"])
            while len(samples) < TARGET_SAMPLES:
                raw_line = ser.readline()
                if not raw_line:
                    continue
                sample = parse_sample(raw_line.decode("utf-8", errors="ignore").strip())
                if sample is None:
                    continue
                current_timestamp_ms = sample[0]
                if not formal_collection_started:
                    if candidate_sample is None:
                        candidate_sample = sample
                        continue
                    delta_ms = current_timestamp_ms - candidate_sample[0]
                    if not 0 < delta_ms <= MAX_TIMESTAMP_DELTA_MS:
                        print(f"Timestamp startup jump ignored: delta_ms={delta_ms}")
                        candidate_sample = sample
                        continue
                    first_timestamp_ms = candidate_sample[0]
                    last_timestamp_ms = current_timestamp_ms
                    formal_collection_started = True
                    dataset_usable = True
                    samples.extend((candidate_sample, sample))
                    writer.writerows((candidate_sample, sample))
                    csv_file.flush()
                    print(f"valid_samples={len(samples)}")
                    candidate_sample = None
                    continue
                delta_ms = current_timestamp_ms - last_timestamp_ms  # type: ignore[operator]
                if not 0 < delta_ms <= MAX_TIMESTAMP_DELTA_MS:
                    dataset_usable = False
                    print(f"Timestamp continuity error: delta_ms={delta_ms}; capture stopped.")
                    print("WARNING: this CSV must not be used as a formal dataset.")
                    break
                samples.append(sample)
                writer.writerow(sample)
                csv_file.flush()
                last_timestamp_ms = current_timestamp_ms
                if len(samples) % 200 == 0 or len(samples) == TARGET_SAMPLES:
                    print(f"valid_samples={len(samples)}")
    except KeyboardInterrupt:
        print("Capture stopped by user.")
    except (serial.SerialException, OSError) as exc:
        print(f"Capture error: {exc}")
    finally:
        dataset_usable = dataset_usable and quality_passed(samples)
        report_file = output_file if dataset_usable else partial_file
        if dataset_usable:
            partial_file.replace(output_file)
            print("Quality checks passed; partial capture promoted to formal CSV.")
        else:
            print(f"Capture retained as partial only: {partial_file}")
            print("It must not be used as a formal dataset.")
        append_report(condition, run_number, report_file, samples, dataset_usable)
        duration_s = ((last_timestamp_ms - first_timestamp_ms) / 1000.0
                      if first_timestamp_ms is not None and last_timestamp_ms is not None else 0.0)
        print(f"Valid samples: {len(samples)}")
        print(f"Actual duration: {duration_s:.3f} s")
        print(f"CSV path: {report_file}")
        print(f"Quality report: {REPORT_PATH}")
        if len(samples) < TARGET_SAMPLES:
            print("WARNING: fewer than 3000 valid samples; review before training use.")


if __name__ == "__main__":
    main()
