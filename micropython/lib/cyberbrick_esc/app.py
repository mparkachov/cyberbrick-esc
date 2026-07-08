try:
    from time import sleep_ms, ticks_diff, ticks_us
except ImportError:
    import time

    def sleep_ms(milliseconds):
        time.sleep(milliseconds / 1000)

    def ticks_diff(now, then):
        return now - then

    def ticks_us():
        return time.monotonic_ns() // 1000

from cyberbrick_esc import config
from cyberbrick_esc.led import StatusLed, rgb_from_commands
from cyberbrick_esc.motor_output import MotorOutputs, output_diagnostic
from cyberbrick_esc.pwm_input import PwmInput
from cyberbrick_esc.safety import (
    Safety,
    map_pulse_us,
    sample_fresh,
    sample_pulse_width_us,
    sample_timestamp_us,
    sample_valid,
)


def main():
    print_startup()
    led = StatusLed()
    inputs = PwmInput()
    safety = Safety()
    outputs = MotorOutputs()
    sleep_time_ms = control_loop_sleep_ms()
    last_diagnostic_us = None

    while True:
        samples = inputs.samples()
        now_us = ticks_us()
        output = safety.update(samples, now_us)
        motor_states = outputs.update(output.commands)
        led.update(output.commands)

        if diagnostic_due(now_us, last_diagnostic_us):
            print_diagnostic(samples, output, safety, motor_states, now_us)
            last_diagnostic_us = now_us

        sleep_ms(sleep_time_ms)


def control_loop_sleep_ms():
    return config.CONTROL_LOOP_SLEEP_MS


def diagnostic_due(now_us, last_diagnostic_us):
    if last_diagnostic_us is None:
        return True
    return ticks_diff(now_us, last_diagnostic_us) >= config.DIAGNOSTIC_INTERVAL_MS * 1000


def print_startup():
    print(
        "ESC simulator starting "
        "inputs={} outputs={} motor_pwm_hz={} motor_full_duty_u16={} led={} capture=time_pulse_us capture_timeout_us={} safety_hz_nominal={} channel_hz_nominal={} loop_sleep_ms={} diag_ms={} valid_us={}-{} neutral_us={} neutral_db_us={} endpoint_db_us={} arm_ms={} arm_grace_ms={} loss_latch_ms={} cmd_confirm_ms={} pwm_filter={}".format(
            config.INPUT_PINS,
            config.MOTOR_OUTPUT_PINS,
            config.MOTOR_PWM_HZ,
            config.MOTOR_PWM_FULL_COMMAND_DUTY_U16,
            config.LED_DATA_PINS,
            config.PWM_CAPTURE_TIMEOUT_US,
            config.CONTROL_LOOP_HZ,
            config.CONTROL_LOOP_HZ // config.CHANNEL_COUNT,
            config.CONTROL_LOOP_SLEEP_MS,
            config.DIAGNOSTIC_INTERVAL_MS,
            config.MIN_VALID_US,
            config.MAX_VALID_US,
            config.NEUTRAL_US,
            config.DEADBAND_US,
            config.ENDPOINT_DEADBAND_US,
            config.ARMING_TIME_MS,
            config.ARMING_NON_NEUTRAL_GRACE_MS,
            config.INPUT_LOSS_LATCH_MS,
            config.COMMAND_CHANGE_CONFIRM_MS,
            config.PWM_FILTER_SAMPLES,
        )
    )


def print_diagnostic(samples, output, safety, motor_states, now_us):
    rgb = rgb_from_commands(output.commands)
    commands = output.commands
    raw = raw_commands_from_samples(samples)
    print(
        "ESC diag t_ms={} reason={} latch={} fault={} armed={} failsafe={} neutral_wait={} neutral_ms={} non_neutral_ms={} loss_ms={} raw={},{} cmd={},{} {} led={},{},{} {},{}".format(
            now_us // 1000,
            diagnostic_reason(samples, output, safety, now_us, raw),
            getattr(safety, "last_latch_reason", ""),
            getattr(safety, "last_fault_reason", ""),
            int(output.armed),
            int(output.failsafe),
            int(getattr(safety, "neutral_pending", False)),
            neutral_pending_ms(safety, now_us),
            non_neutral_pending_ms(safety, now_us),
            input_loss_ms(safety, now_us),
            raw[0],
            raw[1],
            commands[0],
            commands[1],
            output_diagnostic(motor_states),
            rgb[0],
            rgb[1],
            rgb[2],
            channel_diagnostic(samples, 0, now_us),
            channel_diagnostic(samples, 1, now_us),
        )
    )


def neutral_pending_ms(safety, now_us):
    if not getattr(safety, "neutral_pending", False):
        return 0
    try:
        return ticks_diff(now_us, safety.neutral_since_us) // 1000
    except AttributeError:
        return 0


def non_neutral_pending_ms(safety, now_us):
    try:
        non_neutral_since_us = safety.non_neutral_since_us
    except AttributeError:
        return 0

    if not non_neutral_since_us:
        return 0

    return ticks_diff(now_us, non_neutral_since_us) // 1000


def input_loss_ms(safety, now_us):
    try:
        input_loss_since_us = safety.input_loss_since_us
    except AttributeError:
        return 0

    if not input_loss_since_us:
        return 0

    return ticks_diff(now_us, input_loss_since_us) // 1000


def raw_commands_from_samples(samples):
    return (
        raw_command_from_sample(samples, 0),
        raw_command_from_sample(samples, 1),
    )


def raw_command_from_sample(samples, index):
    try:
        sample = samples[index]
    except (TypeError, IndexError, KeyError):
        return "x"

    try:
        return map_pulse_us(sample_pulse_width_us(sample))
    except ValueError:
        return "x"


def diagnostic_reason(samples, output, safety, now_us, raw):
    if output.failsafe and output.armed:
        return "loss_pending"

    if output.armed:
        return "armed"

    if not all_channels_fresh(samples, now_us):
        return "waiting_fresh"

    if raw[0] == config.COMMAND_NEUTRAL and raw[1] == config.COMMAND_NEUTRAL:
        if getattr(safety, "neutral_pending", False):
            return "arming_neutral"
        return "neutral_seen"

    return "need_neutral"


def all_channels_fresh(samples, now_us):
    try:
        if len(samples) != config.CHANNEL_COUNT:
            return False
    except TypeError:
        return False

    for index in range(config.CHANNEL_COUNT):
        try:
            if not sample_fresh(samples[index], now_us):
                return False
        except (TypeError, IndexError, KeyError):
            return False

    return True


def channel_diagnostic(samples, index, now_us):
    try:
        sample = samples[index]
    except (TypeError, IndexError, KeyError):
        return "ch{}=missing".format(index)

    valid = sample_valid(sample)
    fresh = sample_fresh(sample, now_us)

    try:
        pulse_width_us = sample_pulse_width_us(sample)
    except ValueError:
        pulse_width_us = -1

    try:
        age_ms = ticks_diff(now_us, sample_timestamp_us(sample)) // 1000
    except ValueError:
        age_ms = -1

    return "ch{}={}us/v{}/f{}/age{}ms/last{}us/cap{}/rej{}".format(
        index,
        pulse_width_us,
        int(valid),
        int(fresh),
        age_ms,
        getattr(sample, "last_capture_us", -1),
        getattr(sample, "capture_count", -1),
        getattr(sample, "rejected_count", -1),
    )
