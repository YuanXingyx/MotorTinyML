/*
 * motor.c
 *
 *  Created on: 2026年8月10日
 *      Author: Administrator
 */
#include "motor.h"
#include "main.h"

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

    HAL_GPIO_WritePin(MOTOR_PWMA_GPIO_Port,
                      MOTOR_PWMA_Pin,
                      GPIO_PIN_RESET);
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

    HAL_GPIO_WritePin(MOTOR_PWMA_GPIO_Port,
                      MOTOR_PWMA_Pin,
                      GPIO_PIN_SET);
}

void Motor_Stop(void)
{
    HAL_GPIO_WritePin(MOTOR_PWMA_GPIO_Port,
                      MOTOR_PWMA_Pin,
                      GPIO_PIN_RESET);
}


