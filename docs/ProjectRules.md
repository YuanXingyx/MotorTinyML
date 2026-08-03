# MotorTinyML 项目规则

## 1. 决策权限

- Tech Lead 负责项目范围、架构、硬件、接口和技术栈决策。
- Project Engineer 负责执行已批准的计划。
- 需求不明确时，必须先确认再实施。

## 2. 范围控制

- 未经批准不得扩大项目范围或重新设计架构。
- 每个 Issue 只包含已批准的交付物。
- 无关变更必须拆分为不同 Issue 和 Commit。

## 3. 文档管理

- [Project Dashboard](00_ProjectDashboard.md) 是项目管理唯一入口。
- 每次变更必须同步受影响的文档。
- Epic、Issue、Sprint、里程碑和发布必须可追溯。
- 未确认决策必须明确标记为“待确认”。
- 不允许存在失效的内部 Markdown 链接。

## 4. 开发规则

- 使用模块化结构和一致命名。
- 不在单个文件中混合无关职责。
- 不引入未经批准的依赖。
- 未经批准不提交生成产物、大型数据或模型文件。

## 5. 测试规则

- 测试不可跳过。
- 无法执行或失败的测试必须记录原因和风险。
- 硬件验证必须记录平台、步骤和结果。
- 未满足验收标准的任务不得标记为完成。

## 6. Git 规则

- 暂存前检查全部变更。
- 只暂存当前任务批准的文件。
- Commit Message 遵循 Conventional Commits。
- 测试和文档检查完成后才能 Commit。
- Push、合并、变基、发布和强制推送需要明确授权。
- 未经明确批准禁止强制推送。

## 7. 每日流程

每天记录：今日目标、任务、预计工时、交付物、验收标准、风险、学习主题、Commit 建议、明日预览、完成项、阻塞项和项目完成度。

## 8. 完成定义

任务必须同时满足：范围已批准、实现完成、测试通过、文档同步、日志更新、变更检查和验收标准通过。

## 9. 受保护区域

文档任务不得修改：

- `firmware/`
- `python/`
- `dataset/`
- `models/`
- `hardware/`

# Documentation Classification Policy

项目文档分为三个级别。文档更新必须遵循对应级别的触发条件，避免普通 Issue 引发不必要的全量文档修改。

## Level 1 — Dynamic Documents

### 目的

用于记录日常开发中频繁变化的项目状态和执行进展。

### 包含文档

- `docs/00_ProjectDashboard.md`
- `docs/10_DevelopmentLog.md`
- `docs/13_TODO.md`

### 规则

- 每个 Issue 完成后评估 Level 1 文档。
- 只有当实现改变项目状态或日常进展时才更新。
- 这些文档预期会频繁变化。
- 不得为了形式完整而写入无实际状态变化的内容。

## Level 2 — Milestone Documents

### 目的

仅在项目里程碑、工程阶段、Sprint、Epic 或发布状态发生变化时更新。

### 包含文档

- `docs/09_Sprint.md`
- `docs/11_CHANGELOG.md`
- `docs/14_Milestones.md`
- `docs/epics/*.md`

### 更新条件

仅在以下情况更新：

- Sprint 开始或结束。
- Milestone 状态发生变化。
- Epic 状态发生变化。
- 创建正式 Release。
- 必须记录 Post-Sprint Maintenance 活动。

### 规则

- 普通 Issue 不更新 Level 2 文档。
- Issue 只有满足上述触发条件时才能提出 Level 2 更新。
- 更新必须说明触发条件和对项目阶段的影响。
- Level 2 更新需要 Documentation Update Plan 和明确批准。

## Level 3 — Stable Documents

### 目的

记录项目设计、架构、环境和工程标准。这些文档应保持稳定。

### 包含文档

- `docs/01_PRD.md`
- `docs/03_ProjectPlan.md`
- `docs/04_Architecture.md`
- `docs/05_EnvironmentSetup.md`
- `docs/06_CodingStandard.md`
- `docs/07_GitConvention.md`
- `docs/08_DefinitionOfDone.md`
- `docs/ProjectRules.md`

### 更新条件

仅在以下情况更新：

- Tech Lead 批准设计决策。
- 系统架构发生变化。
- 项目标准发生变化。
- 开发工作流发生变化。

### 规则

- 普通 Issue 不更新 Level 3 文档。
- 不得把推测或未批准决定写入 Level 3 文档。
- 必须保留 Tech Lead 的人工设计决策。
- Level 3 更新必须由 Issue 明确授权。
- Level 3 更新需要 Execution Plan 和明确批准。

## 文档更新提案要求

提出文档更新时，必须为每份受影响文档说明：

- Document
- Level
- Reason
- Decision

示例：

```text
Document:
docs/10_DevelopmentLog.md

Level:
Level 1

Reason:
Daily implementation record.

Decision:
Update Required.
```

没有满足对应级别触发条件的文档，应明确标记为 `No Update Required`。
