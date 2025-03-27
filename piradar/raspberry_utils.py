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