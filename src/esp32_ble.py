import ubluetooth
from machine import Pin, Timer

import uuids


class Esp32Ble:
    def __init__(self, name: str):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led: Pin = Pin(2, Pin.OUT)
        self.timer1: Timer = Timer(0)

        self._ble_msg: str = ""
        self._is_connected: bool = False
        self.name: str = name
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
        _ = self.led.value(1)
        self.timer1.deinit()

    @staticmethod
    def toggle_led_value(led: Pin):
        current_value = led.value()
        _ = led.value(not current_value)
        _ = led.value(current_value)
        _ = led.value(not current_value)

    def disconnected(self):
        self._is_connected = False
        self.timer1.init(
            period=40,
            mode=Timer.PERIODIC,
            callback=lambda t: self.toggle_led_value(self.led),
        )

    def ble_irq(self, event: int, _):
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
            self._ble_msg = buffer.decode("UTF-8").strip()

    def register(self):
        # Nordic UART Service (NUS)
        ble_nus = ubluetooth.UUID(uuids.Nus.Service)
        ble_rx = (ubluetooth.UUID(uuids.Nus.Rx), ubluetooth.FLAG_WRITE)
        ble_tx = (ubluetooth.UUID(uuids.Nus.Tx), ubluetooth.FLAG_NOTIFY)

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
