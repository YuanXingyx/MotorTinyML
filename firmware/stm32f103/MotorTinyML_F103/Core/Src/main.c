/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "led.h"
#include "Delay.h"
#include "motor.h"
#include "adxl345.h"
#include "oled_ssd1306.h"
#include "tiny_classifier_3class_final.h"
#include "tiny_classifier_3class_final_params.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
/* USER CODE END Includes */

/* Set after collecting stopped and running windows; zero keeps the candidate disabled. */
#define MOTION_STOPPED_THRESHOLD_X1000 4000U
#define FINAL_DATA_CAPTURE_MODE 0

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;

UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */

static int16_t inference_window[200][3];
static uint16_t inference_sample_count = 0;
static uint32_t total_windows = 0;
static uint32_t predicted_count[3] = {0, 0, 0};
static int32_t current_prediction = -1;
static int last_predictions[5] = {-1, -1, -1, -1, -1};
static uint8_t prediction_history_count = 0;
static uint8_t prediction_history_index = 0;
static int stable_class = -1;
static int last_displayed_state = -1;
static const char *const tiny_classifier_class_names[3] = {
  "normal", "rotor_unbalance", "overload"
};
static const char *const device_state_names[5] = {
  "STOPPED", "NORMAL", "ROTOR_UNBALANCE", "OVERLOAD", "UNKNOWN"
};

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_TIM1_Init(void);
static void MX_I2C1_Init(void);
static void TinyClassifier3Final_StaticLinkCheck(void);
static void TinyClassifier_PrintFeatureVector(const char *prefix,
                                              const float features[TINY3_FINAL_FEATURE_COUNT]);
static void TinyClassifier_PrintAxisFeatures(const float features[TINY3_FINAL_FEATURE_COUNT]);
volatile uintptr_t g_tiny_classifier_link_check;
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* Keep the Stage C-3 classifier objects in the link without running inference. */
__attribute__((noinline, used)) static void TinyClassifier3Final_StaticLinkCheck(void)
{
  void (*extract_fn)(const int16_t (*)[TINY3_FINAL_CHANNELS],
                     float[TINY3_FINAL_FEATURE_COUNT]) = TinyClassifier3Final_ExtractFeatures;
  int (*predict_fn)(const float[TINY3_FINAL_FEATURE_COUNT],
                    float[TINY3_FINAL_CLASS_COUNT]) = TinyClassifier3Final_Predict;
  g_tiny_classifier_link_check = (uintptr_t)extract_fn ^ (uintptr_t)predict_fn;
}

static void TinyClassifier_PrintFeatureVector(
    const char *prefix,
    const float features[TINY3_FINAL_FEATURE_COUNT])
{
  char line[64];
  int length = snprintf(line, sizeof(line), "%s", prefix);
  HAL_UART_Transmit(&huart1, (uint8_t *)line, (uint16_t)length, HAL_MAX_DELAY);
  for (int index = 0; index < TINY3_FINAL_FEATURE_COUNT; ++index)
  {
    const int32_t scaled = (int32_t)(features[index] * 1000.0f);
    length = snprintf(line, sizeof(line), " f%d=%ld", index, (long)scaled);
    HAL_UART_Transmit(&huart1, (uint8_t *)line, (uint16_t)length, HAL_MAX_DELAY);
  }
  HAL_UART_Transmit(&huart1, (uint8_t *)"\r\n", 2, HAL_MAX_DELAY);
}

static void TinyClassifier_PrintAxisFeatures(
    const float features[TINY3_FINAL_FEATURE_COUNT])
{
  static const char *const axis_names[3] = {"X", "Y", "Z"};
  char line[192];
  for (int axis = 0; axis < 3; ++axis)
  {
    const int base = axis * 7;
    const int length = snprintf(
        line, sizeof(line),
        "[FEATURES_%s] mean=%ld std=%ld rms=%ld min=%ld max=%ld p2p=%ld mad=%ld\r\n",
        axis_names[axis],
        (long)(features[base + 0] * 1000.0f),
        (long)(features[base + 1] * 1000.0f),
        (long)(features[base + 2] * 1000.0f),
        (long)(features[base + 3] * 1000.0f),
        (long)(features[base + 4] * 1000.0f),
        (long)(features[base + 5] * 1000.0f),
        (long)(features[base + 6] * 1000.0f));
    HAL_UART_Transmit(&huart1, (uint8_t *)line, (uint16_t)length, HAL_MAX_DELAY);
  }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  LED_Init();

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_TIM1_Init();
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */

 // Motor_Init();
  char boot_msg[] = "MotorTinyML STM32F103 boot\r\n";
  char msg[192];

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)boot_msg,
                    sizeof(boot_msg) - 1,
                    HAL_MAX_DELAY);

  TinyClassifier3Final_StaticLinkCheck();

  /* 先确认芯片 ID */
  uint8_t devid = ADXL345_ReadDeviceID();

  snprintf(msg,
           sizeof(msg),
           "ADXL345 Device ID = 0x%02X\r\n",
           devid);

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)msg,
                    strlen(msg),
                    HAL_MAX_DELAY);

  /* 再初始化 ADXL345 */
  uint8_t oled_address = 0;
  uint8_t oled_ready = 0;
#if !FINAL_DATA_CAPTURE_MODE
  if (OLED_ScanAndInit(&oled_address) == HAL_OK)
  {
      snprintf(msg, sizeof(msg), "OLED FOUND: 0x%02X\r\n", oled_address);
      HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
      if (OLED_ShowStatus(oled_address) == HAL_OK)
      {
          oled_ready = 1;
          char oled_ok[] = "OLED OK: MotorTinyML status displayed\r\n";
          HAL_UART_Transmit(&huart1, (uint8_t *)oled_ok, sizeof(oled_ok) - 1, HAL_MAX_DELAY);
      }
      else
      {
          char oled_err[] = "OLED ERROR: display write failed\r\n";
          HAL_UART_Transmit(&huart1, (uint8_t *)oled_err, sizeof(oled_err) - 1, HAL_MAX_DELAY);
      }
  }
  else
  {
      char oled_missing[] = "OLED NOT FOUND: tried 0x3C and 0x3D\r\n";
      HAL_UART_Transmit(&huart1, (uint8_t *)oled_missing, sizeof(oled_missing) - 1, HAL_MAX_DELAY);
  }
#else
  HAL_UART_Transmit(&huart1,
                    (uint8_t *)"FINAL_DATA_CAPTURE_MODE: classifier/OLED output disabled\r\n",
                    sizeof("FINAL_DATA_CAPTURE_MODE: classifier/OLED output disabled\r\n") - 1,
                    HAL_MAX_DELAY);
#endif

  uint8_t adxl_ready = 0;
  if (devid != 0xE5)
  {
      char err[] = "ADXL345 ERROR: invalid Device ID, classification disabled\r\n";
      HAL_UART_Transmit(&huart1, (uint8_t *)err, sizeof(err) - 1, HAL_MAX_DELAY);
  }
  else if (ADXL345_Init() != HAL_OK)
  {
      char err[] = "ADXL345 ERROR: init failed, classification disabled\r\n";
      HAL_UART_Transmit(&huart1, (uint8_t *)err, sizeof(err) - 1, HAL_MAX_DELAY);
  }
  else
  {
      adxl_ready = 1;
      char ready[] = "ADXL345 READY: realtime classifier enabled\r\n";
      HAL_UART_Transmit(&huart1, (uint8_t *)ready, sizeof(ready) - 1, HAL_MAX_DELAY);
  }

/*I2C方式扫描模块ID
  char boot_msg[] = "MotorTinyML STM32F103 boot\r\n";

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)boot_msg,
                    sizeof(boot_msg) - 1,
                    HAL_MAX_DELAY);

  char msg[64];

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)"I2C scan start\r\n",
                    strlen("I2C scan start\r\n"),
                    HAL_MAX_DELAY);

  for (uint16_t addr = 1; addr < 128; addr++)
  {
      if (HAL_I2C_IsDeviceReady(&hi2c1,
                                addr << 1,
                                1,
                                10) == HAL_OK)
      {
          snprintf(msg,
                   sizeof(msg),
                   "I2C device found: 0x%02X\r\n",
                   addr);

          HAL_UART_Transmit(&huart1,
                            (uint8_t *)msg,
                            strlen(msg),
                            HAL_MAX_DELAY);
      }
  }

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)"I2C scan done\r\n",
                    strlen("I2C scan done\r\n"),
                    HAL_MAX_DELAY);

*/

  /*SPI方式读取ADXL345的ID
  char boot_msg[] = "MotorTinyML STM32F103 boot\r\n";

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)boot_msg,
                    sizeof(boot_msg) - 1,
                    HAL_MAX_DELAY);

  uint8_t devid = ADXL345_ReadDeviceID();

  char msg[64];

  snprintf(msg,
           sizeof(msg),
           "ADXL345 Device ID = 0x%02X\r\n",
           devid);

  HAL_UART_Transmit(&huart1,
                    (uint8_t *)msg,
                    strlen(msg),
                    HAL_MAX_DELAY);
*/
  Motor_Init();
  Motor_SetSpeed(60);
  Motor_Start();


  ADXL345_Data_t accel;
  uint32_t last_sample = HAL_GetTick();
  uint32_t last_heartbeat = HAL_GetTick();
  uint32_t inference_window_start = 0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

	 uint32_t now = HAL_GetTick();
	 /* 心跳灯：每 500 ms 翻转一次 */
	 if ((now - last_heartbeat) >= 500)
	 {
	     last_heartbeat = now;
	     HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
	 }

	 /* ADXL345 200 Hz 采样 */
	     if ((now - last_sample) >= 5)
	     {
	         last_sample += 5;

         if (adxl_ready && ADXL345_ReadXYZ(&accel) == HAL_OK)
         {
             uint32_t sample_time = HAL_GetTick();

	             snprintf(msg,
	                      sizeof(msg),
	                      "%lu,%d,%d,%d\r\n",
	                      sample_time,
	                      accel.x,
	                      accel.y,
	                      accel.z);

             HAL_UART_Transmit(&huart1,
                               (uint8_t *)msg,
                               strlen(msg),
                               HAL_MAX_DELAY);

             
#if !FINAL_DATA_CAPTURE_MODE
             if (inference_sample_count == 0)
             {
                 inference_window_start = sample_time;
             }
             inference_window[inference_sample_count][0] = accel.x;
             inference_window[inference_sample_count][1] = accel.y;
             inference_window[inference_sample_count][2] = accel.z;
             inference_sample_count++;

             if (inference_sample_count >= 200)
             {
                 float features[TINY3_FINAL_FEATURE_COUNT];
                 float scores[TINY3_FINAL_CLASS_COUNT];
                 uint32_t feature_start = HAL_GetTick();
                 TinyClassifier3Final_ExtractFeatures(inference_window, features);
                 uint32_t feature_extract_ms = HAL_GetTick() - feature_start;
                 const float vibration_metric = sqrtf(
                     (features[1] * features[1] +
                      features[8] * features[8] +
                      features[15] * features[15]) / 3.0f);
                 const int stopped_candidate =
                     ((uint32_t)(vibration_metric * 1000.0f) < MOTION_STOPPED_THRESHOLD_X1000) ? 1 : 0;
                 snprintf(msg, sizeof(msg),
                          "[MOTION] vibration_metric=%ld stopped_candidate=%d\r\n",
                          (long)(vibration_metric * 1000.0f), stopped_candidate);
                 HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
                 float scaled_features[TINY3_FINAL_FEATURE_COUNT];
                 for (int feature_index = 0;
                      feature_index < TINY3_FINAL_FEATURE_COUNT;
                      ++feature_index)
                 {
                     scaled_features[feature_index] =
                         (features[feature_index] - g_tiny3_final_feature_mean[feature_index]) /
                         g_tiny3_final_feature_std[feature_index];
                 }
                 TinyClassifier_PrintFeatureVector("[FEATURES]", features);
                 TinyClassifier_PrintFeatureVector("[SCALED_FEATURES]", scaled_features);
                 TinyClassifier_PrintAxisFeatures(features);
                 uint32_t inference_start = HAL_GetTick();
                 int predicted_class = TinyClassifier3Final_Predict(features, scores);
                 uint32_t inference_ms = HAL_GetTick() - inference_start;
                 uint32_t total_cycle_ms = HAL_GetTick() - inference_window_start;
                 uint32_t window_acquisition_ms = sample_time - inference_window_start;
                 int32_t score0 = (int32_t)(scores[0] * 1000.0f);
                 int32_t score1 = (int32_t)(scores[1] * 1000.0f);
                 int32_t score2 = (int32_t)(scores[2] * 1000.0f);

                 total_windows++;
                 if (predicted_class >= 0 && predicted_class < 3)
                 {
                     predicted_count[predicted_class]++;
                 }
                 current_prediction = predicted_class;

                 snprintf(msg, sizeof(msg),
                          "[CLASS] CLASS=%s ID=%d scores_x1000=[%ld,%ld,%ld]\r\n",
                          tiny_classifier_class_names[predicted_class], predicted_class,
                          (long)score0, (long)score1, (long)score2);
                 HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
                 if (predicted_class >= 0 && predicted_class < 3)
                 {
                     uint32_t votes[3] = {0, 0, 0};
                     last_predictions[prediction_history_index] = predicted_class;
                     prediction_history_index = (uint8_t)((prediction_history_index + 1U) % 5U);
                     if (prediction_history_count < 5U)
                     {
                         prediction_history_count++;
                     }

                     for (uint8_t history_index = 0;
                          history_index < prediction_history_count;
                          ++history_index)
                     {
                         const int history_class = last_predictions[history_index];
                         if (history_class >= 0 && history_class < 3)
                         {
                             votes[history_class]++;
                         }
                     }

                     if (prediction_history_count >= 3U)
                     {
                         for (int vote_class = 0; vote_class < 3; ++vote_class)
                         {
                             if (votes[vote_class] >= 3U)
                             {
                                 stable_class = vote_class;
                                 break;
                             }
                         }
                     }

                     snprintf(msg, sizeof(msg),
                              "[CLASS_VOTE] votes=[%lu,%lu,%lu] stable_class=%d\r\n",
                              (unsigned long)votes[0],
                              (unsigned long)votes[1],
                              (unsigned long)votes[2],
                              stable_class);
                     HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);

                     const int final_state = stopped_candidate ? 0 :
                                             (stable_class >= 0 ? stable_class + 1 : -1);
                     if (oled_ready && final_state >= 0 &&
                         final_state != last_displayed_state)
                     {
                         if (OLED_ShowDeviceState(oled_address, final_state) == HAL_OK)
                         {
                             last_displayed_state = final_state;
                         }
                     }
                     const int report_state = final_state >= 0 && final_state < 4 ? final_state : 4;
                     snprintf(msg, sizeof(msg), "[DEVICE_STATE] state=%s\r\n",
                              device_state_names[report_state]);
                     HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
                 }
                 snprintf(msg, sizeof(msg),
                          "[CLASS_STATS] total_windows=%lu\r\n"
                          "predicted_count=[%lu,%lu,%lu]\r\n"
                          "current_prediction=%ld\r\n",
                          (unsigned long)total_windows,
                          (unsigned long)predicted_count[0],
                          (unsigned long)predicted_count[1],
                          (unsigned long)predicted_count[2],
                          (long)current_prediction);
                 HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
                 snprintf(msg, sizeof(msg),
                          "[CLASS_TIMING] sample_interval_ms=5 window_acquisition_ms=%lu feature_extract_ms=%lu inference_ms=%lu total_cycle_ms=%lu\r\n",
                          (unsigned long)window_acquisition_ms,
                          (unsigned long)feature_extract_ms,
                          (unsigned long)inference_ms,
                          (unsigned long)total_cycle_ms);
                 HAL_UART_Transmit(&huart1, (uint8_t *)msg, strlen(msg), HAL_MAX_DELAY);
                 inference_sample_count = 0;
             }
#endif
         }
         else if (adxl_ready)
         {
	             char err[] = "ADXL345 read error\r\n";

	             HAL_UART_Transmit(&huart1,
	                               (uint8_t *)err,
	                               sizeof(err) - 1,
	                               100);
	         }
	      }

  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 0;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 3599;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(ADXL345_CS_GPIO_Port, ADXL345_CS_Pin, GPIO_PIN_SET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, MOTOR_AIN1_Pin|MOTOR_AIN2_Pin|MOTOR_STBY_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : LED_Pin */
  GPIO_InitStruct.Pin = LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : ADXL345_CS_Pin */
  GPIO_InitStruct.Pin = ADXL345_CS_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(ADXL345_CS_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : MOTOR_AIN1_Pin MOTOR_AIN2_Pin MOTOR_STBY_Pin */
  GPIO_InitStruct.Pin = MOTOR_AIN1_Pin|MOTOR_AIN2_Pin|MOTOR_STBY_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
