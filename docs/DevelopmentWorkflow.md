# 项目开发工作流

## 1. 目的

本文档规定 MotorTinyML 的任务执行、每日开发、测试、文档和 Git 提交流程。项目工程师执行 Tech Lead 的计划，不自行修改项目范围或系统架构。

## 2. 角色与决策边界

### Tech Lead

- 确定项目范围、架构和技术栈。
- 安排 Sprint、Issue 和验收标准。
- 审批依赖、工具链和接口变更。

### Project Engineer

- 按批准的任务实施、测试和记录。
- 保持代码、文档、TODO 和开发日志同步。
- 在需求不明确或涉及架构决策时暂停并请求确认。
- 不擅自 Push、合并或发布。

## 3. 项目开发流程

每个任务依次经过以下状态：

```text
任务确认 → 范围检查 → 实施 → 测试 → 文档同步 → 自检 → Commit → 等待评审
```

### 3.1 任务确认

开始前确认：

- Issue 编号、目标和交付物。
- 明确的验收标准。
- 技术负责人已批准的架构和接口。
- 不在任务范围内的事项。
- 是否允许 Commit、Push、合并或发布。

若任一关键条件不明确，先询问 Tech Lead，不通过猜测推进。

### 3.2 范围检查

```powershell
git status --short
git branch --show-current
git log -1 --oneline
```

- 确认工作区中是否已有其他人的修改。
- 不覆盖、删除或混入无关变更。
- 仅创建符合现有目录结构的文件。

### 3.3 实施

- 遵守 `CodingStandard.md` 和已批准架构。
- 保持模块职责单一和命名一致。
- 不把所有逻辑放入单个文件。
- 不提交生成产物、密钥或本地环境文件。
- 不因顺手优化而扩大 Issue 范围。

### 3.4 测试与验证

按变更类型执行适用检查：

| 变更类型 | 最低验证要求 |
|---|---|
| 文档 | 文件存在、链接有效、内容一致、无未批准决策 |
| 固件 | 编译、静态检查、目标硬件验证及结果记录 |
| Python | 格式检查、静态检查、自动化测试及结果记录 |
| 数据 | 格式、完整性、来源和可复现性检查 |
| 模型 | 训练配置、指标、转换、资源占用和设备端验证 |
| 构建环境 | 新环境恢复、版本核对和干净构建 |

无法执行的测试必须在 `DevelopmentLog.md` 中说明原因和风险。

### 3.5 文档同步

每项任务至少检查：

- `README.md`：项目入口、里程碑或使用方式是否变化。
- `Architecture.md`：仅记录 Tech Lead 批准的架构决策。
- `DevelopmentLog.md`：记录进展、测试、阻塞项和结果。
- `TODO.md`：更新完成项和后续项。
- API、测试报告和部署说明：按实际变更更新。
- `CHANGELOG.md`：项目建立后记录用户可见或交付相关变更。

### 3.6 完成检查

对照 `DefinitionOfDone.md` 验收。未通过测试、文档未同步或存在未记录阻塞时，不得标记完成。

## 4. Git 提交流程

### 4.1 分支

正式分支策略等待 Tech Lead 确认。获得任务分支授权后，按 `GitConvention.md` 命名；不要自行创建长期分支。

### 4.2 提交前检查

```powershell
git status --short
git diff --check
git diff
```

暂存后再次检查：

```powershell
git add -- <approved-paths>
git diff --cached --check
git diff --cached
```

检查重点：

- 只有当前 Issue 的文件。
- 没有密钥、个人配置、大型数据和构建产物。
- 测试与文档记录完整。
- 暂存内容与验收范围一致。

### 4.3 Commit Message

格式：

```text
<type>(<optional-scope>): <summary>
```

ISSUE-0009 建议提交信息：

```text
docs: add environment setup and development workflow
```

提交命令示例：

```powershell
git commit -m "docs: add environment setup and development workflow"
```

### 4.4 提交后检查

```powershell
git log -1 --format="%H%n%an <%ae>%n%s"
git status --short
```

确认提交作者、信息、文件范围和工作区状态正确。

### 4.5 Push 与合并

- Commit 只影响本地仓库。
- 只有在用户或 Tech Lead 明确授权后才能 Push。
- Push 前确认远程地址、目标分支及待推送提交。
- 合并、变基、强制推送和发布必须遵循批准的团队流程。
- 禁止未经明确授权执行强制推送。

## 5. 每日开发流程

### 开始工作

1. 阅读 Sprint、TODO、架构和相关 Issue。
2. 检查 Git 分支、最新提交和工作区状态。
3. 确认今日目标、任务、预计工时、交付物和验收标准。
4. 记录潜在风险、学习主题、提交建议和明日预览。

### 开发期间

1. 仅处理已批准范围。
2. 保持小步、可验证的修改。
3. 每完成一个逻辑单元就执行对应检查。
4. 及时记录决定、风险、失败测试和阻塞项。
5. 需求不清时停止相关修改并请求确认。

### 结束工作

1. 执行全部适用测试。
2. 检查差异和生成产物。
3. 同步 README、设计、API、测试和部署文档。
4. 更新 DevelopmentLog、TODO 和 CHANGELOG（建立后）。
5. 对照 Definition of Done 验收。
6. 生成一天一个的 Commit Message 建议；获准后提交。
7. 汇总 Progress、Finished、Blocked、Tomorrow 和项目完成度。
8. 未经授权不 Push。

## 6. Issue 完成记录模板

```markdown
## ISSUE-XXXX — <标题>

### Goal

### Tasks

### Deliverables

### Acceptance Criteria

### Tests

### Documentation Updated

### Risks / Blocked

### Commit Suggestion
```

## 7. 新电脑恢复后的首次开发检查

1. 按 `EnvironmentSetup.md` 恢复并验证工具版本。
2. 获取仓库并确认当前分支和最新提交。
3. 阅读 README、ProjectPlan、Architecture、Sprint 和 TODO。
4. 执行项目已定义的构建、测试和静态检查。
5. 确认工作区干净后再领取 Issue。

## 8. 相关文档

- `EnvironmentSetup.md`
- `ProjectPlan.md`
- `Architecture.md`
- `CodingStandard.md`
- `GitConvention.md`
- `DefinitionOfDone.md`
- `DevelopmentLog.md`
- `TODO.md`
