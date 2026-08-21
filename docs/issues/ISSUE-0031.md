# ISSUE-0031 — Mechanical Looseness Dataset Collection

## 元数据

- 议题 ID：ISSUE-0031
- 类型：Dataset Acquisition / Fault Simulation
- 状态：REVIEW
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-20

## 目标

保持传感器、电机、电源、采样配置等条件与 normal 数据一致，仅通过改变电机安装结构的机械紧固程度，制造稳定、可重复的 `mechanical_looseness` 工况。

## 固定实验条件

- STM32F103C8T6
- ADXL345 I²C
- 200 Hz ODR
- 5 ms timestamp interval
- UART 115200
- ADXL345 位置和朝向不变
- 电机与风扇叶轮保持原结构
- 完全移除 rotor_unbalance 配重
- 电机端子 100 nF 陶瓷电容保留
- TB6612 VM-GND 100 uF + 100 nF 去耦保留
- 电源条件尽量一致

进入 mechanical looseness 采集前，必须完全移除之前 rotor_unbalance 使用的塑料绑带配重，恢复正常平衡状态。

## Mechanical Looseness 模拟原则

故障只作用于电机与安装底座/支架之间的机械固定。保持大部分固定点正常，仅让一个固定点轻微变松；电机仍必须固定在原位置，不得脱落、自由跳动或使叶轮碰撞其他结构。

不得松动：

- ADXL345 及其安装点
- I²C 线
- TB6612
- 电源连接

目标是产生可重复的轻微机械间隙和振动变化，而不是剧烈位移或撞击。

### 安全验证

每次调整固定点前先断电，并确认：

1. 电机不会脱落，叶轮不会碰撞。
2. 以 40% PWM 短跑 2–3 秒，再运行 5–10 秒。
3. 无明显位移、结构脱落或严重撞击。
4. ADXL345 数据持续输出且无 `ADXL345 read error`。

出现异常振动、异响、松动扩大或结构位移时，立即断电停机。正式采集前需要人工确认机械松动方式、旋转部件防护和紧急停机条件。

## 第一轮采集计划

| 速度工况 | 采集次数 | 每次时长 | 每次预期样本 | 目标文件数 |
|---|---:|---:|---:|---:|
| `mechanical_looseness_40` | 3 | 约 15 s | 约 3001 | 3 |
| `mechanical_looseness_60` | 3 | 约 15 s | 约 3001 | 3 |
| 合计 | 6 | — | — | 6 |

第一轮暂不采集 80%。预计每条生成 15 个完整窗口，合计约 90 个 `mechanical_looseness` windows。

## 采集流程

1. 完全移除 rotor_unbalance 配重并检查机械固定。
2. 设置目标 PWM，稳定运行 2–3 秒。
3. 运行 `python python/serial_logger.py`，输入对应 raw label。
4. 自动采集约 15 秒，检查约 3001 samples、5 ms interval 和约 200 Hz。
5. 确认无 timestamp continuity error 和 `ADXL345 read error`，保存 raw CSV。
6. 使用 `plot_accel.py` 生成 PNG 和 stats TXT。
7. 使用 `window_dataset.py --label mechanical_looseness` 完成窗口化。

## 文件命名

```text
dataset/raw/mechanical_looseness_40_YYYYMMDD_HHMMSS.csv
dataset/raw/mechanical_looseness_60_YYYYMMDD_HHMMSS.csv
dataset/plots/<same_basename>.png
dataset/reports/<same_basename>_stats.txt
dataset/processed/<same_basename>_windows.csv
dataset/processed/<same_basename>_windows_meta.txt
```

40% 和 60% 仅表示工况，窗口模型 label 统一为 `mechanical_looseness`。

## 运行记录

| run | speed_percent | raw_csv | sample_count | duration_s | estimated_hz | plot | stats_report | processed_windows | result |
|---|---:|---|---:|---:|---:|---|---|---:|---|
| 1 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 2 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 3 | 40 | 已采集 | 约 3001 | 15.000 | 约 200 | 已生成 | 已生成 | 15 | PASS |
| 4 | 60 | `mechanical_looseness_60_20260820_170815` | 3001 | 15.000 | 200 | 已生成 | 已生成 | 15 | PASS |
| 5 | 60 | `mechanical_looseness_60_20260820_171323` | 3001 | 15.000 | 200 | 已生成 | 已生成 | 15 | PASS |
| 6 | 60 | `mechanical_looseness_60_20260820_172224` | 3001 | 15.000 | 200 | 已生成 | 已生成 | 15 | PASS |

### 供电稳定性与排除记录

`mechanical_looseness_60_20260820_171626` 使用充电宝供电，实验前后观察到供电接触或电压状态可能影响电机振动和 I²C 稳定性。其 std 为 X=15.550、Y=96.937、Z=20.285，因此标记为 `excluded / unstable power condition`，不计入正式数据集，也不作为训练数据。

随后改用电脑 USB 稳定供电重新采集 `mechanical_looseness_60_20260820_172224`，其振动水平恢复到与其他有效 60% 记录接近的范围。后续正式采集统一使用稳定电脑 USB 供电，禁止混用充电宝或触碰 USB/供电连接。

## 基础对比

分别比较：

- `mechanical_looseness_40` 与 `motor_normal_40`
- `mechanical_looseness_60` 与 `motor_normal_60`

至少比较 X/Y/Z 的 std、peak-to-peak 和时域波形；可观察与 rotor_unbalance 的轴向振动模式差异，但不进行 FFT 或模型判断。

## Acceptance Criteria

- [x] rotor_unbalance 配重完全移除
- [x] mechanical looseness 模拟方式安全确认
- [x] ADXL345 本身保持牢固
- [x] 40% 正式采集 3 条
- [x] 60% 正式采集 3 条
- [x] 每条约 15 s
- [x] 每条约 3001 samples
- [x] 每条约 200 Hz
- [x] 无 timestamp continuity error
- [x] 无 ADXL345 read error
- [x] CSV、PNG、stats TXT 全部生成
- [x] `window_dataset.py` 处理完成
- [x] window label = `mechanical_looseness`
- [x] raw CSV 未修改
- [x] 至少约 90 个 `mechanical_looseness` windows
- [x] 与 normal 完成基础统计对比

未完成全部实际采集前，不得标记为 DONE。

## 实际结果与统计

- `mechanical_looseness_40`：3 条正式有效 CSV；每条 3001 samples、15.000 s、200 Hz、15 个完整窗口。
- `mechanical_looseness_60`：3 条正式有效 CSV；每条 3001 samples、15.000 s、200 Hz、15 个完整窗口；正式采集期间无 `ADXL345 read error`。
- 总计 6 条正式 CSV、约 90 个窗口，processed label 统一为 `mechanical_looseness`。

40% 三次标准差（X/Y/Z）：

| Run | X | Y | Z |
|---|---:|---:|---:|
| 1 | 13.689 | 72.691 | 11.514 |
| 2 | 11.576 | 77.351 | 11.056 |
| 3 | 13.731 | 73.576 | 10.290 |

60% 三次正式有效标准差（X/Y/Z）：

| Run | X | Y | Z |
|---|---:|---:|---:|
| 1 | 99.268 | 276.609 | 62.841 |
| 2 | 52.914 | 211.233 | 54.408 |
| 3 | 100.661 | 261.220 | 61.212 |

与对应 `motor_normal_40` / `motor_normal_60` 的基础 std、peak-to-peak 和时域波形对比显示，机械松动工况产生了可观察的振动变化；60% 工况的整体振动水平明显高于 40%，并可与 rotor_unbalance 的振动模式进行后续比较。以上结论仅用于数据质量和工况差异记录，不涉及模型训练或分类判断。

## Out of Scope

- `rotor_unbalance`
- `overload`
- `stall`
- FFT
- filtering
- feature engineering
- neural network
- TensorFlow、TFLite 或 INT8 deployment

## 提交

Pending Git commit
