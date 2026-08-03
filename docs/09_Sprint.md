# Sprint 计划

## Sprint 0 - Day 1

- 日期：2026-08-01
- 主题：项目初始化
- 状态：已完成

### 今日目标

建立规范、清晰且可扩展的项目基础目录与文档框架。

### 今日任务

1. 创建项目标准目录。
2. 创建 README、LICENSE 和 `.gitignore`。
3. 创建项目管理与工程规范文档。
4. 检查目录和文件是否完整。
5. 更新开发日志和 TODO。
6. 准备当日 Git Commit Message。

### 预计工时

| 任务 | 预计工时 |
|---|---:|
| 目录初始化 | 0.5 小时 |
| 基础仓库文件 | 1.0 小时 |
| 项目管理文档 | 1.5 小时 |
| 工程规范文档 | 1.5 小时 |
| 检查与记录 | 0.5 小时 |
| 合计 | 5.0 小时 |

### 交付物

- 标准项目目录结构
- 基础仓库文件
- 项目管理文档
- 编码、Git 和完成定义规范

### 验收标准

- 所有规定目录均已创建。
- 所有规定文件均已创建且内容可读。
- README 准确描述项目目标和目录。
- `.gitignore` 覆盖 STM32CubeIDE、VSCode、Python 和常见构建产物。
- 文档未包含未经批准的架构决策。
- 未生成 STM32、Python 或 AI 代码。
- 仓库状态经过检查。

### 潜在风险

- 空目录不会被 Git 记录。
- 后续技术任务依赖技术负责人提供架构和需求。

### 学习主题

- 项目文档规范
- 嵌入式 AI 项目的目录组织
- 团队 Git 工作流

### Git Commit 建议

`chore: initialize project structure and documentation`

### 明日预览

等待技术负责人确认 Sprint 0 - Day 2 任务，不提前实施未批准内容。

## Sprint 0 最终验收

- 完成日期：2026-08-03
- 状态：已完成（Completed）

### Sprint 目标

完成项目初始化、工程规范、开发工作流、Dashboard、Roadmap 以及最终文档标准化，为 Sprint 1 提供可追溯的管理基线。

### 已完成

- [x] 建立标准项目目录和 Git 仓库。
- [x] 建立基础项目文档和工程规范。
- [x] 建立环境恢复和开发工作流。
- [x] 建立 Project Dashboard 与 Roadmap。
- [x] 建立 PRD、Milestones 和 Project Rules。
- [x] 建立 10 个 Epic 跟踪文件。
- [x] 为已有 ISSUE-0009 和 ISSUE-0017 建立追踪文件。
- [x] 建立 5 个通用项目模板。
- [x] 统一核心文档编号和交叉链接。

### 验收标准

- 所有要求的文档和目录存在。
- 仅创建已有 Issue 的跟踪文件。
- EPIC-01 至 EPIC-10 完整。
- 本地 Markdown 链接检查通过。
- `git diff --check` 通过。
- 未修改固件、Python、数据集、模型或硬件文件。

### Sprint 1 准入条件

- Tech Lead 确认 STM32F103 具体型号和开发板。
- Tech Lead 确认 STM32CubeIDE 与编译器版本。
- Tech Lead 批准 Sprint 1 范围和验收标准。

### Git Commit 建议

`docs: complete sprint 0 documentation standardization`

## Post-Sprint Maintenance

本节记录 Sprint 0 关闭后完成的项目基础设施维护，不修改 Sprint 0 已批准的目标、任务、交付物、验收结果或完成状态。

### ISSUE-0019 — Prompt Library

| 字段 | 内容 |
|---|---|
| 类型 | Development Infrastructure |
| 状态 | 已完成（Completed） |
| 描述 | 为 AI 辅助开发工作流创建可复用的 Prompt Library。 |
| 影响 | 仅改进开发文档资产和工作流。 |
| 非影响范围 | 未修改固件、硬件、Python、数据集或模型。 |

### 交付结果

- 创建根目录 `prompts/`。
- 创建 Sprint、Issue、Review、Documentation 和 Daily Report 通用 Prompt。
- 创建 Codex 项目执行规则。
- 文件、内容、占位符和策略章节验证通过。
