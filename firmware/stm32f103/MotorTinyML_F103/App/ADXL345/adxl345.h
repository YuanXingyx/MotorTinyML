/*
 * adxl345.h
 *
 *  Created on: 2026年8月12日
 *      Author: Administrator
 */
#ifndef ADXL345_ADXL345_H_
#define ADXL345_ADXL345_H_

#include "stm32f1xx_hal.h"
#include <stdint.h>

typedef struct
{
    int16_t x;
    int16_t y;
    int16_t z;
} ADXL345_Data_t;

uint8_t ADXL345_ReadDeviceID(void);
HAL_StatusTypeDef ADXL345_Init(void);
HAL_StatusTypeDef ADXL345_ReadXYZ(ADXL345_Data_t *data);

#endif /* ADXL345_ADXL345_H_ */
