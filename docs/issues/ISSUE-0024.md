# ISSUE-0024 — ADXL345 Driver Bring-up and Device Identification

## 元数据

- 议题 ID：ISSUE-0024
- 类型：Sensor Driver Development
- 状态：DONE
- Epic：EPIC-03 Sensor Driver Development
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-10
- 完成日期：2026-08-13

## 目标

完成 ADXL345 硬件 Bring-up，建立 I²C1 通信并读取 Device ID 与 XYZ 三轴原始数据。

## 当前状态

ADXL345 器件已到货并完成硬件验证。最终采用 I²C1：PB6 为 SCL，PB7 为 SDA，器件地址为 `0x53`。

SPI 调试经过已保留：STM32 SPI loopback 验证正常，但该 ADXL345 模块的 SPI 通信未建立，因此实现切换为 I²C1。

## 实现与验收结果

- [x] ADXL345 器件到货并完成硬件连接
- [x] 配置 I²C1：PB6=SCL、PB7=SDA
- [x] 使用器件地址 `0x53`
- [x] 成功读取 `DEVID=0xE5`
- [x] 成功读取 XYZ 三轴原始数据
- [x] STM32 SPI loopback 验证正常
- [x] 确认 ADXL345 模块 SPI 通信未建立
- [x] 完成 SPI 到 I²C1 的接口切换

## 受保护范围

本 Issue 未引入 DMA、中断、FIFO、滤波或 TinyML 功能。

## 提交

Pending Git commit

## 风险

- 当前 XYZ 数据为原始数据，尚未进行标定、滤波或单位换算。
- 后续采样稳定性和数据质量仍需持续验证。
