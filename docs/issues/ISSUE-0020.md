# ISSUE-0020 — Documentation Classification Policy

## 元数据

| 字段 | 内容 |
|---|---|
| Issue ID | ISSUE-0020 |
| 类型 | Project Policy Update |
| 状态 | Completed |
| Epic | EPIC-01 |
| Sprint | Sprint 0 Maintenance |
| 负责人 | Project Engineer |
| 完成日期 | 2026-08-03 |

## Goal

建立文档分类策略，减少不必要的文档更新，并使项目文档维护符合企业级工程实践。

## Tasks

- [x] Create Documentation Classification Policy
- [x] Update ProjectRules.md
- [x] Update CodexInstructions.md
- [x] Validate documentation workflow rules

## Files Modified

- `docs/ProjectRules.md`
- `prompts/CodexInstructions.md`

## Protected Files

以下区域在 ISSUE-0020 中未修改：

- `firmware/`
- `python/`
- `dataset/`
- `models/`
- `hardware/`

本 Issue 记录创建过程中也未修改 `docs/ProjectRules.md` 或 `prompts/CodexInstructions.md`。

## Validation

- Level 1/2/3 文档分类策略已存在。
- Codex 文档工作流已更新。
- Git 策略已保留，禁止执行 Git 命令、Commit 和 Push 的规则仍然存在。
- 无无关文件被更改。
- 分类策略条目检查：15/15。
- Codex 工作流步骤检查：3/3。
- Codex 策略章节检查：8/8。
- 文档提案字段检查：4/4。
- Git 禁止规则检查：4/4。
- 被替换的旧文档评估流程残留：0。
- 尾随空格：0 行。

## Commit

Pending Git commit

## Risks

- 普通 Issue 是否触发 Level 2 文档更新，必须依据已批准的里程碑触发条件判断。
- Level 3 文档仍需 Tech Lead 明确授权、Execution Plan 和批准后才能修改。
- Prompt Library 使用效果依赖输入上下文完整且决策已获批准。

## Completion Summary

文档分类策略已建立，Codex 文档评估工作流已切换为 Level 1/2/3 分类流程，相关策略验证通过。
