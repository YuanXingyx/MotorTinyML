#ifndef TINY_CLASSIFIER_3CLASS_FINAL_H
#define TINY_CLASSIFIER_3CLASS_FINAL_H
#include <stdint.h>
#define TINY3_FINAL_WINDOW_SIZE 200
#define TINY3_FINAL_CHANNELS 3
#define TINY3_FINAL_FEATURE_COUNT 21
#define TINY3_FINAL_CLASS_COUNT 3
void TinyClassifier3Final_ExtractFeatures(const int16_t raw_window[200][3], float features[21]);
int TinyClassifier3Final_Predict(const float features[21], float scores[3]);
#endif
