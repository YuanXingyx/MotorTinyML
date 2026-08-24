#ifndef TINY_CLASSIFIER_3CLASS_AUG_H
#define TINY_CLASSIFIER_3CLASS_AUG_H
#include <stdint.h>
#define TINY3_AUG_WINDOW_SIZE 200
#define TINY3_AUG_CHANNELS 3
#define TINY3_AUG_FEATURE_COUNT 21
#define TINY3_AUG_CLASS_COUNT 3
void TinyClassifier3Aug_ExtractFeatures(const int16_t raw_window[200][3], float features[21]);
int TinyClassifier3Aug_Predict(const float features[21], float scores[3]);
#endif
