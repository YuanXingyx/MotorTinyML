# Git 规范

## 分支原则

分支策略由技术负责人确认。在未确认前，不自行创建长期分支或修改发布流程。

建议的任务分支命名：

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `chore/<short-description>`

## Commit Message

使用以下格式：

`<type>(<optional-scope>): <summary>`

常用类型：

- `feat`：新增功能
- `fix`：缺陷修复
- `docs`：仅文档变更
- `test`：测试变更
- `refactor`：不改变行为的重构
- `build`：构建系统或依赖变更
- `ci`：持续集成变更
- `chore`：项目维护工作

示例：

`chore: initialize project structure and documentation`

## 提交要求

1. 每个提交只包含一个清晰目的。
2. 提交信息使用祈使语气并保持简洁。
3. 提交前检查变更范围。
4. 不提交构建产物、临时文件、密钥或无关修改。
5. 功能变更应同时包含相应测试和文档。
6. 未通过验收标准的内容不得标记为完成。

## 每日提交

原则上每天提供一个汇总性的 Git Commit Message 建议。实际提交应在当天任务完成并通过检查后执行。
