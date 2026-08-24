#ifndef TINY_CLASSIFIER_PARAMS_H
#define TINY_CLASSIFIER_PARAMS_H

#include <stdint.h>

#define TINY_CLASSIFIER_FEATURE_COUNT 21
#define TINY_CLASSIFIER_CLASS_COUNT 4

#ifdef __cplusplus
extern "C" {
#endif

extern const float g_feature_mean[TINY_CLASSIFIER_FEATURE_COUNT];
extern const float g_feature_std[TINY_CLASSIFIER_FEATURE_COUNT];
extern const float g_logreg_weights[TINY_CLASSIFIER_CLASS_COUNT][TINY_CLASSIFIER_FEATURE_COUNT];
extern const float g_logreg_bias[TINY_CLASSIFIER_CLASS_COUNT];

/* Feature order: x/y/z mean, std, rms, min, max, peak_to_peak, mad. */
/* Class order: 0 normal, 1 rotor_unbalance, 2 mechanical_looseness, 3 overload. */

#ifdef __cplusplus
}
#endif

#endif /* TINY_CLASSIFIER_PARAMS_H */
