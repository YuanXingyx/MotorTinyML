#ifndef TINY_CLASSIFIER_H
#define TINY_CLASSIFIER_H

#include <stdint.h>

#define TINY_CLASSIFIER_WINDOW_SIZE 200
#define TINY_CLASSIFIER_CHANNELS 3
#define TINY_CLASSIFIER_FEATURE_COUNT 21
#define TINY_CLASSIFIER_CLASS_COUNT 4

#ifdef __cplusplus
extern "C" {
#endif

void TinyClassifier_ExtractFeatures(
    const int16_t raw_window[TINY_CLASSIFIER_WINDOW_SIZE][TINY_CLASSIFIER_CHANNELS],
    float features[TINY_CLASSIFIER_FEATURE_COUNT]);

int TinyClassifier_Predict(
    const float features[TINY_CLASSIFIER_FEATURE_COUNT],
    float scores[TINY_CLASSIFIER_CLASS_COUNT]);

#ifdef __cplusplus
}
#endif

#endif /* TINY_CLASSIFIER_H */
