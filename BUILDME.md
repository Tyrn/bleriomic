# BlerioMic

A template Bluetooth BLE peripheral on ESP32 and MicroPython

## Misc

- Reference: [1](https://randomnerdtutorials.com/micropython-esp32-bluetooth-low-energy-ble/)

- [I2C LCD MicroPython Libraries](https://microcontrollerslab.com/i2c-lcd-esp32-esp8266-micropython-tutorial/),
  [Source?](https://github.com/Bucknalla/micropython-i2c-lcd)

- [Faking Russian typeset for HD44780, C language](https://github.com/Tyrn/galvanix); look for `*pmru*` source files.

## Workflow with [esptool.py](https://micropython.org/download/ESP32_GENERIC/) and [rshell](https://github.com/dhylands/rshell)

- Erase (here and elsewhere `--port` may or may not be necessary)

```
esptool.py --port /dev/ttyUSB0 erase_flash
```

- Deploy the interpreter

```
esptool.py --baud 460800 write_flash 0x1000 ~/Downloads/bin/ESP32_GENERIC-20241129-v1.24.1.bin
```

- Start `rshell`

```
rshell -p /dev/ttyUSB0
```

- Inside `rshell`; `/pyboard/` means MCU flash memory

```
> ls
src/           README.md      poetry.lock    pyproject.toml
BUILDME.md     micropy.json   poetry.toml
> ls src/
boot.py      i2c_lcd.py   main.py      uuids.py
> cp src/esp32_ble.py src/i2c_lcd.py src/lcd_api.py src/main.py src/nus_kitty.py src/uuids.py /pyboard/
Copying '.../src/esp32_ble.py' to '/pyboard/esp32_ble.py' ...
Copying '.../src/i2c_lcd.py' to '/pyboard/i2c_lcd.py' ...
Copying '.../src/lcd_api.py' to '/pyboard/lcd_api.py' ...
Copying '.../src/main.py' to '/pyboard/main.py' ...
Copying '.../src/nus_kitty.py' to '/pyboard/nus_kitty.py' ...
Copying '.../src/uuids.py' to '/pyboard/uuids.py' ...
> ls /pyboard/
boot.py      i2c_lcd.py   main.py      uuids.py
esp32_ble.py lcd_api.py   nus_kitty.py
>
```

or just

```
> cp src/* /pyboard/
```

- Exit `rshell` with Ctrl+D
