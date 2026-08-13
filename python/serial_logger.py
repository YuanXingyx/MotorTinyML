import csv
from datetime import datetime
from pathlib import Path

import serial


SERIAL_PORT = "COM3"
BAUDRATE = 115200
SERIAL_TIMEOUT_SECONDS = 1

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / "dataset" / "raw"


def parse_sample(line: str) -> tuple[int, int, int, int] | None:
    """Parse one CSV-like sensor line; return None for logs or malformed data."""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 4:
        return None


def get_label() -> str:
    """Read and normalize the acquisition-condition label."""
    label = input("请输入采集工况 label（直接回车使用 unlabeled）: ").strip()
    label = "_".join(label.split())
    return label or "unlabeled"

    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def main() -> None:
    label = get_label()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"{label}_{timestamp}.csv"
    sample_count = 0

    try:
        with serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=SERIAL_TIMEOUT_SECONDS,
        ) as ser, output_file.open("w", newline="", encoding="utf-8") as csv_file:
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

                writer.writerow(sample)
                csv_file.flush()
                sample_count += 1

    except serial.SerialException as exc:
        print(f"串口错误: {exc}")
    except OSError as exc:
        print(f"文件错误: {exc}")
    except KeyboardInterrupt:
        print("\n采集已停止")
    finally:
        print(f"有效样本数: {sample_count}")
        print(f"CSV 已保存到: {output_file}")


if __name__ == "__main__":
    main()

