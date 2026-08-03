# MotorTinyML 项目总览

> 本文档是 MotorTinyML 项目管理的唯一入口。项目状态、Epic、Issue、Sprint、里程碑、风险和最新进展均从本 Dashboard 查看。

## 项目概况

| 字段 | 当前内容 |
|---|---|
| 项目名称 | MotorTinyML |
| 当前版本 | v0.1.0-alpha |
| 当前 Epic | [EPIC-02 — STM32F103 Bring-up](epics/EPIC-02.md) |
| 当前 Sprint | Sprint 1 — 计划中 |
| 当前日期 | Sprint 0 已完成 — 2026-08-03 |
| 整体进度 | `[██░░░░░░░░░░░░░░░░░░] 10%` |
| 项目健康度 | 黄色（AMBER）— 技术基线决策待确认 |
| 当前风险 | 硬件、传感器、采样参数和完整工具链尚未批准 |
| 当前里程碑 | [Milestone 1 — STM32 Bring-up](14_Milestones.md#milestone-1--stm32-bring-up) |
| 开发板 | STM32F103 系列，具体型号待 Tech Lead 确认 |
| 当前传感器 | 待 Tech Lead 确认 |
| 当前硬件 | MCU、开发板、电机、驱动器和采集硬件待确认 |
| 仓库 | [YuanXingyx/MotorTinyML](https://github.com/YuanXingyx/MotorTinyML) |
| 最新提交 | `dede031` — 本次标准化前的最新已提交基线 |
| 文档状态 | Sprint 0 文档体系已标准化 |
| 文档覆盖率 | 结构覆盖率 100%；技术内容批准待完成 |
| 最新更新 | 2026-08-03 — ISSUE-0019 Prompt Library 已完成 |

## 整体进度

```text
[██░░░░░░░░░░░░░░░░░░] 10%
```

- EPIC-01 已完成，进度为 100%。
- EPIC-02 至 EPIC-10 尚未开始。
- 当前采用 10 个 Epic 等权计算；权重变更需 Tech Lead 批准。

## 当前开发板

| 项目 | 状态 | 说明 |
|---|---|---|
| MCU 系列 | 规划中 | EPIC-02 指定 STM32F103 |
| 具体 MCU | 待确认 | 由 Tech Lead 确认 |
| 开发板 | 待确认 | 具体板卡型号未批准 |
| 工具链 | 待确认 | STM32CubeIDE 与 Arm GNU Toolchain 版本未锁定 |
| 固件工程 | 未创建 | Sprint 0 未创建任何 STM32 工程 |

## 当前传感器

| 项目 | 状态 | 说明 |
|---|---|---|
| 传感器类型 | 待确认 | 由 Tech Lead 确认 |
| 传感器型号 | 待确认 | 由 Tech Lead 确认 |
| 接口 | 待确认 | ADC、I2C、SPI 或其他接口未批准 |
| 采样频率 | 待确认 | 依赖采集需求 |

## 当前硬件

| 组件 | 状态 | 说明 |
|---|---|---|
| STM32F103 | 规划中 | 具体型号与开发板待确认 |
| STM32F407 | 后续规划 | EPIC-07 的目标平台，具体型号待确认 |
| 电机 | 待确认 | 型号与运行参数未批准 |
| 电机驱动器 | 待确认 | 型号与接口未批准 |
| 传感器 | 待确认 | 类型与型号未批准 |
| 数据接口 | 待确认 | 串口、USB、SD 卡或其他方案未批准 |

## 当前 Issues

当前没有已批准且正在执行的 Issue。

## 已完成 Issues

| Issue ID | 标题 | 状态 | 结果 |
|---|---|---|---|
| [ISSUE-0009](issues/ISSUE-0009.md) | Codex 工作流完善 | 已完成 | 环境搭建和开发流程文档已建立 |
| [ISSUE-0017](issues/ISSUE-0017.md) | Project Dashboard 与 Roadmap | 已完成 | 项目管理中心和路线图已建立 |
| [ISSUE-0019](issues/ISSUE-0019.md) | Prompt Library | 已完成 | AI 辅助开发通用 Prompt Library 已建立并通过验证 |

## 即将开展的工作

Issue 编号和执行顺序由 Tech Lead 分配，不在 Dashboard 中虚构 Issue。

| 候选工作项 | 状态 | 依赖 |
|---|---|---|
| 确认 Sprint 1 技术基线 | 待分配 | Tech Lead 决策 |
| 确认 STM32F103 型号与开发板 | 待分配 | 硬件选型 |
| 锁定 STM32CubeIDE 与编译器版本 | 待分配 | MCU 与开发板确认 |
| 确认传感器、接口和采样要求 | 待分配 | 采集目标确认 |
| 制定 EPIC-02 的 Sprint 1 计划 | 待分配 | 技术基线完成 |

## 下一里程碑

### Milestone 1 — STM32 Bring-up

- [ ] Tech Lead 确认 MCU 与开发板。
- [ ] 锁定 STM32CubeIDE 和编译器版本。
- [ ] 批准 Sprint 1 范围和验收标准。
- [ ] 创建并验证 STM32F103 最小固件基线。
- [ ] 完成构建、下载、调试和测试记录。

## 文档导航

### 核心管理

- [Project Dashboard](00_ProjectDashboard.md)
- [产品需求文档](01_PRD.md)
- [项目路线图](02_Roadmap.md)
- [项目计划](03_ProjectPlan.md)
- [Sprint 记录](09_Sprint.md)
- [开发日志](10_DevelopmentLog.md)
- [更新日志](11_CHANGELOG.md)
- [TODO](13_TODO.md)
- [项目里程碑](14_Milestones.md)
- [项目规则](ProjectRules.md)

### 工程规范

- [系统架构](04_Architecture.md)
- [环境配置](05_EnvironmentSetup.md)
- [编码规范](06_CodingStandard.md)
- [Git 规范](07_GitConvention.md)
- [完成定义](08_DefinitionOfDone.md)
- [开发工作流](12_DevelopmentWorkflow.md)

### 追踪与模板

- [Epics](epics/)
- [Issues](issues/)
- [Issue 模板](templates/IssueTemplate.md)
- [Epic 模板](templates/EpicTemplate.md)
- [Sprint 模板](templates/SprintTemplate.md)
- [每日报告模板](templates/DailyReportTemplate.md)
- [评审模板](templates/ReviewTemplate.md)
- [Prompt Library](../prompts/)

## Dashboard 维护规则

1. Dashboard 是项目状态的唯一入口。
2. Issue 状态变化后更新“当前 Issues”和“已完成 Issues”。
3. 每个开发日结束前更新当前日期、项目健康度、风险和整体进度。
4. 每次 Commit 后更新最新提交。
5. 硬件、传感器或工具链决策批准后更新对应字段。
6. Epic 或里程碑进度变化时同步更新 Dashboard、Roadmap 和 Milestones。
7. 未经 Tech Lead 确认的信息必须标记为“待确认”。
