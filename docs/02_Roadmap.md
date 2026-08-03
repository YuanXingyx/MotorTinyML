# MotorTinyML Development Roadmap

## Purpose

本 Roadmap 定义 MotorTinyML 从项目初始化到正式发布的开发路线。

Roadmap 只描述已批准的项目阶段，不替代详细架构、Sprint 或 Issue。每个 Epic 的具体任务、验收标准和排期由 Tech Lead 确认。

## Roadmap Overview

```text
EPIC-01  Project Initialization
   ↓
EPIC-02  STM32F103 Bring-up
   ↓
EPIC-03  Sensor Driver Development
   ↓
EPIC-04  Data Acquisition
   ↓
EPIC-05  Dataset Processing
   ↓
EPIC-06  AI Model Training
   ↓
EPIC-07  Platform Migration (STM32F407)
   ↓
EPIC-08  TinyML Deployment
   ↓
EPIC-09  System Integration & Testing
   ↓
EPIC-10  Project Release
```

## Roadmap Status

| Epic | Name | Status | Progress |
|---|---|---|---:|
| [EPIC-01](epics/EPIC-01.md) | Project Initialization | Completed | 100% |
| [EPIC-02](epics/EPIC-02.md) | STM32F103 Bring-up | Planned | 0% |
| [EPIC-03](epics/EPIC-03.md) | Sensor Driver Development | Planned | 0% |
| [EPIC-04](epics/EPIC-04.md) | Data Acquisition | Planned | 0% |
| [EPIC-05](epics/EPIC-05.md) | Dataset Processing | Planned | 0% |
| [EPIC-06](epics/EPIC-06.md) | AI Model Training | Planned | 0% |
| [EPIC-07](epics/EPIC-07.md) | Platform Migration (STM32F407) | Planned | 0% |
| [EPIC-08](epics/EPIC-08.md) | TinyML Deployment | Planned | 0% |
| [EPIC-09](epics/EPIC-09.md) | System Integration & Testing | Planned | 0% |
| [EPIC-10](epics/EPIC-10.md) | Project Release | Planned | 0% |

## EPIC-01 — Project Initialization

### Goal

建立可维护、可复现、可跟踪的项目仓库和工程管理体系。

### Deliverables

- 标准项目目录结构
- Git 和远程仓库
- 项目基础文档
- 环境搭建文档
- 开发工作流
- Project Dashboard
- Roadmap
- Epic 和 Issue 管理目录
- 经 Tech Lead 批准的技术基线

### Status

Completed

### Progress

```text
[████████████████████] 100%
```

## EPIC-02 — STM32F103 Bring-up

### Goal

在 Tech Lead 指定的 STM32F103 硬件上建立可构建、可下载和可调试的最小固件基线。

### Deliverables

- 经批准的 STM32F103 开发板和 MCU 配置
- 固件工程基线
- 时钟和基础外设配置记录
- 编译、下载和调试验证结果
- Bring-up 测试报告
- 固件构建说明

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-03 — Sensor Driver Development

### Goal

按照批准的传感器和接口方案，实现稳定、可测试的传感器驱动。

### Deliverables

- 传感器接口规范
- 模块化传感器驱动
- 初始化和错误处理
- 原始数据读取接口
- 驱动单元测试或硬件验证
- API 文档和测试报告

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-04 — Data Acquisition

### Goal

建立可靠、可重复的数据采集流程，为数据集构建提供可追溯的原始数据。

### Deliverables

- 采样配置
- 数据采集固件
- 数据传输或存储方案
- 数据格式规范
- 时间戳和标签规则
- 数据采集测试报告
- 数据采集操作说明

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-05 — Dataset Processing

### Goal

将原始采集数据转换为可审计、可复现、适合模型训练的数据集。

### Deliverables

- 原始数据清单
- 数据清洗流程
- 分段与特征处理流程
- 标签定义
- 训练、验证和测试集划分
- 数据质量报告
- 数据集版本说明

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-06 — AI Model Training

### Goal

基于批准的数据和评价指标，训练满足目标任务要求的基线模型。

### Deliverables

- 模型训练配置
- 可复现训练流程
- 基线模型
- 评价指标与验证结果
- 混淆矩阵或等效评估材料
- 模型资源需求分析
- 模型说明文档

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-07 — Platform Migration (STM32F407)

### Goal

将已验证的采集和处理能力迁移到 Tech Lead 指定的 STM32F407 平台。

### Deliverables

- STM32F407 固件工程
- 硬件差异和迁移说明
- 外设和时钟迁移
- 传感器驱动适配
- 数据采集兼容性验证
- 性能与资源对比报告
- 迁移测试报告

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-08 — TinyML Deployment

### Goal

将已验证模型部署到目标 STM32F407 平台并完成设备端推理。

### Deliverables

- 量化或模型优化结果
- 可部署模型产物
- 推理运行时集成
- 输入预处理和输出后处理
- Flash、RAM 和执行时间报告
- 设备端推理验证
- 部署说明

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-09 — System Integration & Testing

### Goal

集成传感器、数据处理、模型推理和系统接口，并验证整体可靠性。

### Deliverables

- 集成固件
- 端到端测试方案
- 功能测试报告
- 性能测试报告
- 稳定性和异常处理测试
- 缺陷清单与关闭记录
- 系统验收报告

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## EPIC-10 — Project Release

### Goal

完成项目交付、版本发布和可复现性验收。

### Deliverables

- 发布版本
- Release Notes
- 完整源代码和构建说明
- 模型与数据版本说明
- API 和部署文档
- 测试及验收报告
- CHANGELOG
- 已知限制和后续建议

### Status

Planned

### Progress

```text
[░░░░░░░░░░░░░░░░░░░░] 0%
```

## Progress Rules

1. Epic 状态使用：
   - `Planned`
   - `In Progress`
   - `Blocked`
   - `Completed`
2. Epic Progress 根据已完成且通过验收的 Deliverables 计算。
3. 未通过 Definition of Done 的交付物不得计入完成进度。
4. Dashboard Overall Progress 默认采用 10 个 Epic 等权平均值。
5. 权重、顺序或范围只能由 Tech Lead 调整。
6. 每次 Epic 进度变化必须同步更新：
   - `00_ProjectDashboard.md`
   - `02_Roadmap.md`
   - `09_Sprint.md`
   - `10_DevelopmentLog.md`
   - `13_TODO.md`

## Dependencies and Risks

- EPIC-02 依赖 STM32F103 具体型号、开发板和工具链确认。
- EPIC-03 依赖传感器选型及接口确认。
- EPIC-04 依赖采样频率、数据格式和传输方案确认。
- EPIC-05 依赖可用且可追溯的原始数据。
- EPIC-06 依赖数据集、任务定义和评价指标确认。
- EPIC-07 依赖 STM32F407 具体型号、开发板和迁移要求确认。
- EPIC-08 依赖模型资源预算和推理运行时确认。
- EPIC-09 依赖全部模块接口稳定。
- EPIC-10 依赖测试、文档和验收全部完成。

## Latest Update

- Date: 2026-08-03
- Issue: Sprint 0 Final Documentation Standardization
- Update: EPIC-01 与 Sprint 0 已完成，文档体系统一为编号结构。
