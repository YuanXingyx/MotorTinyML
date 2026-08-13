# ISSUE-0026 — ADXL345 Continuous Sampling and UART Data Streaming

## 元数据

- 议题 ID：ISSUE-0026
- 类型：Data Acquisition / PC Collection Infrastructure
- 状态：DONE
- Epic：EPIC-03 Sensor Driver Development
- Sprint：Sprint 1
- 负责人：项目工程师
- 完成日期：2026-08-13

## 目标

建立 ADXL345 连续采样、STM32 UART 数据流和 PC 端 CSV 数据采集与可视化基础。

## 已完成实现

- ADXL345 通过 I²C 配置为约 200 Hz 采样。
- STM32 以约 5 ms 周期稳定读取 XYZ 原始数据。
- UART 按 `timestamp,x,y,z` 格式输出数据。
- 创建并验证 `python/serial_logger.py`。
- 有效数据保存到 `dataset/raw/` CSV 文件。
- 创建并验证 `python/plot_accel.py`。
- `plot_accel.py` 支持 XYZ 时域绘图和基础统计分析。
- Python `.venv` 环境已建立。
- STM32 系统时钟已修正为 72 MHz。
- TIM1 PWM 频率已验证为 20 kHz。
- 电机 60% PWM 运行正常，作为采集工况支撑验证。

## 验收结果

- [x] ADXL345 I²C 200 Hz 配置完成
- [x] STM32 约 5 ms 采样周期基本稳定
- [x] UART 输出 `timestamp,x,y,z`
- [x] Python 串口采集脚本运行正常
- [x] CSV 数据成功保存
- [x] CSV 表头为 `timestamp_ms,x,y,z`
- [x] X/Y/Z 时域波形绘制完成
- [x] 三轴基础统计输出完成
- [x] 系统时钟 72 MHz 验证完成
- [x] TIM1 PWM 20 kHz 验证完成
- [x] 电机 60% PWM 工况运行正常

## 支撑文件

- `python/serial_logger.py`
- `python/plot_accel.py`
- `dataset/raw/`
- `.venv/`

## 范围限制

- 未实现 FFT。
- 未实现滤波。
- 未实现机器学习或复杂特征工程。
- 未修改原始 CSV 数据。

## 建议后续 Issue

`ISSUE-0027 — Dataset Quality Validation and Sampling Consistency`

建议范围：校验 CSV 完整性、时间戳单调性、实际采样频率、采样抖动、缺失行和重复时间戳；不包含模型训练或固件修改。

## 提交

Pending Git commit

## 风险

- 当前采样频率和周期稳定性为基础验证结果，仍需更长时间数据集确认。
- 当前数据为原始 ADC/传感器量，不包含标定、单位换算或滤波。
