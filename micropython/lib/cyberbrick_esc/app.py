try:
    from time import sleep_ms, ticks_us
except ImportError:
    import time

    def sleep_ms(milliseconds):
        time.sleep(milliseconds / 1000)

    def ticks_us():
        return time.monotonic_ns() // 1000

from cyberbrick_esc import config
from cyberbrick_esc.led import StatusLed
from cyberbrick_esc.pwm_input import PwmInput
from cyberbrick_esc.safety import Safety


def main():
    led = StatusLed()
    inputs = PwmInput()
    safety = Safety()
    sleep_time_ms = control_loop_sleep_ms()

    while True:
        output = safety.update(inputs.samples(), ticks_us())
        led.update(output.commands)
        sleep_ms(sleep_time_ms)


def control_loop_sleep_ms():
    sleep_time_ms = 1000 // config.CONTROL_LOOP_HZ
    return sleep_time_ms if sleep_time_ms > 0 else 1
