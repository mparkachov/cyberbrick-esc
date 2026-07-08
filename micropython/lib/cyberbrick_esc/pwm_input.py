try:
    from machine import Pin, time_pulse_us
    from time import ticks_us
except ImportError:
    Pin = None
    time_pulse_us = None
    ticks_us = None

from cyberbrick_esc import config


class PulseSample:
    __slots__ = (
        "pulse_width_us",
        "timestamp_us",
        "valid",
        "last_capture_us",
        "capture_count",
        "rejected_count",
    )

    def __init__(self, pulse_width_us=0, timestamp_us=0, valid=False):
        self.pulse_width_us = pulse_width_us
        self.timestamp_us = timestamp_us
        self.valid = valid
        self.last_capture_us = 0
        self.capture_count = 0
        self.rejected_count = 0


class PwmInput:
    __slots__ = ("_channels", "_samples", "_next_channel_index")

    def __init__(self, pins=config.INPUT_PINS):
        if Pin is None or time_pulse_us is None:
            raise RuntimeError("machine.Pin and machine.time_pulse_us are required")

        self._channels = tuple(PwmInputChannel(pin_id) for pin_id in pins)
        self._samples = tuple(channel.current_sample for channel in self._channels)
        self._next_channel_index = 0

    def samples(self):
        self._channels[self._next_channel_index].capture()
        self._next_channel_index += 1
        if self._next_channel_index >= len(self._channels):
            self._next_channel_index = 0
        return self._samples


class PwmInputChannel:
    __slots__ = (
        "pin",
        "current_sample",
        "width_0",
        "width_1",
        "width_2",
        "width_count",
        "width_index",
    )

    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.IN)
        self.current_sample = PulseSample()
        self.width_0 = 0
        self.width_1 = 0
        self.width_2 = 0
        self.width_count = 0
        self.width_index = 0

    def capture(self):
        pulse_width_us = time_pulse_us(
            self.pin,
            1,
            config.PWM_CAPTURE_TIMEOUT_US,
        )
        self.current_sample.last_capture_us = pulse_width_us
        self.current_sample.capture_count += 1
        if config.MIN_VALID_US <= pulse_width_us <= config.MAX_VALID_US:
            self._record_valid_width(pulse_width_us, ticks_us())
        else:
            self.current_sample.rejected_count += 1
        return pulse_width_us

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
            filtered_width_us = median3(self.width_0, self.width_1, self.width_2)
        else:
            filtered_width_us = pulse_width_us

        self.current_sample.pulse_width_us = filtered_width_us
        self.current_sample.timestamp_us = timestamp_us
        self.current_sample.valid = True


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
