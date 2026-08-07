
# ISSUE-0021 — STM32F103 First Hardware Bring-up
记录：
工程创建
硬件型号
工具版本
LED测试结果
## Metadata

| Field | Value |
|---|---|
| Issue ID | ISSUE-0021 |
| Epic | EPIC-02 — STM32F103 Bring-up |
| Status | Completed |
| Priority | High |
| Owner | Project Engineer |
| Completed Date | 2026-08-07 |

---

# Goal

完成 MotorTinyML 项目的第一次真实硬件 Bring-up。

目标：

- 建立 STM32F103C8T6 固件工程。
- 验证 STM32CubeMX 配置流程。
- 验证 STM32CubeIDE 编译流程。
- 验证 ST-Link 下载流程。
- 完成板载 LED Blink 测试。

---

# Hardware Environment

## MCU

| Item | Value |
|---|---|
| MCU | STM32F103C8T6 |
| Board | STM32F103C8T6 Blue Pill |
| Debugger | ST-Link V2 |
| Communication | SWD |

---

# Software Environment

| Tool | Version |
|---|---|
| STM32CubeIDE | 2.2.0 |
| STM32CubeMX | Integrated / Generated Project |
| STM32CubeProgrammer | Installed |
| ST-Link Driver | Installed |

---

# Implementation

## Project Creation

Completed:

- [x] Created STM32F103C8Tx project.
- [x] Generated STM32CubeMX initialization code.
- [x] Imported project into STM32CubeIDE.
- [x] Verified project structure.

Generated project structure:

```text
firmware/
└── stm32f103/
    ├── Core/
    ├── Drivers/
    ├── MotorTinyML_F103.ioc
    ├── .project
    └── .cproject
