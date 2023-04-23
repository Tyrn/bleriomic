from machine import Pin, SoftI2C
from machine import Timer
from time import sleep_ms, sleep
import ubluetooth
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# HD44780 is here.

# sdaPIN = Pin(21)  #for ESP32
# sclPIN = Pin(22)

# i2c=SoftI2C(sda=sdaPIN, scl=sclPIN, freq=10000)

# devices = i2c.scan()
# if len(devices) == 0:
#    print("No i2c device !")
# else:
#    print('i2c devices found:',len(devices))
# for device in devices:
#    print("At address: ",hex(device))

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(
    scl=Pin(22), sda=Pin(21), freq=10000
)  # initializing the I2C method for ESP32
# i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)       #initializing the I2C method for ESP8266

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# while True:
#    print("Enter while True")
#    lcd.putstr("I2C LCD Tutorial")
#    print("sleep(2:1)")
#    sleep(2)
#    lcd.clear()
#    lcd.putstr("Lets Count 0-10!")
#    print("sleep(2:2)")
#    sleep(2)
#    lcd.clear()
#    for i in range(11):
#        lcd.putstr(str(i))
#        print("sleep(1)")
#        sleep(1)
#        lcd.clear()

# BLE Hello is here.

ble_msg = ""
is_ble_connected = False


class ESP32_BLE:
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)

        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        global is_ble_connected
        is_ble_connected = True
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        global is_ble_connected
        is_ble_connected = False
        self.timer1.init(
            period=400,
            mode=Timer.PERIODIC,
            callback=lambda t: self.led.value(not self.led.value()),
        )

    def ble_irq(self, event, data):
        global ble_msg

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
            ble_msg = buffer.decode("UTF-8").strip()

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (
            BLE_NUS,
            (
                BLE_TX,
                BLE_RX,
            ),
        )
        SERVICES = (BLE_UART,)
        (
            (
                self.tx,
                self.rx,
            ),
        ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + "\n")

    def advertiser(self):
        name = bytes(self.name, "UTF-8")
        adv_data = bytearray("\x02\x01\x02") + bytearray((len(name) + 1, 0x09)) + name
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


ble = ESP32_BLE("ESP32BLE")
greeting = "Hola Kitty!"

while True:
    if is_ble_connected:
        ble.send(greeting)
        lcd.putstr(greeting)
    else:
        lcd.putstr("Advertising...")
    sleep_ms(1500)
    lcd.clear()
    sleep_ms(500)
