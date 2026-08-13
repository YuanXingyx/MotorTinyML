# ISSUE-0027 — Dataset Baseline Collection and Quality Validation

## 元数据

- 议题 ID：ISSUE-0027
- 类型：Dataset Acquisition / Data Quality Validation
- 状态：TODO
- Epic：EPIC-04 — Data Acquisition
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-13

## 目标

采集并验证两组可追溯的 ADXL345 基线数据，为后续数据处理和模型训练提供可靠原始数据。

## 基线数据组

- `sensor_idle`
- `motor_normal_60`

每组目标采集约 15 秒。在约 200 Hz 条件下，理论样本量约为 3000 个；实际样本数量以采集时长、串口传输和有效数据行为准，不要求精确等于 3000 个。

## 范围

- 保持 ADXL345 安装位置、方向、供电和接线一致。
- 使用当前约 200 Hz、约 5 ms 采样配置。
- 使用 `python/serial_logger.py` 采集两组 CSV。
- 使用规范 label 生成数据文件名。
- 使用 `plot_accel.py` 生成两组数据的 X/Y/Z 时域图和基础统计结果。
- 检查实际采样频率、时间戳连续性、样本数量和 CSV 数据完整性。
- 保存数据和验证结果，确保采集条件与结果可追溯。

## Acceptance Criteria

- [ ] `sensor_idle` 数据采集完成，时长约 15 秒。
- [ ] `motor_normal_60` 数据采集完成，时长约 15 秒。
- [ ] 两组 CSV 均使用 `timestamp_ms,x,y,z` 表头并保存到 `dataset/raw/`。
- [ ] 时间戳严格单调递增。
- [ ] 不存在重复时间戳。
- [ ] CSV 无缺失字段或无法解析的数据行。
- [ ] 已统计采样间隔并检查潜在缺样。
- [ ] 样本数量与约 15 秒、约 200 Hz 的预期基本一致，不要求精确 3000 个。
- [ ] 实际平均采样频率接近 200 Hz。
- [ ] 两组数据均生成时域图和基础统计结果。
- [ ] 原始 CSV 不被修改或覆盖。
- [ ] 采集条件、文件名、采集时间和硬件状态已记录。

## Out of Scope

- 不修改 STM32 固件。
- 不改变 PWM 配置。
- 不做 FFT。
- 不做滤波。
- 不做机器学习。
- 不做复杂特征工程。
- 不开发新的 GUI、异步采集框架或传感器驱动。

## 依赖

- ISSUE-0026 已完成的 ADXL345 采样、UART 数据流、Python 串口采集和绘图链路。
- 稳定的 STM32F103、ADXL345、USB-TTL 和电机硬件连接。

## 风险

- 串口传输或主机调度可能造成潜在缺样，需要通过时间戳和采样间隔检查识别。
- 两组数据的安装方向、机械振动和电机工况必须保持一致，否则会影响基线可比性。

## 提交

Pending Git commit
