from machine import Pin, SoftI2C
from time import sleep_ms
from i2c_lcd import I2cLcd
from esp32_ble import Esp32Ble


I2C_ADDR = 0x27
TOTAL_ROWS = 2
TOTAL_COLUMNS = 16


def loop():
    lcd = I2cLcd(
        SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000),
        I2C_ADDR,
        TOTAL_ROWS,
        TOTAL_COLUMNS,
    )
    ble = Esp32Ble("ESP32BLE")
    greeting = "Hola Kitty!"

    while True:
        if ble.is_connected():
            ble.send(greeting)
            lcd.putstr(greeting)
        else:
            lcd.putstr("Advertising...")
        sleep_ms(1500)
        lcd.clear()
        sleep_ms(500)
