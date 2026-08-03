# 开发环境搭建

## 1. 目的

本文档用于在新电脑上恢复 MotorTinyML 开发环境。所有成员应使用技术负责人批准的软件版本；未批准的工具不得作为项目标准自行引入。

## 2. 当前环境基线

最后核对日期：2026-07-31

| 软件 | 项目要求版本 | 当前检测结果 | 用途 | 状态 |
|---|---|---|---|---|
| Windows | 待 Tech Lead 确认 | Windows 环境 | 开发主机 | 待确认 |
| Git | 2.54.0.windows.1 | 2.54.0.windows.1 | 版本控制 | 已验证 |
| VSCode | 待 Tech Lead 确认 | 未登记 | 通用编辑器 | 待确认 |
| STM32CubeIDE | 待 Tech Lead 确认 | 未登记 | STM32 固件开发 | 待确认 |
| Python | 待 Tech Lead 确认 | 未在 `PATH` 中检测到 | 数据处理与模型工具 | 待确认 |
| CMake | 待 Tech Lead 确认 | 未在 `PATH` 中检测到 | 构建工具 | 待确认 |
| Ninja | 待 Tech Lead 确认 | 未在 `PATH` 中检测到 | 构建执行器 | 待确认 |
| Arm GNU Toolchain | 待 Tech Lead 确认 | 未在 `PATH` 中检测到 | ARM 交叉编译 | 待确认 |
| AI 框架及转换工具 | 待 Tech Lead 确认 | 未登记 | 模型训练与部署 | 待确认 |

> 版本表是环境恢复的唯一基线。Tech Lead 确认工具链后，应立即填写精确版本，并同步相关安装和验证命令。

## 3. 新电脑恢复步骤

### 3.1 安装 Git

1. 安装版本表中指定的 Git for Windows。
2. 打开 PowerShell，验证安装：

```powershell
git --version
```

3. 配置个人 Git 身份：

```powershell
git config --global user.name "<your-name>"
git config --global user.email "<your-email>"
```

如果不希望影响其他仓库，在克隆项目后去掉 `--global`，改用仓库级配置。

### 3.2 获取项目

批准的远程仓库地址为 `https://github.com/YuanXingyx/MotorTinyML.git`。不要使用来源不明的镜像。

```powershell
git clone https://github.com/YuanXingyx/MotorTinyML.git MotorTinyML
Set-Location MotorTinyML
git status
```

首次恢复时应确认当前分支、最新提交和工作区状态：

```powershell
git branch --show-current
git log -1 --oneline
git status --short
```

### 3.3 安装编辑器

1. 按版本表安装 VSCode。
2. 仅安装仓库文档或 Tech Lead 批准的扩展。
3. 不提交个人工作区文件；`.gitignore` 已忽略常见本地配置。

验证命令：

```powershell
code --version
```

### 3.4 安装 STM32 工具链

在 MCU 和工具链版本确认后执行：

1. 安装指定版本的 STM32CubeIDE。
2. 根据 Tech Lead 决策安装或使用 IDE 自带的 Arm GNU Toolchain。
3. 配置工作区，但不要把 IDE 元数据或构建产物提交到仓库。
4. 使用批准的固件工程执行一次干净构建。

验证项：

- STM32CubeIDE 可以启动。
- 编译器版本与本文件版本表一致。
- 固件工程能够无错误构建。
- `Debug/`、`Release/`、`*.elf`、`*.hex` 和 `*.bin` 未进入 Git 变更列表。

### 3.5 安装 Python 环境

在 Python 版本和依赖清单确认后执行：

1. 安装版本表指定的 Python。
2. 在仓库根目录创建独立虚拟环境：

```powershell
py -<major.minor> -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
```

3. 当项目提供锁定的依赖文件后，严格按该文件安装。不要在未批准的情况下新增或升级依赖。

```powershell
python -m pip install --upgrade pip
python -m pip install -r <approved-requirements-file>
```

4. 退出虚拟环境：

```powershell
deactivate
```

### 3.6 安装构建及 AI 工具

CMake、Ninja、训练框架、模型转换器和推理运行时的安装方式，必须等待 Tech Lead 确认精确版本及来源。确认后应在此处记录：

- 官方下载来源
- 精确版本
- 安装选项
- PATH 配置
- 验证命令
- 与模型或固件的兼容性限制

## 4. 环境验证清单

新环境恢复完成后逐项检查：

- [ ] Git 版本与版本表一致。
- [ ] Git 用户身份正确。
- [ ] 项目可从批准的远程仓库克隆。
- [ ] 当前分支和提交符合团队要求。
- [ ] VSCode 版本及扩展符合项目要求。
- [ ] STM32CubeIDE 和交叉编译器版本一致。
- [ ] 固件能够完成干净构建。
- [ ] Python 版本及虚拟环境正确。
- [ ] Python 依赖可从锁定文件恢复。
- [ ] AI 工具版本与模型部署链路兼容。
- [ ] 适用测试全部通过。
- [ ] `git status --short` 不包含构建产物、环境文件或密钥。

## 5. 本地配置与敏感信息

- 不提交 `.env`、私钥、口令、访问令牌和个人配置。
- 敏感配置通过批准的安全渠道获取。
- 如需环境变量模板，只提交不含真实值的 `.env.example`。
- 数据集和模型产物是否允许版本化，由 Tech Lead 决定。

## 6. 环境变更规则

1. 工具版本升级必须由 Tech Lead 批准。
2. 变更后更新本文件的版本表、安装步骤和验证结果。
3. 依赖文件必须锁定并接受评审。
4. 环境变更应使用独立提交，建议格式：

```text
build: update development environment to <version>
```

## 7. 已知待办

- 确认操作系统支持范围。
- 确认 VSCode 和扩展版本。
- 确认 MCU、STM32CubeIDE 与 Arm GNU Toolchain 版本。
- 确认 Python、依赖管理方式和测试工具版本。
- 确认 CMake、Ninja 及 AI 工具链版本。
