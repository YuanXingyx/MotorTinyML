# ISSUE-0032 — Motor Overload Dataset Collection

## 元数据

- 议题 ID：ISSUE-0032
- 类型：Dataset Acquisition / Fault Simulation
- 状态：TODO
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-20

## 目标

建立可控、可重复的电机过载工况，在电机仍保持旋转的前提下增加机械负载，采集 `overload` 类振动数据。

## 固定实验条件

- STM32F103C8T6
- ADXL345 I²C
- 200 Hz ODR
- 5 ms timestamp interval
- UART 115200
- ADXL345 安装位置和朝向不变
- 电机固定方式恢复正常紧固
- 取消 mechanical looseness 状态
- 不使用 rotor unbalance 配重
- 电机端子 100 nF 陶瓷电容保留
- TB6612 VM-GND 100 uF + 100 nF 去耦保留
- 正式采集统一使用稳定电脑 USB 供电
- 采集期间不触碰供电连接

## Overload 定义

本 Issue 中，overload 指电机仍持续旋转，但机械负载明显高于 normal，可能表现为转速下降、电流增加和振动模式变化。

不允许完全堵转、长时间停轴、用手直接捏住裸轴，或在电机/TB6612 明显发热后继续测试。

## Overload 模拟原则

采用可控机械负载。若现有结构允许，可连接轻微阻尼结构，通过可重复的摩擦或阻力增加负载。电机必须继续旋转，负载不得突然卡死，负载强度应保持一致；具体硬件方式需用户根据现有结构人工确认。

## 第一轮采集计划

| 速度工况 | 采集次数 | 每次时长 | 每次预期样本 | 目标文件数 |
|---|---:|---:|---:|---:|
| `motor_overload_40` | 3 | 约 15 s | 约 3000 | 3 |
| `motor_overload_60` | 3 | 约 15 s | 约 3000 | 3 |
| 合计 | 6 | — | — | 6 |

第一轮暂不采集 80%。每条预计生成约 15 个完整窗口，总计约 90 个 `overload` windows。

## 安全要求

正式采集前，每次先恢复电机正常固定，施加轻微 overload，以 40% PWM 运行 2–3 秒，再观察 5–10 秒。确认电机持续旋转、未卡死、无异常发热且无 `ADXL345 read error` 后才开始正式采集。

出现电机停止、转速接近 0、TB6612 或电机明显发热、USB 供电异常或持续 `ADXL345 read error` 时，立即停止实验并减小负载或断电检查。

开始人工实验前，必须确认可控机械负载的具体方式、负载不会突然卡死、旋转部件防护和紧急停机条件。

## 正式采集流程

1. 恢复 normal 机械固定，移除所有 rotor_unbalance 配重并取消 mechanical looseness。
2. 施加目标机械负载，确认短测安全通过。
3. 运行 `python python/serial_logger.py`，输入 `motor_overload_40` 或 `motor_overload_60`。
4. 自动采集约 15 秒，检查约 3000 samples、5 ms interval 和约 200 Hz。
5. 使用 `plot_accel.py` 生成 PNG 和 stats TXT。
6. 使用 `python python/window_dataset.py dataset/raw/<file>.csv --label overload` 完成窗口化。

40% 和 60% 仅表示速度工况，窗口模型 label 统一为 `overload`。

## 输出文件

每条正式记录应包含：

- `dataset/raw/` 下的 raw CSV
- `dataset/plots/` 下的 PNG
- `dataset/reports/` 下的 stats TXT
- `dataset/processed/` 下的 windows CSV 和 metadata TXT

## 运行记录

| run | speed_percent | raw_csv | sample_count | duration_s | estimated_hz | plot | stats_report | processed_windows | result |
|---|---:|---|---:|---:|---:|---|---|---:|---|
| 1 | 40 | 待采集 | — | — | — | — | — | — | TODO |
| 2 | 40 | 待采集 | — | — | — | — | — | — | TODO |
| 3 | 40 | 待采集 | — | — | — | — | — | — | TODO |
| 4 | 60 | 待采集 | — | — | — | — | — | — | TODO |
| 5 | 60 | 待采集 | — | — | — | — | — | — | TODO |
| 6 | 60 | 待采集 | — | — | — | — | — | — | TODO |

## Acceptance Criteria

- [ ] 电机固定恢复 normal 状态
- [ ] mechanical looseness 状态取消
- [ ] overload 模拟方案安全确认
- [ ] overload 状态下电机仍持续旋转
- [ ] 40% 正式采集 3 条
- [ ] 60% 正式采集 3 条
- [ ] 每条约 15 s
- [ ] 每条约 200 Hz
- [ ] 无 timestamp continuity error
- [ ] 无持续 `ADXL345 read error`
- [ ] raw CSV、PNG、stats TXT 全部生成
- [ ] `window_dataset.py` 处理完成
- [ ] window label = `overload`
- [ ] raw CSV 未修改
- [ ] 至少约 90 个 `overload` windows
- [ ] 与 normal 工况完成基础统计对比

未完成实际采集前不得标记为 DONE。

## Out of Scope

- `stall`
- `rotor_unbalance`
- `mechanical_looseness`
- FFT
- filtering
- feature engineering
- model training
- TensorFlow、TFLite 或 INT8 deployment

## 提交

Pending Git commit
