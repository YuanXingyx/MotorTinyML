# MotorTinyML Project Dashboard

> MotorTinyML 项目管理唯一入口。项目状态、Issue、Epic、里程碑和最新进展均从本 Dashboard 查看。

## Project Overview

| Field | Current Value |
|---|---|
| Project Name | MotorTinyML |
| Version | Unreleased |
| Current Epic | EPIC-01 — Project Initialization |
| Current Sprint | Sprint 0 — Project Initialization |
| Current Day | Day 2 — 2026-08-02 |
| Overall Progress | `[██░░░░░░░░░░░░░░░░░░] 9%` |
| Repository | [YuanXingyx/MotorTinyML](https://github.com/YuanXingyx/MotorTinyML) |
| Current Development Board | 待 Tech Lead 确认；EPIC-02 计划使用 STM32F103 系列 |
| Current Sensor | 待 Tech Lead 确认 |
| Current Hardware | MCU、开发板、电机、驱动器及采集硬件待 Tech Lead 确认 |
| Next Milestone | 完成 EPIC-01 项目初始化和技术基线确认 |
| Latest Commit | `82c6416` — `docs: add environment setup and development workflow` |
| Latest Update | 2026-08-02 |

## Overall Progress

```text
[██░░░░░░░░░░░░░░░░░░] 9%
```

计算规则：

- Overall Progress 为 10 个 Epic 进度的等权平均值。
- 当前 EPIC-01 进度为 90%，其余 Epic 为 0%。
- 当 Epic 权重由 Tech Lead 确认后，应按批准的权重重新计算。

## Current Development Board

| Item | Status | Notes |
|---|---|---|
| MCU Family | Planned | EPIC-02 指定 STM32F103 |
| Development Board | Pending Decision | 具体板卡型号待 Tech Lead 确认 |
| Toolchain | Pending Decision | STM32CubeIDE 和 Arm GNU Toolchain 版本待确认 |
| Firmware Project | Not Created | ISSUE-0017 仅建立项目管理体系 |

## Current Sensor

| Item | Status | Notes |
|---|---|---|
| Sensor Type | Pending Decision | 待 Tech Lead 确认 |
| Sensor Model | Pending Decision | 待 Tech Lead 确认 |
| Interface | Pending Decision | ADC、I2C、SPI 或其他接口待确认 |
| Sampling Rate | Pending Decision | 待数据采集需求确认 |

## Current Hardware

| Component | Status | Notes |
|---|---|---|
| MCU | Planned | STM32F103 系列，具体型号待确认 |
| Development Board | Pending Decision | 待 Tech Lead 确认 |
| Motor | Pending Decision | 型号和工作参数待确认 |
| Motor Driver | Pending Decision | 型号和接口待确认 |
| Sensor | Pending Decision | 类型和型号待确认 |
| Data Interface | Pending Decision | 串口、USB、SD 卡或其他方案待确认 |

## Current Issues

当前没有进行中的 Issue。

## Completed Issues

| Issue ID | Title | Status | Result |
|---|---|---|---|
| ISSUE-0009 | Codex 工作流完善 | Completed | 环境搭建和开发流程文档已建立 |
| ISSUE-0017 | Project Dashboard 与 Roadmap | Completed | 项目管理中心、路线图及管理目录已建立 |

## Upcoming Issues

Issue 编号和执行顺序由 Tech Lead 分配。

| Proposed Work Item | Status | Dependency |
|---|---|---|
| 确认项目技术基线 | Awaiting Assignment | Tech Lead 决策 |
| 确认 STM32F103 具体型号与开发板 | Awaiting Assignment | 硬件选型 |
| 锁定 STM32CubeIDE 与编译器版本 | Awaiting Assignment | MCU 与开发板确认 |
| 确认传感器、接口和采样要求 | Awaiting Assignment | 采集目标确认 |
| 制定 EPIC-02 Sprint 计划 | Awaiting Assignment | 技术基线完成 |

## Next Milestone

### EPIC-01 — Project Initialization Complete

完成条件：

- [x] 创建标准项目目录。
- [x] 建立 Git 仓库和远程仓库。
- [x] 建立基础项目文档。
- [x] 建立环境恢复和开发工作流。
- [x] 建立 Project Dashboard。
- [x] 建立项目 Roadmap。
- [x] 创建 Epic 和 Issue 管理目录。
- [ ] Tech Lead 确认技术基线。
- [ ] Sprint 0 完成验收。

## Project Navigation

### Management

- [Project Dashboard](00_ProjectDashboard.md)
- [Roadmap](02_Roadmap.md)
- [Project Plan](ProjectPlan.md)
- [Sprint](Sprint.md)
- [TODO](TODO.md)
- [Development Log](DevelopmentLog.md)

### Engineering

- [Architecture](Architecture.md)
- [Environment Setup](EnvironmentSetup.md)
- [Development Workflow](DevelopmentWorkflow.md)
- [Coding Standard](CodingStandard.md)
- [Git Convention](GitConvention.md)
- [Definition of Done](DefinitionOfDone.md)

### Tracking

- [Epics](epics/)
- [Issues](issues/)

## Dashboard Maintenance Rules

1. Dashboard 是项目状态的唯一入口。
2. 每次 Issue 状态变化后更新 Current Issues 和 Completed Issues。
3. 每个开发日结束前更新 Current Day、Overall Progress 和 Latest Update。
4. 每次 Commit 后更新 Latest Commit。
5. 每次硬件、传感器或技术栈决策批准后更新对应字段。
6. Roadmap 进度变化时同步更新 Overall Progress。
7. 未经 Tech Lead 确认的架构信息必须标记为 `Pending Decision`。
