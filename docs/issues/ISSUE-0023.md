# ISSUE-0023 — STM32F103 SPI1 Bring-up

## 元数据

- 议题 ID：ISSUE-0023
- 类型：Hardware Bring-up / Peripheral Infrastructure
- 状态：已完成
- Epic：EPIC-02 STM32F103 Bring-up
- Sprint：Sprint 1
- 负责人：项目工程师
- 完成日期：2026-08-08

## 目标

在现有 STM32F103C8T6 工程中建立 SPI1 主机通信基础，为后续 ADXL345 驱动提供稳定接口。

## 配置

- SPI1：Master，2 Lines Full Duplex，8 Bits
- Mode 3：CPOL High，CPHA 2 Edge
- Prescaler：32
- NSS：Software
- First Bit：MSB First
- CRC：Disabled
- PA5：SPI1_SCK
- PA6：SPI1_MISO
- PA7：SPI1_MOSI
- PA4：`ADXL345_CS` GPIO Output，Idle HIGH

## 验收结果

- [x] CubeMX SPI1 配置有效
- [x] 工程构建成功，错误数为 0
- [x] 固件下载成功
- [x] UART Boot Log 保持正常
- [x] PC13 LED 回归测试通过
- [x] `ADXL345_CS` 空闲状态为 HIGH
- [x] 未实现 ADXL345 寄存器协议
- [x] 未实现 DMA 或中断
- [x] 未启动 ISSUE-0024

## 受保护范围

未修改 `python/`、`dataset/`、`models/` 或 `hardware/`，未引入 AI 功能。

## 文档同步

已按文档分类策略更新 Level 1 文档。Level 2 文档未更新，因为本次未关闭 Sprint、Milestone 或 Epic；Level 3 文档未修改。

## 提交

Pending Git commit

## 风险

- 尚未进行 ADXL345 实际寄存器通信验证。
- SPI 时序和 CS 控制将在后续传感器驱动 Issue 中继续验证。
