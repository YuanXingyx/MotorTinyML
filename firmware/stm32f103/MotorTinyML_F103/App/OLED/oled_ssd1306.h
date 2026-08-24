#ifndef OLED_SSD1306_H_
#define OLED_SSD1306_H_

#include "stm32f1xx_hal.h"
#include <stdint.h>

HAL_StatusTypeDef OLED_ScanAndInit(uint8_t *address_7bit);
HAL_StatusTypeDef OLED_ShowStatus(uint8_t address_7bit);
HAL_StatusTypeDef OLED_ShowClassification(uint8_t address_7bit, int predicted_class);
HAL_StatusTypeDef OLED_ShowDeviceState(uint8_t address_7bit, int device_state);

#endif /* OLED_SSD1306_H_ */
