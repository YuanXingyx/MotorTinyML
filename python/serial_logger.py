import csv
from datetime import datetime
from pathlib import Path

import serial


SERIAL_PORT = "COM3"
BAUDRATE = 115200
SERIAL_TIMEOUT_SECONDS = 1
DURATION_SECONDS = 15

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "raw"


def parse_sample(line: str) -> tuple[int, int, int, int] | None:
    """Parse one CSV-like sensor line; return None for logs or malformed data."""

    parts = [part.strip() for part in line.split(",")]

    if len(parts) != 4:
        return None

    try:
        timestamp_ms = int(parts[0])
        x = int(parts[1])
        y = int(parts[2])
        z = int(parts[3])
    except ValueError:
        return None

    return timestamp_ms, x, y, z


def get_label() -> str:
    """Read and normalize the acquisition-condition label."""
    label = input("请输入采集工况 label（直接回车使用 unlabeled）: ").strip()
    label = "_".join(label.split())
    return label or "unlabeled"


def main() -> None:
    label = get_label()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"{label}_{timestamp}.csv"
    sample_count = 0
    first_timestamp_ms: int | None = None
    last_timestamp_ms: int | None = None
    candidate_sample: tuple[int, int, int, int] | None = None
    formal_collection_started = False
    dataset_usable = False

    try:
        with serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=SERIAL_TIMEOUT_SECONDS,
        ) as ser, output_file.open("w", newline="", encoding="utf-8") as csv_file:
            ser.reset_input_buffer()

            writer = csv.writer(csv_file)
            writer.writerow(["timestamp_ms", "x", "y", "z"])
            csv_file.flush()

            print(f"开始采集: {SERIAL_PORT} @ {BAUDRATE} baud")
            print(f"输出文件: {output_file}")
            print("按 Ctrl+C 停止采集")

            while True:
                raw_line = ser.readline()
                if not raw_line:
                    continue

                line = raw_line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                print(line)
                sample = parse_sample(line)
                if sample is None:
                    continue

                current_timestamp_ms = sample[0]
                if not formal_collection_started:
                    if candidate_sample is None:
                        candidate_sample = sample
                        continue

                    delta_ms = current_timestamp_ms - candidate_sample[0]
                    if not 0 < delta_ms <= 100:
                        print(
                            f"起始时间戳异常: delta_ms={delta_ms}，"
                            "重新寻找连续采集起点"
                        )
                        candidate_sample = sample
                        continue

                    first_timestamp_ms = candidate_sample[0]
                    last_timestamp_ms = current_timestamp_ms
                    formal_collection_started = True
                    dataset_usable = True

                    writer.writerow(candidate_sample)
                    writer.writerow(sample)
                    csv_file.flush()
                    sample_count += 2
                    candidate_sample = None
                    continue

                delta_ms = current_timestamp_ms - last_timestamp_ms
                if not 0 < delta_ms <= 100:
                    dataset_usable = False
                    print(
                        f"时间戳异常: delta_ms={delta_ms}，采集已终止。"
                    )
                    print("警告：此次 CSV 数据不应作为正式数据集使用。")
                    break

                writer.writerow(sample)
                csv_file.flush()
                sample_count += 1
                last_timestamp_ms = current_timestamp_ms

                elapsed_ms = last_timestamp_ms - first_timestamp_ms
                if elapsed_ms >= DURATION_SECONDS * 1000:
                    print(f"达到 {DURATION_SECONDS} 秒采集时长，自动停止")
                    break

    except serial.SerialException as exc:
        print(f"串口错误: {exc}")
    except OSError as exc:
        print(f"文件错误: {exc}")
    except KeyboardInterrupt:
        print("\n采集已停止")
    finally:
        if first_timestamp_ms is not None and last_timestamp_ms is not None:
            actual_duration_seconds = (
                last_timestamp_ms - first_timestamp_ms
            ) / 1000.0
        else:
            actual_duration_seconds = 0.0
        print(f"有效样本数: {sample_count}")
        print(f"实际采集时长: {actual_duration_seconds:.3f} 秒")
        if formal_collection_started and dataset_usable:
            print("数据集状态: 可作为正式数据集使用")
        else:
            print("数据集状态: 不可作为正式数据集使用")
        print(f"CSV 已保存到: {output_file}")


if __name__ == "__main__":
    main()
