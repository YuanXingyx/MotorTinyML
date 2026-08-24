#ifndef TINY_CLASSIFIER_3CLASS_FINAL_PARAMS_H
#define TINY_CLASSIFIER_3CLASS_FINAL_PARAMS_H
#define TINY3_FINAL_FEATURE_COUNT 21
#define TINY3_FINAL_CLASS_COUNT 3
#ifdef __cplusplus
extern "C" {
#endif
extern const float g_tiny3_final_feature_mean[21];
extern const float g_tiny3_final_feature_std[21];
extern const float g_tiny3_final_logreg_weights[3][21];
extern const float g_tiny3_final_logreg_bias[3];
#ifdef __cplusplus
}
#endif
#endif
