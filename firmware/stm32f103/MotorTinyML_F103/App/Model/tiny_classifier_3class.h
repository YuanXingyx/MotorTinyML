#ifndef TINY_CLASSIFIER_3CLASS_H_
#define TINY_CLASSIFIER_3CLASS_H_

#include <stdint.h>

#define TINY3_WINDOW_SIZE 200
#define TINY3_CHANNELS 3
#define TINY3_FEATURE_COUNT 21
#define TINY3_CLASS_COUNT 3

void TinyClassifier3_ExtractFeatures(
    const int16_t raw_window[TINY3_WINDOW_SIZE][TINY3_CHANNELS],
    float features[TINY3_FEATURE_COUNT]);

int TinyClassifier3_Predict(
    const float features[TINY3_FEATURE_COUNT],
    float scores[TINY3_CLASS_COUNT]);

#endif /* TINY_CLASSIFIER_3CLASS_H_ */
