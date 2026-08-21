# ISSUE-0030 — Rotor Unbalance Dataset Collection

## 元数据

- 议题 ID：ISSUE-0030
- 类型：Dataset Acquisition / Fault Simulation
- 状态：REVIEW
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-20

## 目标

在保持传感器安装、采样率、电机固定方式、TB6612 接线和抗干扰措施不变的前提下，通过可控的小型偏心质量人为制造转子不平衡，采集 `rotor_unbalance` 类数据。

## 固定实验条件

- STM32F103C8T6
- ADXL345 I²C
- 200 Hz ODR
- 5 ms timestamp interval
- UART 115200
- ADXL345 安装位置和朝向不变
- 电机固定方式不变
- 电源条件尽量一致
- TB6612 接线不变
- 电机端子 100 nF 陶瓷电容保留
- TB6612 VM-GND 100 uF + 100 nF 去耦保留

不得移动传感器来制造数据差异。

## Rotor Unbalance 模拟原则

在旋转部件的非中心位置牢固固定很小的偏心质量，制造周期性不平衡振动。具体质量不预先规定，以能够产生稳定、可重复且不过度剧烈的振动为标准，逐步增加并观察结果。

### 安全要求

- 偏心质量必须牢固固定，不得使用松散物体。
- 不得将大质量物体直接固定到高速转轴。
- 第一次验证从低速开始。
- 启动时人与旋转部件保持安全距离。
- 出现剧烈振动、异响、配重松动或结构位移时立即停机。
- 不得为了增加数据差异无限增大偏心质量。

开始人工实验前，必须确认偏心质量固定方式、旋转部件防护和紧急停机条件。

## 第一轮采集计划

| 速度工况 | 采集次数 | 每次时长 | 每次预期样本 | 目标文件数 |
|---|---:|---:|---:|---:|
| `rotor_unbalance_40` | 3 | 约 15 s | 约 3001 | 3 |
| `rotor_unbalance_60` | 3 | 约 15 s | 约 3001 | 3 |
| 合计 | 6 | — | — | 6 |

第一轮暂不采集 80%，先验证偏心质量模拟的稳定性和安全性。

## 采集流程

1. 检查偏心质量固定牢靠。
2. 设置目标 PWM。
3. 启动电机并观察 2–3 秒。
4. 确认无剧烈振动、无配重松动、无 `ADXL345 read error`。
5. 运行 `serial_logger.py`，输入对应 label。
6. 自动采集约 15 秒。
7. 检查约 3001 samples、15.000 s、5 ms interval 和约 200 Hz。
8. 确认数据集状态可正式使用并保存 raw CSV。
9. 使用 `plot_accel.py` 生成 PNG 和 stats TXT。
10. 使用 `window_dataset.py --label rotor_unbalance` 完成窗口化。

## 文件约定

```text
dataset/raw/rotor_unbalance_40_YYYYMMDD_HHMMSS.csv
dataset/raw/rotor_unbalance_60_YYYYMMDD_HHMMSS.csv
dataset/plots/<same_basename>.png
dataset/reports/<same_basename>_stats.txt
dataset/processed/<same_basename>_windows.csv
dataset/processed/<same_basename>_windows_meta.txt
```

窗口模型 label 必须统一为 `rotor_unbalance`；40% 和 60% 仅表示速度工况，不是不同模型类别。

## 运行记录

| run | speed_percent | raw_csv | sample_count | duration_s | estimated_hz | plot | stats_report | processed_windows | result |
|---|---:|---|---:|---:|---:|---|---|---:|---|
| 1 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 2 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 3 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 4 | 60 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 5 | 60 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 6 | 60 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |

### 异常记录

一次 60% 实验出现 Y 轴反复触及 -1024/+1023 的量程饱和。该 CSV 已由用户删除，不计入正式数据集；其余三条有效 60% 数据均未出现明显饱和。

## Acceptance Criteria

- [x] Rotor unbalance 模拟方案完成并安全验证
- [x] 40% 采集 3 条
- [x] 60% 采集 3 条
- [x] 每条约 15 s
- [x] 每条约 3001 samples
- [x] 每条约 200 Hz
- [x] 无 timestamp continuity error
- [x] 无 ADXL345 read error
- [x] raw CSV 保存成功
- [x] PNG 生成成功
- [x] stats TXT 生成成功
- [x] `window_dataset.py` 处理完成
- [x] 所有 window label = `rotor_unbalance`
- [x] raw CSV 未修改
- [x] 至少约 90 个 `rotor_unbalance` windows
- [x] 与对应 `motor_normal_40` / `motor_normal_60` 完成 std、peak-to-peak 和时域波形基础对比

每条约 3001 samples 的 CSV 预期生成 15 个完整窗口并丢弃 1 个剩余 sample；6 条完成后预计约 90 个 `rotor_unbalance` windows。

## 实际结果与统计

- `rotor_unbalance_40`：3 条正式 CSV，每条约 3001 samples、15.000 s、约 200 Hz、15 个完整窗口。
- `rotor_unbalance_60`：3 条有效正式 CSV，每条约 3001 samples、15.000 s、约 200 Hz、15 个完整窗口。
- 总计 6 条正式 CSV、约 90 个窗口，统一窗口 label 为 `rotor_unbalance`。
- 所有正式数据均生成 raw CSV、PNG、stats TXT、processed windows CSV 和 metadata TXT；raw CSV 未修改。
- 最终有效数据无 `ADXL345 read error`。

40% 三次采集的标准差（X/Y/Z）分别为：

| Run | X | Y | Z |
|---|---:|---:|---:|
| 1 | 173.684 | 586.630 | 61.665 |
| 2 | 156.311 | 539.627 | 67.617 |
| 3 | 150.310 | 538.145 | 65.895 |

60% 三次有效采集的标准差（X/Y/Z）分别为：

| Run | X | Y | Z |
|---|---:|---:|---:|
| 1 | 60.381 | 390.056 | 25.227 |
| 2 | 69.034 | 331.586 | 26.421 |
| 3 | 75.070 | 392.515 | 30.351 |

与对应 `motor_normal_40` / `motor_normal_60` 的基础 std、peak-to-peak 和时域波形对比表明，偏心工况产生了可观察的振动差异，且 Y 轴是主要振动方向。上述差异用于区分工况，不改变 `rotor_unbalance` 的统一类别标签。

## Out of Scope

- `mechanical_looseness`
- `overload`
- `stall`
- FFT
- filtering
- feature engineering
- train/validation/test split
- model training
- TensorFlow、TFLite 或 INT8 deployment

## 依赖与风险

- 依赖 ISSUE-0027 和 ISSUE-0029 已验证的采集链路及抗干扰措施。
- 偏心质量脱落、结构位移和高速离心力是主要安全风险。
- 任何异常振动、异响或硬件松动都必须立即停止实验。

## 提交

Pending Git commit
