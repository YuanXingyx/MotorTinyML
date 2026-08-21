#include "model_preprocess.h"

#include <math.h>

static float Model_Normalize(int16_t raw_value, int axis)
{
    float mean;
    float std;

    if (axis == 0) {
        mean = NORMALIZATION_MEAN_X;
        std = NORMALIZATION_STD_X;
    } else if (axis == 1) {
        mean = NORMALIZATION_MEAN_Y;
        std = NORMALIZATION_STD_Y;
    } else {
        mean = NORMALIZATION_MEAN_Z;
        std = NORMALIZATION_STD_Z;
    }
    return ((float)raw_value - mean) / std;
}

int8_t Model_QuantizeAccel(int16_t raw_value, int axis)
{
    float normalized = Model_Normalize(raw_value, axis);
    long quantized = lroundf(normalized / MODEL_INPUT_SCALE + MODEL_INPUT_ZERO_POINT);

    if (quantized < -128L) {
        quantized = -128L;
    } else if (quantized > 127L) {
        quantized = 127L;
    }
    return (int8_t)quantized;
}

void Model_PreprocessWindow(
    const int16_t accel[MODEL_WINDOW_SIZE][MODEL_CHANNELS],
    int8_t output[MODEL_WINDOW_SIZE][MODEL_CHANNELS])
{
    for (int sample = 0; sample < MODEL_WINDOW_SIZE; ++sample) {
        for (int channel = 0; channel < MODEL_CHANNELS; ++channel) {
            output[sample][channel] = Model_QuantizeAccel(accel[sample][channel], channel);
        }
    }
}
