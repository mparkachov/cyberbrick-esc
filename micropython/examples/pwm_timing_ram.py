import sys
from machine import Pin, time_pulse_us
from time import ticks_diff, ticks_ms


PROBE_ID = "cyberbrick-pwm-timing-ram-v2"
INPUT_PINS = (1, 0)
EXPECTED_MIN_US = 900
EXPECTED_MAX_US = 2100
CAPTURE_TIMEOUT_US = 30000
REPORT_INTERVAL_MS = 500
RUN_DURATION_MS = 60000

def measure_full_high_pulse(pin):
    # The first call may begin partway through an already-high pulse. Discard it
    # so the second call starts immediately after a falling edge and measures
    # the next complete pulse in native code.
    synchronization_width_us = time_pulse_us(pin, 1, CAPTURE_TIMEOUT_US)
    if synchronization_width_us < 0:
        return synchronization_width_us
    return time_pulse_us(pin, 1, CAPTURE_TIMEOUT_US)


def update_window(minimums, maximums, index, width_us):
    if width_us < 0:
        return

    if minimums[index] is None or width_us < minimums[index]:
        minimums[index] = width_us
    if maximums[index] is None or width_us > maximums[index]:
        maximums[index] = width_us


def width_text(width_us):
    if width_us == -2:
        return "wait-high-timeout"
    if width_us == -1:
        return "high-pulse-timeout"
    if width_us < EXPECTED_MIN_US or width_us > EXPECTED_MAX_US:
        return "{}us/out-of-range".format(width_us)
    return "{}us/valid".format(width_us)


def range_text(minimum_us, maximum_us):
    if minimum_us is None:
        return "none"
    return "{}-{}us".format(minimum_us, maximum_us)


def print_startup():
    print("PWM TIMING RAM PROBE starting")
    print(
        "probe_id={} active=ram-probe capture=machine.time_pulse_us pins={} timeout_us={} report_ms={} duration_ms={}".format(
            PROBE_ID,
            INPUT_PINS,
            CAPTURE_TIMEOUT_US,
            REPORT_INTERVAL_MS,
            RUN_DURATION_MS,
        )
    )
    print(
        "filesystem=unchanged reset=not-requested led=not-written esc_app=not-running safety=not-running pin_irq=disabled"
    )
    print(
        "The LED keeps its previously latched color; ignore it during this probe."
    )
    print("runtime={}".format(sys.implementation))
    print("The probe stops after 60 seconds; Ctrl-C may also stop it.")


def main():
    pins = tuple(Pin(pin_id, Pin.IN) for pin_id in INPUT_PINS)
    for pin in pins:
        pin.irq(handler=None)

    widths = [-2, -2]
    minimums = [None, None]
    maximums = [None, None]
    sequence = 0
    started_ms = ticks_ms()
    last_report_ms = started_ms

    print_startup()

    try:
        while True:
            for index in range(len(pins)):
                widths[index] = measure_full_high_pulse(pins[index])
                update_window(minimums, maximums, index, widths[index])

            sequence += 1
            now_ms = ticks_ms()
            if ticks_diff(now_ms, started_ms) >= RUN_DURATION_MS:
                print(
                    "PWM TIMING RAM PROBE completed; no reset or filesystem write requested."
                )
                return

            if ticks_diff(now_ms, last_report_ms) < REPORT_INTERVAL_MS:
                continue

            print(
                "PWM timing t_ms={} seq={} ch0={} range0={} ch1={} range1={}".format(
                    ticks_diff(now_ms, started_ms),
                    sequence,
                    width_text(widths[0]),
                    range_text(minimums[0], maximums[0]),
                    width_text(widths[1]),
                    range_text(minimums[1], maximums[1]),
                )
            )
            minimums[0] = None
            minimums[1] = None
            maximums[0] = None
            maximums[1] = None
            last_report_ms = now_ms
    except KeyboardInterrupt:
        print("PWM TIMING RAM PROBE stopped; no reset or filesystem write requested.")


main()
