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
        period: seconds
        n_pulse: 0 -> infinite.
        """
        if period < 0.004:
            raise ValueError("Pulse must be greater than 0.004")
        _high = int(1e6 * (0.25 * period))
        _low = int(1e6 * (0.75 * period))
        lgpio.tx_pulse(GPIO_CLAIM, self.io_pin, _high, _low, 0, n_pulse)


RADAR_POWER = RaspIoSwitch(6)
GREEN_LED = RaspIoSwitch(13)
BLUE_LED = RaspIoSwitch(19)
RED_LED = RaspIoSwitch(26)