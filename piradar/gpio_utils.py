import time

import lgpio

GPIO_CLAIM = lgpio.gpiochip_open(0)


class RaspIoSwitch:
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


def release_gpio():
    lgpio.gpiochip_close(GPIO_CLAIM)


class GPIOController:
    def __init__(self):

        self.red_led = RaspIoLED(26) # Red
        self.blue_led = RaspIoLED(19)  # Blue
        self.green_led = RaspIoLED(13)  # Green
        self.radar_power = RaspIoSwitch(6)

    def program_started_led(self):
        self.led_off()
        self.blue_led.on()
        self.green_led.on()

    def waiting_for_radar_led(self):
        self.led_off()
        self.green_led.on()

    def setting_radar_led(self):
        self.led_off()
        self.green_led.pulse(period=0.25)

    def ready_to_record_led(self):
        self.led_off()
        self.blue_led.on()

    def scan_standby_led(self):
        self.led_off()
        self.blue_led.pulse(period=0.5)

    def is_transmitting_led(self):
        self.led_off()
        self.red_led.on()

    def is_recording_led(self):
        self.led_off()
        self.red_led.pulse(period=0.5)

    def error_pulse_led(self, error_type: str):
        self.led_off()

        match error_type:
            case 'no_radar':
                self.green_led.pulse(period=0.5, n_pulse=10)
                self.blue_led.pulse(period=0.5, n_pulse=10)
            case 'no_eth':
                self.red_led.pulse(period=0.5, n_pulse=10)
                self.green_led.pulse(period=0.5, n_pulse=10)
            case 'no_drive':
                self.red_led.pulse(period=0.5, n_pulse=10)
                self.blue_led.pulse(period=0.5, n_pulse=10)
            case 'no_eth_drive':
                self.red_led.pulse(period=0.6, n_pulse=10, offset=0)
                self.green_led.pulse(period=0.6, n_pulse=10, offset=0.2)
                self.blue_led.pulse(period=0.6, n_pulse=10, offset=0.4)
            case 'fatal':
                self.red_led.pulse(period=0.25, n_pulse=20)
                self.green_led.pulse(period=0.25, n_pulse=20)
                self.blue_led.pulse(period=0.25, n_pulse=20)

    def reboot_radar(self):
        self.radar_power.off()
        time.sleep(1)
        self.radar_power.on()

    def led_off(self):
        for _pin in [self.green_led, self.blue_led, self.red_led]:
            _pin.stop_pulse()
            _pin.off()

    def all_off(self):
        self.led_off()
        self.radar_power.off()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        release_gpio() # maybe not be nescessary but hey.


gpio_controller = GPIOController()
