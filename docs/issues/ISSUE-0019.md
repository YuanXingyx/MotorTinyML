# ISSUE-0019 — Prompt Library

## 元数据

| 字段 | 内容 |
|---|---|
| Issue ID | ISSUE-0019 |
| 所属 Epic | [EPIC-01](../epics/EPIC-01.md) |
| Sprint | Sprint 0（Post-Sprint Maintenance） |
| 版本 | v0.1.0-alpha |
| 类型 | Development Infrastructure |
| 状态 | 已完成（Completed） |
| 负责人 | Project Engineer |
| 完成日期 | 2026-08-03 |

## 目标

创建可复用的 AI 辅助开发 Prompt Library，并将其作为 MotorTinyML 的项目资产。

## 背景

项目需要一套通用、专业、可维护的 Prompt，以支持 Sprint 规划、Issue 执行、工程评审、文档同步、每日报告和 Codex 执行约束。

## 范围

### 范围内

- 创建根目录 `prompts/`。
- 创建 6 个经批准的 Markdown Prompt 文件。
- 使用通用占位符，避免硬编码特定 Issue。
- 验证文件、内容、占位符和策略章节。

### 范围外

- 固件、硬件、Python、数据集和模型变更。
- 项目方向、架构或产品需求变更。
- Git、Commit 或 Push 操作。

## 任务

- [x] 创建 `SprintPrompt.md`。
- [x] 创建 `IssuePrompt.md`。
- [x] 创建 `ReviewPrompt.md`。
- [x] 创建 `DocumentationPrompt.md`。
- [x] 创建 `DailyReportPrompt.md`。
- [x] 创建 `CodexInstructions.md`。
- [x] 执行文件和内容验证。
- [x] 完成批准的项目管理文档同步。

## 交付物

- [Sprint Prompt](../../prompts/SprintPrompt.md)
- [Issue Prompt](../../prompts/IssuePrompt.md)
- [Review Prompt](../../prompts/ReviewPrompt.md)
- [Documentation Prompt](../../prompts/DocumentationPrompt.md)
- [Daily Report Prompt](../../prompts/DailyReportPrompt.md)
- [Codex Instructions](../../prompts/CodexInstructions.md)

## 验收标准与结果

| 验收项 | 结果 |
|---|---|
| 创建根目录 `prompts/` | 通过 |
| 创建 6 个批准文件 | 6/6 通过 |
| 文件均为非空 Markdown | 通过 |
| 使用通用占位符 | 通过 |
| 不硬编码具体 Issue | 硬编码 Issue ID 为 0 |
| CodexInstructions 包含 6 个必需策略章节 | 6/6 通过 |
| 未修改受保护实现区域 | 通过 |
| 未执行 Git 命令 | 通过 |

## 文档更新

- Project Dashboard：已更新。
- Sprint：追加 Post-Sprint Maintenance，未修改 Sprint 0 原有内容。
- Development Log：已记录实施和验证结果。
- CHANGELOG：已记录到 v0.1.0-alpha。
- EPIC-01：已增加 Issue 关联和维护记录。
- README：已增加 Prompt Library 入口。
- Architecture、Roadmap、Milestones 和 PRD：无技术或产品范围变化，保持不变。

## 风险

- Prompt 输出质量依赖使用者提供完整、准确且已批准的上下文。
- Prompt Library 不能替代 Tech Lead 的设计、范围和批准职责。

## 完成总结

ISSUE-0019 已按批准范围实施并通过验证。Prompt Library 已纳入项目资产和管理追踪体系。

## Git

未执行任何 Git 命令。Commit 和 Push 由用户手动完成。

## 批准

Tech Lead 已批准 Epic、Sprint、版本、README 和文档同步范围。
