# MotorTinyML

## Project Overview

MotorTinyML 是一个基于 STM32F103 与 ADXL345 的离线电机状态识别系统。系统在 MCU 上直接完成振动特征提取和 Logistic Regression 推理，无需 PC 在线参与。

## Final Device States

- STOPPED
- NORMAL
- ROTOR UNBALANCE
- OVERLOAD

## Hardware

- STM32F103C8T6
- ADXL345
- SSD1306-compatible 0.96-inch I2C OLED
- Motor / PWM control hardware

## System Pipeline

```text
ADXL345
  → 200 Hz XYZ sampling
  → 200-point window
  → 21 statistical features
  → StandardScaler
  → Logistic Regression
  → 5-window majority vote
  → OLED state display
```

STOPPED 由独立 vibration threshold 判断，并优先于三分类模型。

## Feature Definition

每个轴使用 7 个特征：mean、population std、RMS、min、max、peak-to-peak、MAD。X/Y/Z 三轴共 21 维。

## Model

最终演示模型为三分类 Logistic Regression：

- 0 normal
- 1 rotor_unbalance
- 2 overload

`mechanical_looseness` 因物理故障模拟可重复性不足而移出最终 demo；历史四分类数据和报告保留。

## Validation

Stage D-4B 使用 CSV-level leave-one-run-out，确保同一 CSV 不跨 train/test：

- Overall accuracy: 99.2593%
- Normal recall: 100%
- Rotor_unbalance recall: 100%
- Overload recall: 97.78%

Confusion matrix:

```text
[[45, 0, 0],
 [0, 45, 0],
 [1, 0, 44]]
```

## PC/C Parity

Python 导出的参数与纯 C 实现进行一致性检查：

- Predicted class agreement: 100%
- PC/C parity: PASS

## Embedded Deployment

- 纯 C inference
- 不依赖 TensorFlow Lite Micro runtime
- 不依赖 C++ runtime
- 不使用 Tensor Arena
- 使用 `libm`
- STM32F103 可独立离线运行

最终 ELF 的可靠 Flash/SRAM 总量需要在 STM32CubeIDE 使用一致工具链 Clean/Rebuild 后确认；当前仓库报告未伪造资源数值。

## OLED Behaviour

```text
STOPPED:             NORMAL:
MotorTinyML          MotorTinyML
MOTOR                RUNNING
STOPPED              NORMAL

ROTOR:               OVERLOAD:
MotorTinyML          MotorTinyML
FAULT                FAULT
ROTOR                OVERLOAD
UNBALANCE
```

## Repository Structure

- `firmware/`：STM32 固件
- `python/`：数据处理、训练和分析工具
- `dataset/raw/`：原始采集数据
- `dataset/reports/`：统计、验证和项目总结报告

## How to Reproduce

```powershell
# 在项目根目录激活虚拟环境
.venv\Scripts\Activate.ps1

# 评估 final-demo 九个 run
python python/evaluate_final_demo_loro.py

# 导出 final-demo 三分类纯 C 参数
python python/export_final_demo_classifier.py
```

随后在 STM32CubeIDE 中执行 Clean Project 和 Build Project，再进行烧录验证。

## Engineering Decisions

项目初始尝试过 TFLite Micro，但 STM32F103 的 Flash/RAM 资源和 runtime 依赖不适合最终部署。最终采用 21 维统计特征加 Logistic Regression，在保留较好 CSV-level 泛化验证结果的同时，显著降低了 Flash、RAM 和运行时依赖。系统通过 golden test、PC/C parity、真实硬件数据和最终 LORO 进行验证。

## Documentation

- [Project Dashboard](docs/00_ProjectDashboard.md)
- [Roadmap](docs/02_Roadmap.md)
- [Environment Setup](docs/05_EnvironmentSetup.md)
- [Development Workflow](docs/12_DevelopmentWorkflow.md)
- [Project Rules](docs/ProjectRules.md)
- [Prompt Library](prompts/)
