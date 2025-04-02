import lgpio

GPIO_CLAIM = lgpio.gpiochip_open(0)


class RaspIoSwitch():
    def __init__(self, io_pin: int):
        self.io_pin = io_pin
        self.is_up = False

        lgpio.gpio_claim_output(GPIO_CLAIM, io_pin)

        self.off()

    def on(self):
        lgpio.gpio_write(GPIO_CLAIM, self.io_pin, 1)
        self.is_up = True

    def off(self):
        lgpio.gpio_write(GPIO_CLAIM, self.io_pin, 0)
        self.is_up = False

    def pulse(self, period=1, n_pulse=0):
        """
        period: milliseconds. High 1/4 of the time.
        n_pulse: 0 -> infinite.
        """
        lgpio.tx_pulse(GPIO_CLAIM, self.io_pin, 0.25*period, 0.75*period, 0, n_pulse)


RADAR_POWER = RaspIoSwitch(6)
GREEN_LED = RaspIoSwitch(13)
BLUE_LED = RaspIoSwitch(19)
RED_LED = RaspIoSwitch(26)