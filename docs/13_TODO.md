# TODO

## Sprint 0 - Day 1

- [x] 创建 `firmware/`
- [x] 创建 `python/`
- [x] 创建 `dataset/`
- [x] 创建 `models/`
- [x] 创建 `docs/`
- [x] 创建 `hardware/`
- [x] 创建 `README.md`
- [x] 创建 `LICENSE`
- [x] 创建 `.gitignore`
- [x] 创建项目管理文档
- [x] 创建工程规范文档
- [x] 检查目录和文件完整性
- [x] 更新开发日志
- [x] 生成 Git Commit Message

## 等待 Tech Lead

- [x] 确认许可证类型（MIT）
- [x] 初始化 Git 仓库
- [x] 配置仓库级 Git 提交者身份并完成第一次提交
- [ ] 提供并批准系统架构
- [ ] 确认 STM32F103 具体型号与开发板
- [ ] 确认传感器、采样要求、数据与模型方案
- [ ] 批准 Sprint 1 范围与验收标准

## Backlog

后续任务由技术负责人确认后添加。

## ISSUE-0009 Codex 工作流完善

- [x] 创建 `docs/05_EnvironmentSetup.md`
- [x] 记录环境安装步骤和软件版本基线
- [x] 创建 `docs/12_DevelopmentWorkflow.md`
- [x] 记录项目开发、Git 提交和每日开发流程
- [x] 在 README 中添加文档入口
- [x] 完成文档验收检查
- [ ] Tech Lead 确认并锁定完整工具链版本
- [x] 配置远程仓库并补充克隆地址

## Sprint 0 最终文档标准化

- [x] 重命名核心文档为编号结构
- [x] 创建 `01_PRD.md`
- [x] 创建 `11_CHANGELOG.md`
- [x] 创建 `14_Milestones.md`
- [x] 创建 `ProjectRules.md`
- [x] 创建 5 个通用模板
- [x] 创建 EPIC-01 至 EPIC-10
- [x] 仅为已有 Issue 创建跟踪文件
- [x] 更新 Dashboard、Roadmap 和 README
- [x] 完成本地链接和文档验证
- [x] 确认未创建或修改 STM32、Python、数据集、模型和硬件文件

## ISSUE-0021 STM32F103 开发环境搭建与验证

- [x] 创建 STM32F103C8T6 STM32CubeIDE 工程
- [x] 完成 Clean Project
- [x] 完成 Build Project
- [x] 使用 ST-Link V2 下载到 MCU
- [x] 完成 MCU 复位运行验证
- [x] 完成 PC13 LED Blink 验证
- [x] 创建 ISSUE-0021 记录
- [x] 同步 Level 1 项目文档
- [ ] Tech Lead 确认是否关闭 EPIC-02
- [ ] Tech Lead 确认是否关闭 Milestone 1

## ISSUE-0025 TB6612 PWM Speed Control

- [x] 配置 TB6612 A 通道控制引脚
- [x] 创建 `App/Motor/motor.c`
- [x] 创建 `App/Motor/motor.h`
- [x] 实现 `Motor_Init()`、`Motor_Start()`、`Motor_Stop()`
- [x] 完成 PWM 速度控制
- [x] 配置 PA8 为 TIM1_CH1
- [x] 验证 TIM1 PWM 生成和频率配置
- [x] 验证 `Motor_Init()` 在 `MX_TIM1_Init()` 后启动 PWM
- [x] 实现并验证 `Motor_SetSpeed()`
- [x] 完成 40%、60%、80% 和 100% 占空比硬件验证
- [x] 完成 0 错误构建和固件下载
- [x] 回归验证 UART Boot Log 和 PC13 LED
- [x] 完成电机启停及周期运行验证
- [x] 创建 ISSUE-0025 记录
- [x] 同步 Level 1 项目文档

## ISSUE-0024 ADXL345 Driver Bring-up

- [ ] 等待 ADXL345 器件到货
- [ ] 器件到货后执行 SPI Device ID 验证

## ISSUE-0023 STM32F103 SPI1 Bring-up

- [x] 配置 SPI1 Master、2 Lines Full Duplex、8 Bits
- [x] 配置 SPI Mode 3（CPOL High、CPHA 2 Edge）
- [x] 配置 Prescaler 32、MSB First、Software NSS
- [x] 配置 PA5 SCK、PA6 MISO、PA7 MOSI
- [x] 配置 PA4 `ADXL345_CS`，空闲状态 HIGH
- [x] 完成 0 错误构建
- [x] 完成固件下载
- [x] 回归验证 UART Boot Log 和 PC13 LED Blink
- [x] 创建 ISSUE-0023 记录
- [x] 同步 Level 1 项目文档
- [ ] Tech Lead 确认是否关闭 EPIC-02
- [ ] Tech Lead 确认是否关闭 Milestone 1

## ISSUE-0022 STM32F103 UART 调试控制台

- [x] 配置 USART1：115200 8-N-1
- [x] 配置 PA9 UART TX
- [x] 完成 USB-TTL 通信验证
- [x] 验证 MCU 复位启动消息
- [x] 回归验证 PC13 LED Blink
- [x] 创建 ISSUE-0022 记录
- [x] 同步 Level 1 项目文档
- [ ] Tech Lead 确认是否关闭 EPIC-02
- [ ] Tech Lead 确认是否关闭 Milestone 1
