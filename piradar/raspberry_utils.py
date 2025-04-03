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


class RaspIoLED(RaspIoSwitch):

    def __init__(self, io_pin: int):
        super().__init__(io_pin)

    def pulse(self, period=1, n_pulse=0, offset=0):
        """
        period: seconds
        n_pulse: 0 -> infinite.
        """
        if period < 0.004:
            raise ValueError("Pulse must be greater than 0.004")
        _high = int(1e6 * (0.25 * period))
        _low = int(1e6 * (0.75 * period))

        _offset = int(1e6 * offset)

        lgpio.tx_pulse(GPIO_CLAIM, self.io_pin, _high, _low, _offset, n_pulse)

    def stop_pulse(self):
        lgpio.tx_pulse(GPIO_CLAIM, self.io_pin, 1000, 1000, 0, 0)
        lgpio.tx_pulse(GPIO_CLAIM, self.io_pin, 0, 0, 0, 0)


RADAR_POWER = RaspIoSwitch(6)
GREEN_LED = RaspIoSwitch(13)
BLUE_LED = RaspIoSwitch(19)
RED_LED = RaspIoSwitch(26)


def release_gpio():
    lgpio.gpiochip_close(GPIO_CLAIM)