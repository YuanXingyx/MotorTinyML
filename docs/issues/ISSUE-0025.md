# ISSUE-0025 — TB6612 PWM Speed Control

## 元数据

- 议题 ID：ISSUE-0025
- 类型：Hardware Bring-up / Motor Control Infrastructure
- 状态：DONE
- Epic：EPIC-02 STM32F103 Bring-up
- Sprint：Sprint 1
- 负责人：项目工程师
- 完成日期：2026-08-10

## 目标

实现 TB6612 A 通道直流电机的 PWM 速度控制，并验证 STM32F103 与电机驱动器之间的控制链路。

## 实现范围

- PB0：`MOTOR_AIN1`
- PB1：`MOTOR_AIN2`
- PB10：`MOTOR_STBY`
- PA8：`MOTOR_PWMA`
- 电机连接至 TB6612 `AO1/AO2`
- 新增 `App/Motor/motor.c`
- 新增 `App/Motor/motor.h`
- 实现 `Motor_Init()`
- 实现 `Motor_Start()`
- 实现 `Motor_Stop()`
- 实现 PWM 速度控制

## 硬件连接与供电

- TB6612 逻辑电源 VCC：3.3 V
- 电机 VM：外部电机电源
- STM32、TB6612 和外部电源：共地

## 验收结果

- [x] 工程构建成功，错误数为 0
- [x] 固件下载成功
- [x] UART Boot Log 保持正常
- [x] PC13 LED 回归测试通过
- [x] 电机启动成功
- [x] 电机停止成功
- [x] 电机约运行 2 秒、停止 2 秒，重复运行正常
- [x] PWM 速度控制实现并完成硬件验证

## 明确不包含

- 闭环速度控制
- 电流检测
- 过流保护逻辑
- ISSUE-0024 ADXL345 驱动

## 受保护范围

未修改 `python/`、`dataset/`、`models/` 或其他非本 Issue 范围文件。

## 文档同步

Issue 记录创建后，将依据 Documentation Classification Policy 评估 Level 1、Level 2 和 Level 3 文档；在批准前不修改其他文档。

## 提交

Pending Git commit

## 风险

- 电机 VM 电源、电机电流和 TB6612 散热条件尚未进行长期稳定性验证。
- 当前已验证 PWM 速度控制，但尚未实现闭环控制和保护机制。
- ISSUE-0024 ADXL345 器件尚未到货，传感器开发暂不开始。
