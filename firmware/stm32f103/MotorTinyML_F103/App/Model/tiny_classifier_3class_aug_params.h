#ifndef TINY_CLASSIFIER_3CLASS_AUG_PARAMS_H
#define TINY_CLASSIFIER_3CLASS_AUG_PARAMS_H
#define TINY3_AUG_FEATURE_COUNT 21
#define TINY3_AUG_CLASS_COUNT 3
#ifdef __cplusplus
extern "C" {
#endif
extern const float g_tiny3_aug_feature_mean[21];
extern const float g_tiny3_aug_feature_std[21];
extern const float g_tiny3_aug_logreg_weights[3][21];
extern const float g_tiny3_aug_logreg_bias[3];
#ifdef __cplusplus
}
#endif
#endif
