# ISSUE-0029 — Multi-Speed Normal Dataset Collection

## 元数据

- 议题 ID：ISSUE-0029
- 类型：Dataset Acquisition
- 状态：REVIEW
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-19

## 目标

在保持传感器安装、硬件连接和采样配置不变的情况下，采集多个正常转速工况数据，避免未来模型将转速变化误判为故障。

## 固定实验条件

- STM32F103C8T6
- ADXL345 I²C
- 200 Hz ODR
- 5 ms timestamp interval
- UART 115200
- ADXL345 固定位置和朝向不变
- 电机固定方式、电源条件和 TB6612 接线保持一致
- 电机端子 100 nF 抗干扰电容保留
- TB6612 VM-GND 的 100 uF + 100 nF 去耦保留

采集过程中不移动传感器来制造数据差异。

## 采集计划

| 速度工况 | 目标采集次数 | 每次时长 | 每次预期样本 | 目标文件数 |
|---|---:|---:|---:|---:|
| `motor_normal_40` | 3 | 约 15 s | 约 3001 | 3 |
| `motor_normal_60` | 3 | 约 15 s | 约 3001 | 3 |
| `motor_normal_80` | 3 | 约 15 s | 约 3001 | 3 |
| 合计 | 9 | — | — | 9 |

已存在正式记录 `dataset/raw/motor_normal_60_20260819_204215.csv` 计入 60% 组第 1 条；本轮 40%、60% 和 80% 三档均已完成 3 次正式采集。

## 采集流程

1. 设置指定 PWM。
2. 启动电机。
3. 等待 2–3 秒进入稳定状态。
4. 运行 `serial_logger.py` 并输入对应 label。
5. 自动采集约 15 秒。
6. 检查样本数、时长、5 ms 间隔、200 Hz、无 I²C 错误和数据集可用性。
7. 保存 raw CSV，不修改原始数据。
8. 使用 `plot_accel.py` 生成 PNG 和 stats TXT。
9. 使用 `window_dataset.py` 以统一 label `normal` 完成窗口化。

## 文件约定

原始文件：

```text
dataset/raw/motor_normal_40_YYYYMMDD_HHMMSS.csv
dataset/raw/motor_normal_60_YYYYMMDD_HHMMSS.csv
dataset/raw/motor_normal_80_YYYYMMDD_HHMMSS.csv
```

分析输出：

```text
dataset/plots/<same_basename>.png
dataset/reports/<same_basename>_stats.txt
```

窗口化输出：

```text
dataset/processed/<same_basename>_windows.csv
dataset/processed/<same_basename>_windows_meta.txt
```

所有窗口的模型标签统一为 `normal`；速度标签仅表示采集工况，不是模型类别。

## 运行记录

| run | speed_percent | raw_csv | sample_count | duration_s | estimated_hz | plot | stats_report | processed_windows | result |
|---|---:|---|---:|---:|---:|---|---|---:|---|
| 1 | 40 | `motor_normal_40_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 2 | 40 | `motor_normal_40_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 3 | 40 | `motor_normal_40_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 4 | 60 | `motor_normal_60_20260819_204215.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 5 | 60 | `motor_normal_60_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 6 | 60 | `motor_normal_60_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 7 | 80 | `motor_normal_80_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 8 | 80 | `motor_normal_80_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |
| 9 | 80 | `motor_normal_80_*.csv` | 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | 通过 |

## Acceptance Criteria

- [x] 40% 正常运行采集 3 次
- [x] 60% 正常运行总计 3 次
- [x] 80% 正常运行采集 3 次
- [x] 每次约 15 s
- [x] 每次约 3001 samples
- [x] 每次约 200 Hz
- [x] 无 timestamp continuity error
- [x] 无 ADXL345 read error
- [x] 每次保存 raw CSV
- [x] 每次生成 PNG
- [x] 每次生成 stats TXT
- [x] 每次完成 `window_dataset.py` 处理
- [x] 所有 normal window label 均为 `normal`
- [x] 原始 CSV 未修改
- [x] 至少约 135 normal windows

## 预期窗口数量

每条 3001 samples 的正式 CSV 经 200 samples、无重叠窗口化后得到 15 个完整窗口并丢弃 1 个剩余 sample。9 条记录共得到约 135 个 `normal` windows。

## 实验结论

不同转速（40%、60% 和 80%）之间存在明显振动差异，但三档均属于 `normal` 类。速度百分比作为采集工况标签，不作为模型类别标签；所有窗口统一使用 `normal`。

## Out of Scope

- `rotor_unbalance`
- `mechanical_looseness`
- `stall`
- `overload`
- FFT
- filtering
- feature extraction
- train/validation/test split
- model training
- TensorFlow、TFLite 或 INT8 deployment

## 依赖与风险

- 依赖 ISSUE-0027 的采集稳定性和抗干扰配置。
- 传感器位置、朝向、固定方式和电源条件必须保持一致。
- 速度工况变化不得与传感器重新安装或接线变化同时发生。

## 提交

Pending Git commit
