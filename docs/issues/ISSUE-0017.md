# ISSUE-0017 — Project Dashboard 与 Roadmap

## 元数据

| 字段 | 内容 |
|---|---|
| Issue ID | ISSUE-0017 |
| 所属 Epic | [EPIC-01](../epics/EPIC-01.md) |
| 状态 | 已完成（Completed） |
| 优先级 | 未分配 |
| 负责人 | Project Engineer |
| 完成日期 | 2026-08-03 |

## 目标

建立 MotorTinyML 项目管理中心和完整开发路线图。

## 任务

- [x] 创建 Project Dashboard。
- [x] 创建项目 Roadmap。
- [x] 建立 Epic 和 Issue 管理目录。
- [x] 验证 Dashboard 必需字段。
- [x] 验证 EPIC-01 至 EPIC-10。
- [x] 确认未修改代码。

## 交付物

- [Project Dashboard](../00_ProjectDashboard.md)
- [Roadmap](../02_Roadmap.md)
- `epics/`
- `issues/`

## 验收结果

- Dashboard 字段：16/16
- Roadmap Epic：10/10
- 非文档变更：0
- `git diff --check`：通过

## Commit

`dede031` — `docs: add project dashboard and development roadmap`

## 风险

- 版本策略在本次 Sprint 0 标准化中确定为 `v0.1.0-alpha`。
- 开发板、传感器和具体硬件仍待确认。
- Epic 当前采用等权进度计算。
