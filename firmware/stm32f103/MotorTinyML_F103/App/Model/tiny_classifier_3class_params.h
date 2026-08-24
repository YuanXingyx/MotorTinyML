#ifndef TINY_CLASSIFIER_3CLASS_PARAMS_H
#define TINY_CLASSIFIER_3CLASS_PARAMS_H

#define TINY_CLASSIFIER_3CLASS_FEATURE_COUNT 21
#define TINY_CLASSIFIER_3CLASS_CLASS_COUNT 3

#ifdef __cplusplus
extern "C" {
#endif

extern const float g_tiny3_feature_mean[21];
extern const float g_tiny3_feature_std[21];
extern const float g_tiny3_logreg_weights[3][21];
extern const float g_tiny3_logreg_bias[3];

/* Feature order: x/y/z mean, std, rms, min, max, peak_to_peak, mad. */
/* Class order: 0 normal, 1 rotor_unbalance, 2 overload. */

#ifdef __cplusplus
}
#endif

#endif
