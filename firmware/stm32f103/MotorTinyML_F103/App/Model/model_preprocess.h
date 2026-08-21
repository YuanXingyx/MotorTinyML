#ifndef MODEL_PREPROCESS_H
#define MODEL_PREPROCESS_H

#include <stdint.h>

#include "model_config.h"

#ifdef __cplusplus
extern "C" {
#endif

int8_t Model_QuantizeAccel(int16_t raw_value, int axis);
void Model_PreprocessWindow(
    const int16_t accel[MODEL_WINDOW_SIZE][MODEL_CHANNELS],
    int8_t output[MODEL_WINDOW_SIZE][MODEL_CHANNELS]);

#ifdef __cplusplus
}
#endif

#endif /* MODEL_PREPROCESS_H */
