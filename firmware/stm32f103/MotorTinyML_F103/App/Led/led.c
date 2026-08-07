#include "led.h"

void LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct={0};

    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;

    HAL_GPIO_Init(GPIOC,&GPIO_InitStruct);

    LED_Off();
}


void LED_On(void)
{
    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,GPIO_PIN_RESET);
}


void LED_Off(void)
{
    HAL_GPIO_WritePin(GPIOC,GPIO_PIN_13,GPIO_PIN_SET);
}


void LED_Toggle(void)
{
    HAL_GPIO_TogglePin(GPIOC,GPIO_PIN_13);
}
