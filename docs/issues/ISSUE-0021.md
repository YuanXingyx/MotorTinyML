# ISSUE-0021 — STM32F103 开发环境搭建与验证

## 元数据

| 字段 | 内容 |
|---|---|
| Issue ID | ISSUE-0021 |
| 类型 | Hardware Bring-up / Development Infrastructure |
| 状态 | 已完成（Completed） |
| Epic | EPIC-02 — STM32F103 Bring-up |
| Sprint | Sprint 1 |
| 负责人 | Project Engineer |
| 完成日期 | 2026-08-08 |

## 目标

建立 STM32F103C8T6 基础开发环境，创建可构建的 STM32F103 工程，并完成第一次硬件验证。

## 范围

- STM32CubeIDE 工程结构
- STM32F103C8T6 MCU 配置
- STM32F103C8T6 Blue Pill 开发板
- ST-Link V2 下载和调试
- PC13 LED Blink 验证
- 开发环境记录

## 交付物

- `firmware/stm32f103/`
- STM32CubeIDE 工程 `MotorTinyML_F103`
- STM32F103C8T6 配置文件
- 基础 LED 驱动和 Blink 验证
- 固件工程 README

## 硬件与环境

| 项目 | 内容 |
|---|---|
| MCU | STM32F103C8T6 |
| 开发板 | STM32F103C8T6 Blue Pill |
| IDE | STM32CubeIDE 2.2.0 |
| 配置工具 | STM32CubeMX |
| 下载器 | ST-Link V2 |
| LED 引脚 | PC13 |
| 固件包 | STM32Cube FW_F1 V1.8.7 |

## 验收结果

| 验收项 | 结果 | 证据或说明 |
|---|---|---|
| STM32CubeIDE 环境可用 | 通过 | 工程已创建并可打开 |
| STM32F103 工程创建成功 | 通过 | `MotorTinyML_F103` 工程文件存在 |
| Clean Project | 通过 | 用户确认成功 |
| Build Project | 通过 | 已生成 ELF、MAP 和 LIST 构建产物 |
| ST-Link 下载 | 通过 | 用户确认成功 |
| MCU 复位运行 | 通过 | 用户确认复位后正常运行 |
| PC13 LED Blink | 通过 | 用户确认约 500 ms 周期闪烁 |

## 验证说明

- `main.c` 调用 `LED_Init()`。
- 主循环调用 `LED_Toggle()` 和 `HAL_Delay(500)`。
- LED 驱动使用 GPIOC Pin 13。
- 工程配置目标为 STM32F103C8Tx。
- 硬件下载和 LED 观察结果由 Project Engineer 在实际开发板上确认。

## 受保护区域

本 Issue 未修改：

- `python/`
- `dataset/`
- `models/`
- `hardware/`

本 Issue 未创建 Python、AI、数据集或模型内容。

## 文档更新状态

当前仅创建本 Issue 记录。Dashboard、DevelopmentLog、TODO、EPIC-02 和 Milestones 的同步将在 Documentation Update Plan 获得批准后执行。

## 风险

- 当前工程包含 Debug 构建产物，后续需确认其版本控制策略。
- EPIC-02 和 Milestone 1 是否关闭尚未单独批准。
- 传感器和后续数据采集方案仍待 Tech Lead 确认。

## Commit

Pending Git commit

## 完成总结

STM32F103C8T6 开发环境已建立，工程已成功构建并下载到 MCU，PC13 LED Blink 硬件验证通过。ISSUE-0021 已完成。
