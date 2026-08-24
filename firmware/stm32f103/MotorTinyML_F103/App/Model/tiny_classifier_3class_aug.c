#include "tiny_classifier_3class_aug.h"
#include "tiny_classifier_3class_aug_params.h"
#include <math.h>
void TinyClassifier3Aug_ExtractFeatures(const int16_t raw_window[200][3], float features[21]) {
  for (int axis = 0; axis < 3; ++axis) {
    float sum = 0.0f, sum_square = 0.0f, variance = 0.0f, mad = 0.0f;
    int16_t minimum = raw_window[0][axis], maximum = minimum;
    for (int sample = 0; sample < 200; ++sample) { float value = (float)raw_window[sample][axis]; sum += value; sum_square += value * value; if (raw_window[sample][axis] < minimum) minimum = raw_window[sample][axis]; if (raw_window[sample][axis] > maximum) maximum = raw_window[sample][axis]; }
    float mean = sum / 200.0f;
    for (int sample = 0; sample < 200; ++sample) { float delta = (float)raw_window[sample][axis] - mean; variance += delta * delta; mad += fabsf(delta); }
    int base = axis * 7; features[base] = mean; features[base + 1] = sqrtf(variance / 200.0f); features[base + 2] = sqrtf(sum_square / 200.0f); features[base + 3] = (float)minimum; features[base + 4] = (float)maximum; features[base + 5] = (float)maximum - (float)minimum; features[base + 6] = mad / 200.0f;
  }
}
int TinyClassifier3Aug_Predict(const float features[21], float scores[3]) { int best = 0; float best_score = -INFINITY; for (int class_index = 0; class_index < 3; ++class_index) { float score = g_tiny3_aug_logreg_bias[class_index]; for (int feature_index = 0; feature_index < 21; ++feature_index) { float scaled = (features[feature_index] - g_tiny3_aug_feature_mean[feature_index]) / g_tiny3_aug_feature_std[feature_index]; score += g_tiny3_aug_logreg_weights[class_index][feature_index] * scaled; } scores[class_index] = score; if (score > best_score) { best_score = score; best = class_index; } } return best; }
