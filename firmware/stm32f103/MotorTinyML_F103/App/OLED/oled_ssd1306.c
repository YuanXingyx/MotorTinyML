#include "oled_ssd1306.h"

#include "main.h"
#include <string.h>

extern I2C_HandleTypeDef hi2c1;

#define OLED_WIDTH 128U
#define OLED_HEIGHT_PAGES 8U
#define OLED_CONTROL_COMMAND 0x00U
#define OLED_CONTROL_DATA 0x40U

static HAL_StatusTypeDef oled_command(uint8_t address, uint8_t command)
{
    uint8_t packet[2] = {OLED_CONTROL_COMMAND, command};
    return HAL_I2C_Master_Transmit(&hi2c1, (uint16_t)(address << 1), packet, 2, 20);
}

static HAL_StatusTypeDef oled_commands(uint8_t address, const uint8_t *commands, uint16_t count)
{
    for (uint16_t index = 0; index < count; ++index)
    {
        if (oled_command(address, commands[index]) != HAL_OK)
        {
            return HAL_ERROR;
        }
    }
    return HAL_OK;
}

static const uint8_t *glyph(char character)
{
    static const uint8_t blank[5] = {0, 0, 0, 0, 0};
    static const uint8_t M[5] = {0x7F, 0x02, 0x0C, 0x02, 0x7F};
    static const uint8_t O[5] = {0x3E, 0x41, 0x41, 0x41, 0x3E};
    static const uint8_t L[5] = {0x7F, 0x40, 0x40, 0x40, 0x40};
    static const uint8_t E[5] = {0x7F, 0x49, 0x49, 0x49, 0x41};
    static const uint8_t D[5] = {0x7F, 0x41, 0x41, 0x22, 0x1C};
    static const uint8_t K[5] = {0x7F, 0x08, 0x14, 0x22, 0x41};
    static const uint8_t T[5] = {0x01, 0x01, 0x7F, 0x01, 0x01};
    static const uint8_t S[5] = {0x46, 0x49, 0x49, 0x49, 0x31};
    static const uint8_t F[5] = {0x7F, 0x09, 0x09, 0x01, 0x01};
    static const uint8_t A[5] = {0x7E, 0x11, 0x11, 0x11, 0x7E};
    static const uint8_t U[5] = {0x3F, 0x40, 0x40, 0x40, 0x3F};
    static const uint8_t R[5] = {0x7F, 0x09, 0x19, 0x29, 0x46};
    static const uint8_t B[5] = {0x7F, 0x49, 0x49, 0x49, 0x36};
    static const uint8_t N[5] = {0x7F, 0x06, 0x18, 0x60, 0x7F};
    static const uint8_t C[5] = {0x3E, 0x41, 0x41, 0x41, 0x22};
    static const uint8_t P[5] = {0x7F, 0x09, 0x09, 0x09, 0x06};
    static const uint8_t G[5] = {0x3E, 0x41, 0x49, 0x49, 0x7A};
    static const uint8_t I[5] = {0x00, 0x41, 0x7F, 0x41, 0x00};
    static const uint8_t a[5] = {0x20, 0x54, 0x54, 0x54, 0x78};
    static const uint8_t e[5] = {0x38, 0x54, 0x54, 0x54, 0x18};
    static const uint8_t p[5] = {0x7C, 0x14, 0x14, 0x14, 0x08};
    static const uint8_t d[5] = {0x08, 0x14, 0x14, 0x18, 0x7C};
    static const uint8_t u[5] = {0x3C, 0x40, 0x40, 0x20, 0x7C};
    static const uint8_t s[5] = {0x48, 0x54, 0x54, 0x54, 0x24};
    static const uint8_t colon[5] = {0, 0x36, 0x36, 0, 0};
    static const uint8_t percent[5] = {0x62, 0x64, 0x08, 0x13, 0x23};
    static const uint8_t digit0[5] = {0x3E, 0x45, 0x49, 0x51, 0x3E};
    static const uint8_t digit6[5] = {0x3E, 0x49, 0x49, 0x49, 0x30};
    static const uint8_t o[5] = {0x38, 0x44, 0x44, 0x44, 0x38};
    static const uint8_t t[5] = {0x04, 0x3F, 0x44, 0x40, 0x20};
    static const uint8_t r[5] = {0x7C, 0x08, 0x04, 0x04, 0x08};
    static const uint8_t i[5] = {0, 0x44, 0x7D, 0x40, 0};
    static const uint8_t n[5] = {0x7C, 0x08, 0x04, 0x04, 0x78};
    static const uint8_t y[5] = {0x0C, 0x50, 0x50, 0x50, 0x3C};

    switch (character)
    {
    case 'M': return M;
    case 'O': return O;
    case 'L': return L;
    case 'E': return E;
    case 'D': return D;
    case 'K': return K;
    case 'T': return T;
    case 'S': return S;
    case 'F': return F;
    case 'A': return A;
    case 'U': return U;
    case 'R': return R;
    case 'B': return B;
    case 'N': return N;
    case 'C': return C;
    case 'P': return P;
    case 'G': return G;
    case 'I': return I;
    case 'o': return o;
    case 't': return t;
    case 'r': return r;
    case 'i': return i;
    case 'n': return n;
    case 'y': return y;
    case 'a': return a;
    case 'e': return e;
    case 'p': return p;
    case 'd': return d;
    case 'u': return u;
    case 's': return s;
    case ':': return colon;
    case '%': return percent;
    case '0': return digit0;
    case '6': return digit6;
    default: return blank;
    }
}

static HAL_StatusTypeDef oled_write_text(uint8_t address, uint8_t page, const char *text)
{
    if (oled_command(address, (uint8_t)(0xB0U | page)) != HAL_OK ||
        oled_command(address, 0x00U) != HAL_OK ||
        oled_command(address, 0x10U) != HAL_OK)
    {
        return HAL_ERROR;
    }

    for (const char *cursor = text; *cursor != '\0'; ++cursor)
    {
        uint8_t packet[6] = {OLED_CONTROL_DATA, 0, 0, 0, 0, 0};
        memcpy(&packet[1], glyph(*cursor), 5);
        if (HAL_I2C_Master_Transmit(&hi2c1, (uint16_t)(address << 1), packet, sizeof(packet), 20) != HAL_OK)
        {
            return HAL_ERROR;
        }
    }
    return HAL_OK;
}

static HAL_StatusTypeDef oled_clear(uint8_t address)
{
    uint8_t clear_packet[17] = {OLED_CONTROL_DATA};
    for (uint8_t page = 0; page < OLED_HEIGHT_PAGES; ++page)
    {
        if (oled_command(address, (uint8_t)(0xB0U | page)) != HAL_OK ||
            oled_command(address, 0x00U) != HAL_OK ||
            oled_command(address, 0x10U) != HAL_OK)
        {
            return HAL_ERROR;
        }
        for (uint16_t column = 0; column < OLED_WIDTH; column += 16U)
        {
            if (HAL_I2C_Master_Transmit(&hi2c1, (uint16_t)(address << 1), clear_packet, sizeof(clear_packet), 20) != HAL_OK)
            {
                return HAL_ERROR;
            }
        }
    }
    return HAL_OK;
}

HAL_StatusTypeDef OLED_ScanAndInit(uint8_t *address_7bit)
{
    static const uint8_t candidates[] = {0x3CU, 0x3DU};
    uint8_t found = 0;
    for (uint32_t index = 0; index < sizeof(candidates); ++index)
    {
        if (HAL_I2C_IsDeviceReady(&hi2c1, (uint16_t)(candidates[index] << 1), 2, 20) == HAL_OK)
        {
            found = candidates[index];
            break;
        }
    }
    if (found == 0U)
    {
        return HAL_ERROR;
    }

    static const uint8_t init_sequence[] = {
        0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
        0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12,
        0x81, 0x7F, 0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6, 0xAF
    };
    if (oled_commands(found, init_sequence, sizeof(init_sequence)) != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (address_7bit != NULL)
    {
        *address_7bit = found;
    }
    return HAL_OK;
}

HAL_StatusTypeDef OLED_ShowStatus(uint8_t address_7bit)
{
    if (oled_clear(address_7bit) != HAL_OK) return HAL_ERROR;
    return oled_write_text(address_7bit, 1, "MotorTinyML") == HAL_OK &&
           oled_write_text(address_7bit, 4, "OLED OK") == HAL_OK ? HAL_OK : HAL_ERROR;
}

HAL_StatusTypeDef OLED_ShowClassification(uint8_t address_7bit, int predicted_class)
{
    if (predicted_class < 0 || predicted_class > 2 || oled_clear(address_7bit) != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (oled_write_text(address_7bit, 0, "MotorTinyML") != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (predicted_class == 0)
    {
        return (oled_write_text(address_7bit, 2, "Speed 60%") == HAL_OK &&
                oled_write_text(address_7bit, 4, "NORMAL") == HAL_OK) ? HAL_OK : HAL_ERROR;
    }
    if (oled_write_text(address_7bit, 2, "FAULT") != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (predicted_class == 1)
    {
        return (oled_write_text(address_7bit, 3, "ROTOR") == HAL_OK &&
                oled_write_text(address_7bit, 4, "UNBALANCE") == HAL_OK) ? HAL_OK : HAL_ERROR;
    }
    return oled_write_text(address_7bit, 4, "OVERLOAD") == HAL_OK ? HAL_OK : HAL_ERROR;
}

/* device_state: 0 STOPPED, 1 NORMAL, 2 ROTOR_UNBALANCE, 3 OVERLOAD */
HAL_StatusTypeDef OLED_ShowDeviceState(uint8_t address_7bit, int device_state)
{
    const char *line2 = "RUNNING";
    const char *line3 = "NORMAL";
    const char *line4 = NULL;
    if (device_state == 0)
    {
        line2 = "MOTOR";
        line3 = "STOPPED";
    }
    else if (device_state == 2)
    {
        line3 = "FAULT";
        line4 = "ROTOR";
    }
    else if (device_state == 3)
    {
        line3 = "FAULT";
        line4 = "OVERLOAD";
    }
    else if (device_state != 1)
    {
        return HAL_ERROR;
    }
    if (oled_clear(address_7bit) != HAL_OK ||
        oled_write_text(address_7bit, 0, "MotorTinyML") != HAL_OK ||
        oled_write_text(address_7bit, 2, line2) != HAL_OK ||
        oled_write_text(address_7bit, 4, line3) != HAL_OK)
    {
        return HAL_ERROR;
    }
    if (line4 != NULL && oled_write_text(address_7bit, 5, line4) != HAL_OK)
    {
        return HAL_ERROR;
    }
    return HAL_OK;
}
