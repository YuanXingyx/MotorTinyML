/*
 * adxl345.c
 *
 *  Created on: 2026年8月12日
 *      Author: Administrator
 */

#include "adxl345.h"
#include "main.h"

extern I2C_HandleTypeDef hi2c1;

#define ADXL345_I2C_ADDR      (0x53 << 1)

#define ADXL345_REG_DEVID     0x00
#define ADXL345_REG_POWER_CTL 0x2D
#define ADXL345_REG_DATA_FMT  0x31
#define ADXL345_REG_DATAX0    0x32
#define ADXL345_REG_BW_RATE   0x2C

uint8_t ADXL345_ReadDeviceID(void)
{
    uint8_t devid = 0;

    HAL_I2C_Mem_Read(&hi2c1,
                     ADXL345_I2C_ADDR,
                     ADXL345_REG_DEVID,
                     I2C_MEMADD_SIZE_8BIT,
                     &devid,
                     1,
                     HAL_MAX_DELAY);

    return devid;
}

HAL_StatusTypeDef ADXL345_Init(void)
{
    uint8_t value;

    /* Full Resolution + ±4g */
    value = 0x09;

    if (HAL_I2C_Mem_Write(&hi2c1,
                          ADXL345_I2C_ADDR,
                          ADXL345_REG_DATA_FMT,
                          I2C_MEMADD_SIZE_8BIT,
                          &value,
                          1,
                          HAL_MAX_DELAY) != HAL_OK)
    {
        return HAL_ERROR;
    }

    /* Output Data Rate = 200 Hz */
    value = 0x0B;

    if (HAL_I2C_Mem_Write(&hi2c1,
                          ADXL345_I2C_ADDR,
                          ADXL345_REG_BW_RATE,
                          I2C_MEMADD_SIZE_8BIT,
                          &value,
                          1,
                          HAL_MAX_DELAY) != HAL_OK)
    {
        return HAL_ERROR;
    }

    /* Measurement Mode */
    value = 0x08;

    if (HAL_I2C_Mem_Write(&hi2c1,
                          ADXL345_I2C_ADDR,
                          ADXL345_REG_POWER_CTL,
                          I2C_MEMADD_SIZE_8BIT,
                          &value,
                          1,
                          HAL_MAX_DELAY) != HAL_OK)
    {
        return HAL_ERROR;
    }

    return HAL_OK;
}

HAL_StatusTypeDef ADXL345_ReadXYZ(ADXL345_Data_t *data)
{
    uint8_t buf[6];

    if (HAL_I2C_Mem_Read(&hi2c1,
                         ADXL345_I2C_ADDR,
                         ADXL345_REG_DATAX0,
                         I2C_MEMADD_SIZE_8BIT,
                         buf,
                         6,
                         HAL_MAX_DELAY) != HAL_OK)
    {
        return HAL_ERROR;
    }

    data->x = (int16_t)((buf[1] << 8) | buf[0]);
    data->y = (int16_t)((buf[3] << 8) | buf[2]);
    data->z = (int16_t)((buf[5] << 8) | buf[4]);

    return HAL_OK;
}

//I2C方式通讯读取ADXL345模块ID
/*
#include "adxl345.h"
#include "main.h"

extern I2C_HandleTypeDef hi2c1;

#define ADXL345_I2C_ADDR   (0x53 << 1)
#define ADXL345_DEVID_REG  0x00

uint8_t ADXL345_ReadDeviceID(void)
{
    uint8_t devid = 0x00;

    HAL_I2C_Mem_Read(&hi2c1,
                     ADXL345_I2C_ADDR,
                     ADXL345_DEVID_REG,
                     I2C_MEMADD_SIZE_8BIT,
                     &devid,
                     1,
                     HAL_MAX_DELAY);

    return devid;
}*/

//SPI方式通讯读取ADXL345模块ID
/*
#include "adxl345.h"
#include "main.h"
#include <stdio.h>
#include <string.h>

extern SPI_HandleTypeDef hspi1;
extern UART_HandleTypeDef huart1;

#define ADXL345_DEVID_REG   0x00
#define ADXL345_READ_BIT    0x80


uint8_t ADXL345_ReadDeviceID(void)
{
    uint8_t tx[2] = {0x80, 0x00};
    uint8_t rx[2] = {0x00, 0x00};

    HAL_GPIO_WritePin(ADXL345_CS_GPIO_Port,
                      ADXL345_CS_Pin,
                      GPIO_PIN_RESET);

    HAL_StatusTypeDef status =
        HAL_SPI_TransmitReceive(&hspi1,
                                tx,
                                rx,
                                2,
                                HAL_MAX_DELAY);

    HAL_GPIO_WritePin(ADXL345_CS_GPIO_Port,
                      ADXL345_CS_Pin,
                      GPIO_PIN_SET);

    char msg[64];

    snprintf(msg,
             sizeof(msg),
             "SPI status=%d RX0=0x%02X RX1=0x%02X\r\n",
             status,
             rx[0],
             rx[1]);

    HAL_UART_Transmit(&huart1,
                      (uint8_t *)msg,
                      strlen(msg),
                      HAL_MAX_DELAY);

    return rx[1];
}
*/


