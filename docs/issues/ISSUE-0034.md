Goal:
Integrate the validated INT8 TFLite model into STM32F103 firmware using TensorFlow Lite Micro, first with fixed golden-vector validation, then with live ADXL345 windows.

Current validated model:
- INT8 TFLite size: 12,112 bytes
- Input: int8 [1, 200, 3]
- Output: int8 [1, 4]
- Input scale: 0.032843973487615585
- Input zero point: -10
- Output scale: 0.00390625
- Output zero point: -128
- Keras vs INT8 class agreement: 100%
- LORO CV: 99.26% ± 0.60%
- mechanical_looseness recall: ~97%

Existing deployment resources:
- App/Model/model_data.*
- App/Model/model_config.h
- App/Model/model_preprocess.*
- docs/model_deployment_contract.md
- stm32_golden_vectors.txt

Tasks:
1. Complete expected PC INT8 output for golden vectors
2. Integrate TensorFlow Lite Micro runtime
3. Create MicroInterpreter
4. Allocate Tensor Arena
5. Verify input/output tensor contract
6. Run inference on fixed golden vectors
7. Compare STM32 quantized input against PC expected input
8. Compare STM32 INT8 output against PC expected output
9. Verify predicted class parity
10. Only after golden parity passes, connect live ADXL345 200×3 sampling windows
11. Add UART output for class and confidence

Acceptance criteria:
- Golden preprocessing matches PC
- All four golden-vector predicted classes match PC
- No changes to model/data during firmware integration
- Test CSV/data remain frozen
- Live inference is not enabled until golden validation passes