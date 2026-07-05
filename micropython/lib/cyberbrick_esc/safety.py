try:
    from time import ticks_diff
except ImportError:
    def ticks_diff(now, then):
        return now - then

from cyberbrick_esc import config


class SafetyOutput:
    __slots__ = ("commands", "armed", "failsafe")

    def __init__(self, commands=None, armed=False, failsafe=False):
        self.commands = commands if commands is not None else [0, 0]
        self.armed = armed
        self.failsafe = failsafe


class Safety:
    __slots__ = ("armed", "failsafe", "neutral_pending", "neutral_since_us")

    def __init__(self):
        self.armed = False
        self.failsafe = False
        self.neutral_pending = False
        self.neutral_since_us = 0

    def update(self, samples, now_us):
        mapped = [0, 0]
        all_fresh = True
        all_neutral = True

        if not sample_count_valid(samples):
            all_fresh = False
        else:
            for idx in range(config.CHANNEL_COUNT):
                try:
                    sample = samples[idx]
                except (TypeError, IndexError, KeyError):
                    all_fresh = False
                    break

                if not sample_fresh(sample, now_us):
                    all_fresh = False
                    break

                try:
                    mapped[idx] = map_pulse_us(sample_pulse_width_us(sample))
                except ValueError:
                    all_fresh = False
                    break

                if mapped[idx] != config.COMMAND_NEUTRAL:
                    all_neutral = False

        if not all_fresh:
            self.armed = False
            self.failsafe = True
            self.neutral_pending = False
            return self._safe_output()

        if not self.armed:
            if all_neutral:
                if not self.neutral_pending:
                    self.neutral_pending = True
                    self.neutral_since_us = now_us

                if ticks_diff(now_us, self.neutral_since_us) >= config.ARMING_TIME_MS * 1000:
                    self.armed = True
                    self.failsafe = False
            else:
                self.neutral_pending = False

            return self._safe_output()

        self.failsafe = False
        self.neutral_pending = False
        return SafetyOutput(mapped, True, False)

    def _safe_output(self):
        return SafetyOutput(
            [config.COMMAND_NEUTRAL, config.COMMAND_NEUTRAL],
            self.armed,
            self.failsafe,
        )


def map_pulse_us(pulse_width_us):
    if not int_value(pulse_width_us):
        raise ValueError("pulse width must be an integer")

    if pulse_width_us < config.MIN_VALID_US or pulse_width_us > config.MAX_VALID_US:
        raise ValueError("pulse outside valid range")

    if pulse_width_us <= config.MIN_COMMAND_US:
        return config.COMMAND_MIN

    if pulse_width_us >= config.MAX_COMMAND_US:
        return config.COMMAND_MAX

    if (
        pulse_width_us >= config.NEUTRAL_US - config.DEADBAND_US
        and pulse_width_us <= config.NEUTRAL_US + config.DEADBAND_US
    ):
        return config.COMMAND_NEUTRAL

    if pulse_width_us < config.NEUTRAL_US:
        span_us = config.NEUTRAL_US - config.MIN_COMMAND_US
        delta_us = config.NEUTRAL_US - pulse_width_us
        mapped = -(((delta_us * config.COMMAND_MAX) + (span_us // 2)) // span_us)
    else:
        span_us = config.MAX_COMMAND_US - config.NEUTRAL_US
        delta_us = pulse_width_us - config.NEUTRAL_US
        mapped = ((delta_us * config.COMMAND_MAX) + (span_us // 2)) // span_us

    return clamp_command(mapped)


def clamp_command(command):
    if command > config.COMMAND_MAX:
        return config.COMMAND_MAX
    if command < config.COMMAND_MIN:
        return config.COMMAND_MIN
    return command


def sample_fresh(sample, now_us):
    if not sample_valid(sample):
        return False

    try:
        age_us = ticks_diff(now_us, sample_timestamp_us(sample))
    except (TypeError, ValueError):
        return False

    return age_us >= 0 and age_us <= config.INPUT_TIMEOUT_MS * 1000


def sample_pulse_width_us(sample):
    return sample_int_field(sample, "pulse_width_us", 0)


def sample_timestamp_us(sample):
    return sample_int_field(sample, "timestamp_us", 1)


def sample_valid(sample):
    try:
        return sample_field(sample, "valid", 2) is True
    except ValueError:
        return False


def sample_count_valid(samples):
    try:
        return len(samples) == config.CHANNEL_COUNT
    except TypeError:
        return False


def sample_int_field(sample, attr, index):
    value = sample_field(sample, attr, index)
    if not int_value(value):
        raise ValueError("sample field must be an integer")
    return value


def sample_field(sample, attr, index):
    if sample is None:
        raise ValueError("sample is missing")

    if hasattr(sample, attr):
        return getattr(sample, attr)

    try:
        return sample[index]
    except (TypeError, IndexError, KeyError):
        raise ValueError("sample field is missing")


def int_value(value):
    return isinstance(value, int) and not isinstance(value, bool)
