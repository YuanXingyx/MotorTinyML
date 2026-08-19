# ISSUE-0028 — Dataset Windowing and Preprocessing Pipeline

## 元数据

- 议题 ID：ISSUE-0028
- 类型：Dataset Processing
- 状态：DONE
- Epic：EPIC-05 — Dataset Processing
- Sprint：Sprint 1
- 负责人：项目工程师
- 创建日期：2026-08-19

## 目标

将 MotorTinyML 原始 ADXL345 CSV 数据转换为固定长度 window，为后续特征工程和模型训练准备统一输入。

## 范围

- 读取并验证标准 raw CSV。
- 检查 timestamp 单调性、采样间隔和估算采样频率。
- 使用 200 samples、1 秒、无重叠的固定窗口。
- 输出可读的 long-format processed CSV 和 metadata TXT。
- 保留明确的 label，不将 `sensor_idle` 自动归类为最终 Normal。

## 交付物

- `python/window_dataset.py`
- `dataset/processed/*_windows.csv`
- `dataset/processed/*_windows_meta.txt`

## Acceptance Criteria

- [x] `window_dataset.py` 创建完成
- [x] 能读取标准 raw CSV 并验证 header
- [x] 完成 timestamp monotonicity 和重复检查
- [x] 输出平均采样间隔和估算采样频率
- [x] 完成 200-sample fixed window
- [x] 使用不重叠窗口
- [x] remainder samples 正确丢弃并报告
- [x] label 正确写入 processed CSV 和 metadata
- [x] processed CSV 输出成功
- [x] metadata TXT 输出成功
- [x] raw CSV 完全不修改
- [x] `motor_normal_60` 的 3001 samples 得到 15 windows
- [x] 错误输入有明确错误信息

## 实际验证记录

验证由用户在本地 Python 虚拟环境中完成：

```text
python python/window_dataset.py dataset/raw/motor_normal_60_20260819_204215.csv --label normal
```

实际输出：

```text
total_samples: 3001
window_size: 200
complete_windows: 15
discarded_samples: 1
shape: (15, 200, 3)
```

生成文件：

- `dataset/processed/motor_normal_60_20260819_204215_windows.csv`
- `dataset/processed/motor_normal_60_20260819_204215_windows_meta.txt`

用户已在本地项目 `.venv` 中成功完成实际验证，并人工检查 processed CSV 和 metadata 内容无异常。Codex 执行环境无法访问原 `.venv` 基础解释器，但不影响用户本地验证结论。

## Out of Scope

- FFT
- 频域特征
- 滤波
- 归一化或标准化策略
- 数据增强
- 重叠窗口
- train/validation/test split
- 神经网络、TensorFlow、TFLite 或 INT8 量化
- 模型训练
- STM32 固件或 CubeMX 配置修改

## 测试计划

```powershell
python python/window_dataset.py `
  dataset/raw/motor_normal_60_20260819_204215.csv `
  --label normal
```

预期：3001 samples、200 window size、15 complete windows、1 discarded sample，逻辑形状为 `15 × 200 × 3`。

## 依赖与风险

- 依赖 ISSUE-0027 已验证的 200 Hz raw CSV。
- 输入数据质量错误必须在生成 processed 数据前报错。
- 原始 CSV 不得被覆盖或修改。

## 状态规则

用户本地验证和人工检查已完成，ISSUE-0028 状态更新为 `DONE`。

## Commit

Pending Git commit
