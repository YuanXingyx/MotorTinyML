#ifndef MOTORTINYML_MODEL_INFERENCE_H_
#define MOTORTINYML_MODEL_INFERENCE_H_

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

bool Model_Init(void);
bool Model_IsInitialized(void);
uint32_t Model_GetTensorArenaUsedBytes(void);

#ifdef __cplusplus
}
#endif

#endif  // MOTORTINYML_MODEL_INFERENCE_H_
