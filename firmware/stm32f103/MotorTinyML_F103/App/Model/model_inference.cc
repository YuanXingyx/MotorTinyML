#include "model_inference.h"

#include "model_config.h"
#include "model_data.h"

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

namespace {

// Deliberately conservative for the STM32F103 SRAM budget. Stage B-1 only
// validates allocation; the final value must be confirmed on target hardware.
constexpr size_t kTensorArenaSize = 16u * 1024u;
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

tflite::MicroInterpreter* interpreter = nullptr;
bool initialized = false;
uint32_t arena_used_bytes = 0;

bool CheckTensorContract(const TfLiteTensor* tensor, TfLiteType type,
                         int expected_dims, const int* expected_shape) {
  if (tensor == nullptr || tensor->type != type || tensor->dims == nullptr ||
      tensor->dims->size != expected_dims) {
    return false;
  }
  for (int i = 0; i < expected_dims; ++i) {
    if (tensor->dims->data[i] != expected_shape[i]) return false;
  }
  return true;
}

}  // namespace

extern "C" bool Model_Init(void) {
  initialized = false;
  arena_used_bytes = 0;

  const tflite::Model* model = tflite::GetModel(g_model);
  if (model == nullptr || model->version() != TFLITE_SCHEMA_VERSION) {
    return false;
  }

  static tflite::MicroMutableOpResolver<7> resolver;
  if (resolver.AddExpandDims() != kTfLiteOk ||
      resolver.AddConv2D() != kTfLiteOk ||
      resolver.AddReshape() != kTfLiteOk ||
      resolver.AddMaxPool2D() != kTfLiteOk ||
      resolver.AddMean() != kTfLiteOk ||
      resolver.AddFullyConnected() != kTfLiteOk ||
      resolver.AddSoftmax() != kTfLiteOk) {
    return false;
  }

  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize);
  interpreter = &static_interpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk) {
    interpreter = nullptr;
    return false;
  }

  constexpr int kInputShape[] = {1, MODEL_WINDOW_SIZE, MODEL_CHANNELS};
  constexpr int kOutputShape[] = {1, MODEL_CLASS_COUNT};
  if (!CheckTensorContract(interpreter->input(0), kTfLiteInt8, 3,
                           kInputShape) ||
      !CheckTensorContract(interpreter->output(0), kTfLiteInt8, 2,
                           kOutputShape)) {
    interpreter = nullptr;
    return false;
  }

  // Allocation succeeded and tensor contracts match. Exact arena usage is
  // reported as zero until a target-specific allocator measurement is added.
  initialized = true;
  return true;
}

extern "C" bool Model_IsInitialized(void) { return initialized; }

extern "C" uint32_t Model_GetTensorArenaUsedBytes(void) {
  return arena_used_bytes;
}
