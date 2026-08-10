# ISSUE-0024 — ADXL345 Driver Bring-up and Device Identification

## 元数据

- 议题 ID：ISSUE-0024
- 类型：Sensor Driver Development
- 状态：BLOCKED / Waiting for Hardware
- Epic：EPIC-03 Sensor Driver Development
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-10

## 目标

实现最小 ADXL345 SPI 驱动并读取 Device ID 寄存器 `0x00`，预期值为 `0xE5`。

## 当前状态

ADXL345 器件尚未到货，无法进行硬件连接、SPI 通信和 Device ID 验证。因此本 Issue 保持阻塞状态，未标记为完成。

## 待执行范围

- 创建模块化 ADXL345 驱动
- 实现最小 SPI 寄存器读写
- 读取寄存器 `0x00`
- 通过 UART 输出 Device ID
- 保持 LED 和 UART 回归功能

## 受保护范围

在器件到货前不启动连续采样、DMA、中断、FIFO、滤波或 TinyML 功能。

## 提交

Pending Git commit

## 风险

- 器件到货时间影响 ISSUE-0024 开始时间。
- 实际模块供电、电平和接线需要到货后确认。
