try:
    from machine import Pin, disable_irq, enable_irq
    from time import ticks_diff, ticks_us
except ImportError:
    Pin = None
    disable_irq = None
    enable_irq = None
    ticks_us = None

    def ticks_diff(now, then):
        return now - then

from cyberbrick_esc import config


class PulseSample:
    __slots__ = ("pulse_width_us", "timestamp_us", "valid")

    def __init__(self, pulse_width_us=0, timestamp_us=0, valid=False):
        self.pulse_width_us = pulse_width_us
        self.timestamp_us = timestamp_us
        self.valid = valid


class PwmInput:
    def __init__(self, pins=config.INPUT_PINS):
        if Pin is None:
            raise RuntimeError("machine.Pin is required on the target")

        self._channels = tuple(PwmInputChannel(pin_id) for pin_id in pins)

    def samples(self):
        state = disable_irq()
        try:
            return tuple(channel.sample() for channel in self._channels)
        finally:
            enable_irq(state)


class PwmInputChannel:
    __slots__ = (
        "pin",
        "rising_seen",
        "rising_us",
        "pulse_width_us",
        "timestamp_us",
        "valid",
        "width_0",
        "width_1",
        "width_2",
        "width_count",
        "width_index",
    )

    def __init__(self, pin_id):
        self.rising_seen = False
        self.rising_us = 0
        self.pulse_width_us = 0
        self.timestamp_us = 0
        self.valid = False
        self.width_0 = 0
        self.width_1 = 0
        self.width_2 = 0
        self.width_count = 0
        self.width_index = 0
        self.pin = Pin(pin_id, Pin.IN)
        self.pin.irq(
            handler=self._handle_edge,
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
        )

    def sample(self):
        return PulseSample(self.pulse_width_us, self.timestamp_us, self.valid)

    def _handle_edge(self, pin):
        now_us = ticks_us()
        if pin.value():
            self.rising_us = now_us
            self.rising_seen = True
            return

        if not self.rising_seen:
            return

        self.rising_seen = False
        pulse_width_us = ticks_diff(now_us, self.rising_us)
        if config.MIN_VALID_US <= pulse_width_us <= config.MAX_VALID_US:
            self._record_valid_width(pulse_width_us, now_us)

    def _record_valid_width(self, pulse_width_us, timestamp_us):
        if self.width_index == 0:
            self.width_0 = pulse_width_us
        elif self.width_index == 1:
            self.width_1 = pulse_width_us
        else:
            self.width_2 = pulse_width_us

        self.width_index += 1
        if self.width_index >= config.PWM_FILTER_SAMPLES:
            self.width_index = 0

        if self.width_count < config.PWM_FILTER_SAMPLES:
            self.width_count += 1

        if self.width_count >= config.PWM_FILTER_SAMPLES:
            self.pulse_width_us = median3(self.width_0, self.width_1, self.width_2)
        else:
            self.pulse_width_us = pulse_width_us

        self.timestamp_us = timestamp_us
        self.valid = True


def median3(first, second, third):
    if first > second:
        if second > third:
            return second
        if first > third:
            return third
        return first

    if first > third:
        return first
    if second > third:
        return third
    return second
