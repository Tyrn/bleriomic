from machine import Pin, SoftI2C
from machine import Timer
from time import sleep_ms
import ubluetooth
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
TOTAL_ROWS = 2
TOTAL_COLUMNS = 16

SOFT_I2C_LCD = SoftI2C(
    scl=Pin(22), sda=Pin(21), freq=10000
)  # initializing the I2C method for ESP32

LCD = I2cLcd(SOFT_I2C_LCD, I2C_ADDR, TOTAL_ROWS, TOTAL_COLUMNS)

BLE_MSG = ""


class Esp32Ble:
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)

        self._is_connected = False
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def is_connected(self):
        return self._is_connected

    def connected(self):
        self._is_connected = True
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        self._is_connected = False
        self.timer1.init(
            period=400,
            mode=Timer.PERIODIC,
            callback=lambda t: self.led.value(not self.led.value()),
        )

    def ble_irq(self, event, data):
        global BLE_MSG

        if event == 1:  # _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral
            self.connected()

        elif event == 2:  # _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()

        elif event == 3:  # _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            buffer = self.ble.gatts_read(self.rx)
            BLE_MSG = buffer.decode("UTF-8").strip()

    def register(self):
        # Nordic UART Service (NUS)
        nus_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        rx_uuid = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        tx_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

        ble_nus = ubluetooth.UUID(nus_uuid)
        ble_rx = (ubluetooth.UUID(rx_uuid), ubluetooth.FLAG_WRITE)
        ble_tx = (ubluetooth.UUID(tx_uuid), ubluetooth.FLAG_NOTIFY)

        ble_uart = (
            ble_nus,
            (
                ble_tx,
                ble_rx,
            ),
        )
        services = (ble_uart,)
        (
            (
                self.tx,
                self.rx,
            ),
        ) = self.ble.gatts_register_services(services)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + "\n")

    def advertiser(self):
        name = bytes(self.name, "UTF-8")
        adv_data = bytearray(b"\x02\x01\x02") + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
        # adv_data
        # raw: 0x02010209094553503332424C45
        # b'\x02\x01\x02\t\tESP32BLE'
        #
        # 0x02 - General discoverable mode
        # 0x01 - AD Type = 0x01
        # 0x02 - value = 0x02

        # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
        # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics


BLE = Esp32Ble("ESP32BLE")
GREETING = "Hola Kitty!"


def loop():
    while True:
        if BLE.is_connected():
            BLE.send(GREETING)
            LCD.putstr(GREETING)
        else:
            LCD.putstr("Advertising...")
        sleep_ms(1500)
        LCD.clear()
        sleep_ms(500)
