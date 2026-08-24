#ifndef TINY_CLASSIFIER_GOLDEN_DATA_H
#define TINY_CLASSIFIER_GOLDEN_DATA_H

#include <stdint.h>

#define TINY_CLASSIFIER_GOLDEN_CASE_COUNT 4

#ifdef __cplusplus
extern "C" {
#endif

extern const int16_t g_tiny_classifier_golden_raw[4][200][3];
extern const float g_tiny_classifier_golden_features[4][21];
extern const float g_tiny_classifier_golden_scores[4][4];
extern const int g_tiny_classifier_golden_expected_class[4];

#ifdef __cplusplus
}
#endif

#endif /* TINY_CLASSIFIER_GOLDEN_DATA_H */
