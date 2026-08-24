#include "tiny_classifier_3class.h"

#include <math.h>

#include "tiny_classifier_3class_params.h"

void TinyClassifier3_ExtractFeatures(
    const int16_t raw_window[TINY3_WINDOW_SIZE][TINY3_CHANNELS],
    float features[TINY3_FEATURE_COUNT])
{
    for (int axis = 0; axis < TINY3_CHANNELS; ++axis)
    {
        float sum = 0.0f;
        float sum_square = 0.0f;
        int16_t minimum = raw_window[0][axis];
        int16_t maximum = raw_window[0][axis];
        for (int sample = 0; sample < TINY3_WINDOW_SIZE; ++sample)
        {
            const float value = (float)raw_window[sample][axis];
            sum += value;
            sum_square += value * value;
            if (raw_window[sample][axis] < minimum) minimum = raw_window[sample][axis];
            if (raw_window[sample][axis] > maximum) maximum = raw_window[sample][axis];
        }
        const float mean = sum / (float)TINY3_WINDOW_SIZE;
        float variance_sum = 0.0f;
        float mad_sum = 0.0f;
        for (int sample = 0; sample < TINY3_WINDOW_SIZE; ++sample)
        {
            const float delta = (float)raw_window[sample][axis] - mean;
            variance_sum += delta * delta;
            mad_sum += fabsf(delta);
        }
        const int base = axis * 7;
        features[base + 0] = mean;
        features[base + 1] = sqrtf(variance_sum / (float)TINY3_WINDOW_SIZE);
        features[base + 2] = sqrtf(sum_square / (float)TINY3_WINDOW_SIZE);
        features[base + 3] = (float)minimum;
        features[base + 4] = (float)maximum;
        features[base + 5] = (float)maximum - (float)minimum;
        features[base + 6] = mad_sum / (float)TINY3_WINDOW_SIZE;
    }
}

int TinyClassifier3_Predict(
    const float features[TINY3_FEATURE_COUNT],
    float scores[TINY3_CLASS_COUNT])
{
    int best_class = 0;
    float best_score = -INFINITY;
    for (int class_index = 0; class_index < TINY3_CLASS_COUNT; ++class_index)
    {
        float score = g_tiny3_logreg_bias[class_index];
        for (int feature_index = 0; feature_index < TINY3_FEATURE_COUNT; ++feature_index)
        {
            const float scaled = (features[feature_index] - g_tiny3_feature_mean[feature_index]) /
                                 g_tiny3_feature_std[feature_index];
            score += g_tiny3_logreg_weights[class_index][feature_index] * scaled;
        }
        scores[class_index] = score;
        if (score > best_score)
        {
            best_score = score;
            best_class = class_index;
        }
    }
    return best_class;
}
