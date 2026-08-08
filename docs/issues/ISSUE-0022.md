# ISSUE-0022 — STM32F103 UART 调试控制台

## 元数据

- 议题 ID：ISSUE-0022
- 类型：Hardware Bring-up / Debug Infrastructure
- 状态：已完成
- Epic：EPIC-02 STM32F103 Bring-up
- Sprint：Sprint 1
- 负责人：项目工程师
- 完成日期：2026-08-08

## 目标

建立 STM32F103C8T6 的 USART1 调试输出通道，为后续外设和 TinyML 调试提供稳定日志接口。

## 配置

- USART1
- PA9：TX
- PA10：RX
- 波特率：115200
- 数据位：8
- 校验：None
- 停止位：1
- 流控：None

## 验收结果

- [x] STM32F103C8T6 启动成功
- [x] USART1 115200 8-N-1 通信正常
- [x] PA9 UART TX 输出正常
- [x] USB-TTL 通信正常
- [x] 复位后输出 `MotorTinyML STM32F103 boot`
- [x] 原有 PC13 LED Blink 功能保持正常
- [x] 未启动 SPI 或 ADXL345 实现

## 受保护范围

本 Issue 未修改 `python/`、`dataset/`、`models/` 或 `hardware/`，也未引入 AI 功能。

## 文档同步

已按文档分类策略评估 Level 1 文档；Level 2 和 Level 3 文档未因本普通 Issue 更新。EPIC-02 与 Milestone 1 的关闭状态仍待 Tech Lead 决策。

## 提交

Pending Git commit

## 风险

- USB-TTL 电平、接线和终端参数需保持一致。
- 尚未建立自动化串口回归测试。
