# 开发日志

## 2026-08-01 — Sprint 0 Day 1

### 计划

- 初始化项目目录。
- 创建基础仓库文件。
- 创建项目管理和工程规范文档。
- 验证目录及文件完整性。

### 进展

- 已按确认的预览创建项目目录与基础文件。
- 已完成目录、文件和关键 `.gitignore` 规则检查。
- 已初始化本地 Git 仓库，尚未配置远程仓库且未 Push。
- 已使用仓库级提交者身份完成第一次本地 Git 提交。

### 已完成

- 创建 `firmware/`、`python/`、`dataset/`、`models/`、`docs/` 和 `hardware/`。
- 创建 README、MIT License 和 `.gitignore`。
- 创建全部规定的项目管理及工程规范文档。
- 未生成 STM32、Python 或 AI 代码。

### 阻塞项

- 后续技术工作等待 Tech Lead 的架构和任务安排。

### 测试与检查

- 目录完整性检查：6/6 通过。
- 文件完整性检查：11/11 通过。
- `.gitignore` 关键规则抽查：4/4 通过。
- 禁止生成的固件、Python、Notebook 和模型文件检查：0 个。
- Git 状态检查：通过，待提交范围仅包含 Sprint 0 Day 1 项目文件。

### 明日计划

等待 Sprint 0 - Day 2 任务。

### 项目完成度

- Sprint 0 Day 1：100%。
- 整体项目：后续 Sprint 尚未规划，暂不计算百分比。

### Git Commit 建议

`chore: initialize project structure and documentation`

## 2026-08-01 — ISSUE-0009 Codex 工作流完善

### 目标

补充可用于新电脑环境恢复的环境搭建文档和标准开发工作流。

### 已完成

- 创建 `EnvironmentSetup.md`，记录安装步骤、版本基线、验证清单和环境变更规则。
- 创建 `DevelopmentWorkflow.md`，记录项目开发、Git 提交和每日开发流程。
- 在 README 中添加两份文档的入口。

### 环境检测

- Git：`2.54.0.windows.1`，已验证。
- Python、CMake、Ninja、Arm GNU Toolchain：当前未在 `PATH` 中检测到。
- 其余版本等待 Tech Lead 确认，不作为既定架构或工具链决策。

### 测试与检查

- 规定文档完整性检查：2/2 通过。
- README 文档链接检查：2/2 通过。
- 环境文档必需章节检查：3/3 通过。
- 工作流文档必需章节检查：3/3 通过。
- `git diff --check`：通过。
- Git 变更范围：仅包含 ISSUE-0009 文档及同步记录。

### 阻塞项

- 软件工具链精确版本尚待 Tech Lead 确认。
- 远程仓库尚未配置，克隆地址待补充。

### Git Commit 建议

`docs: add environment setup and development workflow`
