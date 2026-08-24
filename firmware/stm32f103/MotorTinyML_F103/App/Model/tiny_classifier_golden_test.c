#include "tiny_classifier_golden_test.h"

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "main.h"
#include "tiny_classifier.h"
#include "tiny_classifier_golden_data.h"

extern UART_HandleTypeDef huart1;

#define GOLDEN_FEATURE_TOLERANCE 1.0e-3f
#define GOLDEN_SCORE_TOLERANCE 1.0e-3f

static void Golden_Print(const char *text)
{
  HAL_UART_Transmit(&huart1, (uint8_t *)text, (uint16_t)strlen(text), HAL_MAX_DELAY);
}

static float Golden_MaxFeatureDiff(const float *actual, const float *expected)
{
  float maximum = 0.0f;
  for (int index = 0; index < TINY_CLASSIFIER_FEATURE_COUNT; ++index) {
    const float difference = fabsf(actual[index] - expected[index]);
    if (difference > maximum) maximum = difference;
  }
  return maximum;
}

static float Golden_MaxScoreDiff(const float *actual, const float *expected)
{
  float maximum = 0.0f;
  for (int index = 0; index < TINY_CLASSIFIER_CLASS_COUNT; ++index) {
    const float difference = fabsf(actual[index] - expected[index]);
    if (difference > maximum) maximum = difference;
  }
  return maximum;
}

void TinyClassifier_GoldenTest_Run(void)
{
  static const char *const class_names[4] = {
    "normal", "rotor_unbalance", "mechanical_looseness", "overload"
  };
  bool all_passed = true;
  char line[160];

  Golden_Print("TINY CLASSIFIER GOLDEN TEST START\r\n");
  for (int test_index = 0; test_index < TINY_CLASSIFIER_GOLDEN_CASE_COUNT; ++test_index) {
    float features[TINY_CLASSIFIER_FEATURE_COUNT];
    float scores[TINY_CLASSIFIER_CLASS_COUNT];
    TinyClassifier_ExtractFeatures(g_tiny_classifier_golden_raw[test_index], features);
    const int predicted_class = TinyClassifier_Predict(features, scores);
    const float feature_diff = Golden_MaxFeatureDiff(
      features, g_tiny_classifier_golden_features[test_index]);
    const float score_diff = Golden_MaxScoreDiff(
      scores, g_tiny_classifier_golden_scores[test_index]);
    const bool passed = predicted_class == g_tiny_classifier_golden_expected_class[test_index]
      && feature_diff <= GOLDEN_FEATURE_TOLERANCE
      && score_diff <= GOLDEN_SCORE_TOLERANCE;
    all_passed = all_passed && passed;

    snprintf(line, sizeof(line),
      "case=%s expected=%d predicted=%d feature_max_diff_x1000=%ld score_max_diff_x1000=%ld %s\r\n",
      class_names[test_index], g_tiny_classifier_golden_expected_class[test_index],
      predicted_class, (long)(feature_diff * 1000.0f + 0.5f),
      (long)(score_diff * 1000.0f + 0.5f),
      passed ? "PASS" : "FAIL");
    Golden_Print(line);
    snprintf(line, sizeof(line), "scores_x1000=[%ld,%ld,%ld,%ld] expected_x1000=[%ld,%ld,%ld,%ld]\r\n",
      (long)(scores[0] * 1000.0f), (long)(scores[1] * 1000.0f),
      (long)(scores[2] * 1000.0f), (long)(scores[3] * 1000.0f),
      (long)(g_tiny_classifier_golden_scores[test_index][0] * 1000.0f),
      (long)(g_tiny_classifier_golden_scores[test_index][1] * 1000.0f),
      (long)(g_tiny_classifier_golden_scores[test_index][2] * 1000.0f),
      (long)(g_tiny_classifier_golden_scores[test_index][3] * 1000.0f));
    Golden_Print(line);
  }
  Golden_Print(all_passed ? "TINY CLASSIFIER GOLDEN TEST PASS\r\n" :
                            "TINY CLASSIFIER GOLDEN TEST FAIL\r\n");
}
