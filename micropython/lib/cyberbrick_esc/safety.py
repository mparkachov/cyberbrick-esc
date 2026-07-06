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
    __slots__ = (
        "armed",
        "failsafe",
        "neutral_pending",
        "neutral_since_us",
        "non_neutral_since_us",
        "input_loss_since_us",
        "last_latch_reason",
        "last_fault_reason",
        "released_commands",
        "pending_commands",
        "pending_since_us",
    )

    def __init__(self):
        self.armed = False
        self.failsafe = False
        self.neutral_pending = False
        self.neutral_since_us = 0
        self.non_neutral_since_us = 0
        self.input_loss_since_us = 0
        self.last_latch_reason = ""
        self.last_fault_reason = ""
        self.released_commands = [config.COMMAND_NEUTRAL, config.COMMAND_NEUTRAL]
        self.pending_commands = [config.COMMAND_NEUTRAL, config.COMMAND_NEUTRAL]
        self.pending_since_us = [0, 0]

    def update(self, samples, now_us):
        mapped = [0, 0]
        all_fresh = True
        all_neutral = True
        fault_reason = ""

        if not sample_count_valid(samples):
            fault_reason = "sample_count"
        else:
            for idx in range(config.CHANNEL_COUNT):
                try:
                    sample = samples[idx]
                except (TypeError, IndexError, KeyError):
                    fault_reason = "sample_missing"
                    break

                try:
                    if not sample_valid_flag(sample):
                        all_fresh = False
                        break

                    age_us = ticks_diff(now_us, sample_timestamp_us(sample))
                except (TypeError, ValueError):
                    fault_reason = "sample_field"
                    break

                if age_us < 0:
                    fault_reason = "future_timestamp"
                    break

                if age_us > config.INPUT_TIMEOUT_MS * 1000:
                    all_fresh = False
                    break

                try:
                    mapped[idx] = map_pulse_us(sample_pulse_width_us(sample))
                except ValueError:
                    fault_reason = "pulse_width"
                    break

                if mapped[idx] != config.COMMAND_NEUTRAL:
                    all_neutral = False

        if fault_reason:
            self.armed = False
            self.failsafe = True
            self.neutral_pending = False
            self.non_neutral_since_us = 0
            self.input_loss_since_us = 0
            self.last_latch_reason = "hard_fault"
            self.last_fault_reason = fault_reason
            self._reset_released_commands()
            return self._safe_output()

        if not all_fresh:
            return self._handle_input_loss(now_us)

        self.input_loss_since_us = 0

        if not self.armed:
            if all_neutral:
                if not self.neutral_pending:
                    self.neutral_pending = True
                    self.neutral_since_us = now_us
                self.non_neutral_since_us = 0

                if ticks_diff(now_us, self.neutral_since_us) >= config.ARMING_TIME_MS * 1000:
                    self.armed = True
                    self.failsafe = False
                    self.last_latch_reason = ""
                    self.last_fault_reason = ""
            else:
                self._handle_non_neutral_before_arm(now_us)

            self._reset_released_commands()
            return self._safe_output()

        self.failsafe = False
        self.neutral_pending = False
        self.non_neutral_since_us = 0
        return SafetyOutput(self._stable_commands(mapped, now_us), True, False)

    def _handle_input_loss(self, now_us):
        self.failsafe = True
        self.neutral_pending = False
        self.non_neutral_since_us = 0

        if not self.armed:
            self.input_loss_since_us = 0
            self._reset_released_commands()
            return self._safe_output()

        if self.input_loss_since_us == 0:
            self.input_loss_since_us = now_us

        if ticks_diff(now_us, self.input_loss_since_us) > config.INPUT_LOSS_LATCH_MS * 1000:
            self.armed = False
            self.input_loss_since_us = 0
            self.last_latch_reason = "input_loss"

        self._reset_released_commands()
        return self._safe_output()

    def _handle_non_neutral_before_arm(self, now_us):
        if not self.neutral_pending:
            return

        if self.non_neutral_since_us == 0:
            self.non_neutral_since_us = now_us
            return

        if ticks_diff(now_us, self.non_neutral_since_us) <= (
            config.ARMING_NON_NEUTRAL_GRACE_MS * 1000
        ):
            return

        self.neutral_pending = False
        self.non_neutral_since_us = 0

    def _stable_commands(self, mapped, now_us):
        return [
            self._stable_command(0, normalize_command(mapped[0]), now_us),
            self._stable_command(1, normalize_command(mapped[1]), now_us),
        ]

    def _stable_command(self, index, command, now_us):
        if command == self.released_commands[index]:
            self.pending_since_us[index] = 0
            self.pending_commands[index] = command
            return command

        if command != self.pending_commands[index]:
            self.pending_commands[index] = command
            self.pending_since_us[index] = now_us
            return self.released_commands[index]

        if self.pending_since_us[index] == 0:
            self.pending_since_us[index] = now_us
            return self.released_commands[index]

        if ticks_diff(now_us, self.pending_since_us[index]) < (
            config.COMMAND_CHANGE_CONFIRM_MS * 1000
        ):
            return self.released_commands[index]

        self.released_commands[index] = command
        self.pending_since_us[index] = 0
        return command

    def _reset_released_commands(self):
        for index in range(config.CHANNEL_COUNT):
            self.released_commands[index] = config.COMMAND_NEUTRAL
            self.pending_commands[index] = config.COMMAND_NEUTRAL
            self.pending_since_us[index] = 0

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

    min_full_command_us = config.MIN_COMMAND_US + config.ENDPOINT_DEADBAND_US
    max_full_command_us = config.MAX_COMMAND_US - config.ENDPOINT_DEADBAND_US
    neutral_low_us = config.NEUTRAL_US - config.DEADBAND_US
    neutral_high_us = config.NEUTRAL_US + config.DEADBAND_US

    if pulse_width_us <= min_full_command_us:
        return config.COMMAND_MIN

    if pulse_width_us >= max_full_command_us:
        return config.COMMAND_MAX

    if pulse_width_us >= neutral_low_us and pulse_width_us <= neutral_high_us:
        return config.COMMAND_NEUTRAL

    if pulse_width_us < config.NEUTRAL_US:
        span_us = neutral_low_us - min_full_command_us
        delta_us = neutral_low_us - pulse_width_us
        mapped = -(((delta_us * config.COMMAND_MAX) + (span_us // 2)) // span_us)
    else:
        span_us = max_full_command_us - neutral_high_us
        delta_us = pulse_width_us - neutral_high_us
        mapped = ((delta_us * config.COMMAND_MAX) + (span_us // 2)) // span_us

    return clamp_command(mapped)


def clamp_command(command):
    if command > config.COMMAND_MAX:
        return config.COMMAND_MAX
    if command < config.COMMAND_MIN:
        return config.COMMAND_MIN
    return command


def normalize_command(command):
    if command >= config.COMMAND_ENDPOINT_SNAP:
        return config.COMMAND_MAX
    if command <= -config.COMMAND_ENDPOINT_SNAP:
        return config.COMMAND_MIN
    if -config.COMMAND_NEUTRAL_SNAP <= command <= config.COMMAND_NEUTRAL_SNAP:
        return config.COMMAND_NEUTRAL
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
        return sample_valid_flag(sample) is True
    except ValueError:
        return False


def sample_valid_flag(sample):
    value = sample_field(sample, "valid", 2)
    if not isinstance(value, bool):
        raise ValueError("sample valid field must be a boolean")
    return value


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
