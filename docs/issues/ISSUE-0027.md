# ISSUE-0027 — Dataset Baseline Collection and Quality Validation

## 元数据

- 议题 ID：ISSUE-0027
- 类型：Dataset Acquisition / Data Quality Validation
- 状态：DONE
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-13
- 完成日期：2026-08-19

## 目标

完成两组可追溯的 ADXL345 正式基线数据采集，并验证数据完整性、采样稳定性和静止/电机运行状态之间的差异。

## 正式基线数据

### sensor_idle

- 采集时长：15.000 s
- 样本数量：3001
- 平均采样频率：200.000 Hz
- 平均时间戳间隔：5.000 ms

| 轴 | mean | min | max | peak_to_peak | std |
|---|---:|---:|---:|---:|---:|
| X | -5.502 | -10 | -1 | 9 | 1.241 |
| Y | -4.325 | -10 | 0 | 10 | 1.482 |
| Z | 256.008 | 252 | 260 | 8 | 1.107 |

### motor_normal_60

- 正式 CSV：`dataset/raw/motor_normal_60_20260819_204215.csv`
- 采集时长：15.000 s
- 样本数量：3001
- 平均采样频率：200.000 Hz
- 平均时间戳间隔：5.000 ms
- 数据集状态：可作为正式数据集使用

| 轴 | mean | min | max | peak_to_peak | std |
|---|---:|---:|---:|---:|---:|
| X | -35.873 | -282 | 176 | 458 | 134.460 |
| Y | -6.086 | -146 | 166 | 312 | 83.422 |
| Z | 258.169 | 66 | 405 | 339 | 110.859 |

## Acceptance Criteria

- [x] `sensor_idle` 正式采集完成，时长 15.000 s。
- [x] `motor_normal_60` 正式采集完成，时长 15.000 s。
- [x] 两组数据各有 3001 samples，与约 15 秒、约 200 Hz 的预期基本一致。
- [x] 两组 CSV 使用 `timestamp_ms,x,y,z` 表头并保存到 `dataset/raw/`。
- [x] 时间戳严格单调递增。
- [x] 不存在重复时间戳。
- [x] CSV 无缺失字段或无法解析的数据行。
- [x] 已统计平均采样间隔并检查潜在缺样。
- [x] 两组实际平均采样频率均为 200.000 Hz。
- [x] 两组数据均生成 X/Y/Z 时域图。
- [x] 两组数据均生成基础统计结果 TXT 报告。
- [x] 正式 `motor_normal_60` 采集过程中无 `ADXL345 read error`。
- [x] 传感器安装位置、方向和采集配置保持一致。
- [x] 原始 CSV 未被修改或覆盖。

## 实验结论

`sensor_idle` 的 X/Y/Z 标准差为 1.241 / 1.482 / 1.107，peak-to-peak 为 9 / 10 / 8；`motor_normal_60` 的标准差为 134.460 / 83.422 / 110.859，peak-to-peak 为 458 / 312 / 339。

电机正常运行产生的振动相对于静止传感器噪声存在明显差异。当前 ADXL345 + STM32F103 + 200 Hz + UART + Python CSV pipeline 可以稳定捕获电机运行振动，并区分静止基线和正常运转基线。

`sensor_idle` 仅作为静止基线，不等同于最终模型类别中的 Normal；最终 Normal 类应以电机正常运行数据为主。

## 数据采集稳定性证据

实验过程中曾出现 `ADXL345 read error`。在电机端子并联 100 nF 陶瓷电容，并在 TB6612 VM-GND 之间增加 100 uF 电解电容和 100 nF 陶瓷电容后，电机运行时的 I²C 读取错误消失，随后 `motor_normal_60` 正式采集成功。

## Evidence / Files

- `dataset/raw/*.csv`
- `dataset/plots/*.png`
- `dataset/reports/*_stats.txt`
- `python/serial_logger.py`
- `python/plot_accel.py`
- Python `.venv` 作为本地开发环境，不作为项目数据成果提交。

## Out of Scope

- 不修改 STM32 固件。
- 不改变 PWM 配置。
- 不做 FFT、滤波、机器学习或复杂特征工程。

## Next Step

`ISSUE-0028 — Dataset Quality Report and Baseline Comparison`

## 提交

Pending Git commit

## 风险

- 当前基线数据已通过本次质量验证，但后续仍需在更多运行批次中确认可重复性。
- 原始数据尚未进行标定、单位换算或模型特征工程。
