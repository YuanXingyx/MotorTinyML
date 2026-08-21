# MotorTinyML MCU Model Deployment Contract

## Model

- Source: `models/final_model_int8.tflite`
- Input shape: `[1, 200, 3]`
- Input dtype: `int8`
- Output shape: `[1, 4]`
- Output dtype: `int8`
- Model bytes: 12,112

## Normalization and input quantization

The ADXL345 values are the raw integer X/Y/Z values used during training. Do not convert them to g or mg.

```text
normalized_x = (raw_x - mean_x) / std_x
quantized_x = round(normalized_x / input_scale + input_zero_point)
quantized_x = clip(quantized_x, -128, 127)
```

Apply the same operation independently to Y and Z.

```text
mean = [-26.244976043701172, -7.357481479644775, 257.181396484375]
std  = [81.74789428710938, 247.98873901367188, 78.34064483642578]
input_scale = 0.032843973487615585
input_zero_point = -10
```

The reference helper is `firmware/stm32f103/MotorTinyML_F103/App/Model/model_preprocess.c`.

## Tensor layout

The input order is X, Y, Z and the flattened index is:

```text
index = sample_index * 3 + channel
```

The tensor is therefore:

```text
[X0, Y0, Z0, X1, Y1, Z1, ..., X199, Y199, Z199]
```

## Output interpretation

Class order:

```text
0 normal
1 rotor_unbalance
2 mechanical_looseness
3 overload
```

Output quantization:

```text
output_scale = 0.00390625
output_zero_point = -128
float_output = (int8_output - output_zero_point) * output_scale
```

For classification, argmax can be performed directly on the four int8 outputs because they share one scale and zero point. MCU code does not need to convert all outputs to float just to select a class.

## Deployment boundary

This package does not integrate TFLite Micro, configure a tensor arena, modify the main loop, or change ADXL345/PWM logic. The model array, configuration, preprocessing helper and golden vectors are preparation resources only.
