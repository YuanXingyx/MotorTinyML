/*
 * motor.c
 *
 *  Created on: 2026年8月10日
 *      Author: Administrator
 */
#include "motor.h"
#include "main.h"

extern TIM_HandleTypeDef htim1;

void Motor_Init(void)
{
    HAL_GPIO_WritePin(MOTOR_STBY_GPIO_Port,
                      MOTOR_STBY_Pin,
                      GPIO_PIN_RESET);

    HAL_GPIO_WritePin(MOTOR_AIN1_GPIO_Port,
                      MOTOR_AIN1_Pin,
                      GPIO_PIN_RESET);

    HAL_GPIO_WritePin(MOTOR_AIN2_GPIO_Port,
                      MOTOR_AIN2_Pin,
                      GPIO_PIN_RESET);

    HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);

    __HAL_TIM_SET_COMPARE(&htim1,
                          TIM_CHANNEL_1,
                          0);
}

void Motor_Start(void)
{
    HAL_GPIO_WritePin(MOTOR_STBY_GPIO_Port,
                      MOTOR_STBY_Pin,
                      GPIO_PIN_SET);

    HAL_GPIO_WritePin(MOTOR_AIN1_GPIO_Port,
                      MOTOR_AIN1_Pin,
                      GPIO_PIN_SET);

    HAL_GPIO_WritePin(MOTOR_AIN2_GPIO_Port,
                      MOTOR_AIN2_Pin,
                      GPIO_PIN_RESET);
}

void Motor_Stop(void)
{
    Motor_SetSpeed(0);

    HAL_GPIO_WritePin(MOTOR_STBY_GPIO_Port,
                      MOTOR_STBY_Pin,
                      GPIO_PIN_RESET);
}

void Motor_SetSpeed(uint8_t percent)
{
    if (percent > 100)
    {
        percent = 100;
    }

    uint32_t arr = __HAL_TIM_GET_AUTORELOAD(&htim1);

    uint32_t compare =
        ((arr + 1) * percent) / 100;

    __HAL_TIM_SET_COMPARE(&htim1,
                          TIM_CHANNEL_1,
                          compare);
}


