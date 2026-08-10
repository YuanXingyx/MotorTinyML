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

- 创建 `05_EnvironmentSetup.md`，记录安装步骤、版本基线、验证清单和环境变更规则。
- 创建 `12_DevelopmentWorkflow.md`，记录项目开发、Git 提交和每日开发流程。
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

## 2026-08-03 — Sprint 0 最终文档标准化

### 目标

在 Sprint 1 开始前统一整个项目文档体系，并完成 Sprint 0。

### 已完成

- 将 10 个已有核心文档重命名为编号结构。
- 创建 PRD、CHANGELOG、Milestones 和 Project Rules。
- 创建 5 个通用项目管理模板。
- 创建 EPIC-01 至 EPIC-10 跟踪文件。
- 仅为已有 ISSUE-0009 和 ISSUE-0017 创建 Issue 文件。
- 更新 Dashboard、Roadmap、ProjectPlan、Sprint、TODO 和 README。
- 将 Sprint 0 和 EPIC-01 标记为已完成。

### 测试与检查

- 核心文档完整性：16/16 通过。
- Epic 文件：10/10 通过。
- 已有 Issue 文件：2/2 通过，未生成虚构 Issue。
- 通用模板：5/5 通过。
- 旧文档路径残留：0。
- 本地 Markdown 文件检查：34 个，失效链接 0 个。
- 旧文件名引用检查：0 个。
- `git diff --check`：通过。
- 固件、Python、数据集、模型和硬件变更：0 个。

### 风险

- 硬件、传感器、采样参数和完整工具链仍待 Tech Lead 确认。
- Milestone 的 Sprint 分配为规划基线，最终排期仍需批准。

### 明日计划

等待 Tech Lead 批准 Sprint 1 技术基线和具体 Issue。

### 项目完成度

- Sprint 0：100%。
- EPIC-01：100%。
- 整体项目：10%。

### Git Commit 建议

`docs: complete sprint 0 documentation standardization`

## 2026-08-03 — ISSUE-0019 Prompt Library

### 类型

Development Infrastructure — Sprint 0 Post-Sprint Maintenance

### 目标

创建可复用、通用、专业且适合企业研发的 AI 辅助开发 Prompt Library。

### 已完成

- 创建根目录 `prompts/`。
- 创建 `SprintPrompt.md`。
- 创建 `IssuePrompt.md`。
- 创建 `ReviewPrompt.md`。
- 创建 `DocumentationPrompt.md`。
- 创建 `DailyReportPrompt.md`。
- 创建 `CodexInstructions.md`。

### 测试与检查

- 预期文件：6/6。
- 缺失文件：0。
- 非预期文件：0。
- 空文件：0。
- 非 Markdown 文件：0。
- 核心占位符检查：通过。
- 硬编码 Issue ID：0。
- Codex 必需策略章节：6/6。
- 尾随空格：0 行。

### 影响范围

- 仅新增 Prompt Library 项目资产。
- 未修改固件、硬件、Python、数据集或模型。
- 未执行任何 Git 命令。

### 风险

- Prompt 使用者仍需填入真实项目上下文和已批准决策。
- 通用 Prompt 不能替代 Tech Lead 的架构和范围决策。

### 状态

已完成（Completed）。

## 2026-08-08 — ISSUE-0021 STM32F103 开发环境搭建与验证

### 类型

Hardware Bring-up / Development Infrastructure

### 目标

建立 STM32F103C8T6 基础开发环境，完成工程构建、下载和第一次硬件验证。

### 已完成

- 创建并打开 `firmware/stm32f103/MotorTinyML_F103` STM32CubeIDE 工程。
- 配置 STM32F103C8T6 和 PC13 LED。
- Clean Project 成功。
- Build Project 成功。
- ST-Link V2 下载成功。
- MCU 复位后正常运行。
- PC13 LED 按约 500 ms 周期闪烁。

### 验证结果

- IDE：STM32CubeIDE 2.2.0。
- MCU：STM32F103C8T6。
- 开发板：STM32F103C8T6 Blue Pill。
- LED：PC13。
- 固件构建产物：ELF、MAP、LIST 已生成。
- 硬件结果：Project Engineer 确认通过。

### 文档状态

- Level 1 文档已同步。
- EPIC-02 和 Milestone 1 是否关闭：待 Tech Lead 确认。
- Level 2 和 Level 3 文档未修改。

### 风险

- 传感器、采样参数和后续数据采集方案仍待确认。
- Debug 构建产物的版本控制策略仍需确认。

### 项目完成度

- ISSUE-0021：100%。
- EPIC-02：保持原状态，待里程碑关闭决策。
- 整体项目：保持 10%，等待 Epic 状态更新。

## 2026-08-08 — ISSUE-0022 STM32F103 UART 调试控制台

### 类型

Hardware Bring-up / Debug Infrastructure

### 目标

建立 STM32F103C8T6 的 USART1 调试输出通道，为后续外设与 TinyML 调试提供稳定日志接口。

### 已完成

- USART1 配置为 115200 8-N-1，无流控。
- PA9 作为 UART TX，USB-TTL 通信验证通过。
- MCU 复位后输出 `MotorTinyML STM32F103 boot`。
- 原有 PC13 LED Blink 功能保持正常。
- 未启动 SPI 或 ADXL345 实现。

### 验收结果

- STM32F103C8T6 启动：通过。
- UART TX 与串口终端通信：通过。
- 启动日志可读性：通过。
- LED 回归验证：通过。

### 文档同步

- 已同步 Level 1 动态文档。
- EPIC-02 与 Milestone 1 关闭状态仍待 Tech Lead 决策。
- Level 2、Level 3 文档未修改。

## 2026-08-10 — ISSUE-0025 TB6612 PWM Speed Control

### 类型

Hardware Bring-up / Motor Control Infrastructure

### 已完成

- 完成 TB6612 A 通道电机控制。
- PB0/PB1/PB10/PA8 已用于电机控制信号。
- 新增 `App/Motor/motor.c` 和 `App/Motor/motor.h`。
- 实现 `Motor_Init()`、`Motor_Start()`、`Motor_Stop()`。
- PWM 速度控制已实现并完成硬件验证。
- TB6612 AO1/AO2、电源和共地连接验证通过。

### 验收结果

- 工程构建错误数：0。
- 固件下载：通过。
- UART Boot Log：通过。
- PC13 LED 回归测试：通过。
- 电机启动、停止和约 2 秒运行/2 秒停止循环：通过。

### 范围控制

- 未实现闭环速度控制或保护机制。
- ISSUE-0024 保留为 ADXL345 驱动任务，当前因器件未到货而阻塞。

### 风险

- USB-TTL 电平、接线和终端参数需在后续调试中保持一致。
- 尚未建立自动化串口回归测试。

## 2026-08-08 — ISSUE-0023 STM32F103 SPI1 Bring-up

### 类型

Hardware Bring-up / Peripheral Infrastructure

### 目标

在现有 STM32F103C8T6 工程中建立 SPI1 主机通信基础，为后续 ADXL345 驱动提供稳定接口。

### 已完成

- SPI1 配置为 Master、2 Lines Full Duplex、8 Bits。
- SPI Mode 3：CPOL High、CPHA 2 Edge。
- Prescaler 32、MSB First、Software NSS、CRC Disabled。
- PA5：SPI1_SCK；PA6：SPI1_MISO；PA7：SPI1_MOSI。
- PA4 配置为 `ADXL345_CS` GPIO，空闲状态为 HIGH。

### 验收结果

- CubeMX SPI1 配置：通过。
- 工程构建错误数：0。
- 固件下载：通过。
- UART Boot Log：通过。
- PC13 LED 回归测试：通过。
- `ADXL345_CS` 空闲电平 HIGH：通过。

### 范围控制

- 未实现 ADXL345 寄存器协议。
- 未实现 DMA 或中断。
- 未启动 ISSUE-0024。

### 文档同步

- 已同步 Level 1 动态文档。
- EPIC-02 与 Milestone 1 关闭状态仍待 Tech Lead 决策。
- Level 2、Level 3 文档未修改。
