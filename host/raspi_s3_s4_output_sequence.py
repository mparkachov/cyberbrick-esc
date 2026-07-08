#!/usr/bin/env python3

import os
import signal
import sys
import time
import argparse
from dataclasses import dataclass


PWMCHIP = "/sys/class/pwm/pwmchip0"

# Default dtoverlay=pwm-2chan mapping:
# pwm0 = GPIO18 = physical pin 12 = CH1 = S3 = Motor 1 input
# pwm1 = GPIO19 = physical pin 35 = CH2 = S4 = Motor 2 input
S3_CHANNEL = 0
S4_CHANNEL = 1

PERIOD_NS = 20_000_000  # 20 ms = 50 Hz RC PWM
ARM_DURATION_SEC = 2.0
ACTIVE_DURATION_SEC = 5.0
NEUTRAL_DURATION_SEC = 1.5

# Keep this in sync with cyberbrick_esc.config.MOTOR_PWM_FULL_COMMAND_DUTY_U16.
OUTPUT_DUTY_U16 = 16_384

running = True


@dataclass(frozen=True)
class Step:
    name: str
    s3_us: int
    s4_us: int
    duration_sec: float


def write(path: str, value: int) -> None:
    with open(path, "w") as handle:
        handle.write(str(value))


def pwm_path(channel: int) -> str:
    return f"{PWMCHIP}/pwm{channel}"


def handle_stop(signum, frame) -> None:
    global running
    running = False


def export_channel(channel: int) -> None:
    path = pwm_path(channel)

    if not os.path.exists(path):
        try:
            write(f"{PWMCHIP}/export", channel)
        except OSError:
            pass

        for _ in range(50):
            if os.path.exists(path):
                break
            time.sleep(0.02)

    if not os.path.exists(path):
        print(f"ERROR: {path} was not created", file=sys.stderr)
        sys.exit(1)


def disable_channel(channel: int) -> None:
    try:
        write(f"{pwm_path(channel)}/enable", 0)
    except OSError:
        pass


def configure_channel(channel: int) -> None:
    path = pwm_path(channel)

    disable_channel(channel)
    write(f"{path}/period", PERIOD_NS)
    write(f"{path}/duty_cycle", 1_500_000)
    write(f"{path}/enable", 1)


def set_channel_us(channel: int, pulse_us: int) -> None:
    write(f"{pwm_path(channel)}/duty_cycle", pulse_us * 1000)


def setup_pwm() -> None:
    for channel in (S3_CHANNEL, S4_CHANNEL):
        export_channel(channel)
        configure_channel(channel)


def pulse_to_command(pulse_us: int) -> int:
    if pulse_us <= 1000:
        return -1000
    if pulse_us >= 2000:
        return 1000
    return 0


def motor_output(command: int, positive_pin: int, negative_pin: int) -> tuple[int, int]:
    if command > 0:
        return OUTPUT_DUTY_U16, 0
    if command < 0:
        return 0, OUTPUT_DUTY_U16
    return 0, 0


def led_name(left_command: int, right_command: int) -> str:
    if left_command == 0 and right_command == 0:
        return "blue neutral"
    if left_command == -right_command and abs(left_command) == abs(right_command):
        return "blue tie"
    if max(left_command, right_command, key=abs) > 0:
        return "green"
    return "red"


def expected_for_step(step: Step) -> tuple[str, str, str]:
    left_command = pulse_to_command(step.s3_us)
    right_command = pulse_to_command(step.s4_us)
    gpio4, gpio5 = motor_output(left_command, 4, 5)
    gpio6, gpio7 = motor_output(right_command, 6, 7)
    command_text = f"cmd={left_command},{right_command}"
    output_text = f"out=m0:a4={gpio4}/b5={gpio5},m1:a6={gpio6}/b7={gpio7}"
    return command_text, output_text, led_name(left_command, right_command)


def run_step(index: int, step: Step, dry_run: bool) -> None:
    command_text, output_text, led_text = expected_for_step(step)

    print()
    print(f"{index:02d}. {step.name}")
    print(f"    S3 = {step.s3_us} us, S4 = {step.s4_us} us")
    print(f"    Expected CyberBrick: {command_text} {output_text} led={led_text}")

    if dry_run:
        return

    set_channel_us(S3_CHANNEL, step.s3_us)
    set_channel_us(S4_CHANNEL, step.s4_us)
    start = time.monotonic()
    while running and time.monotonic() - start < step.duration_sec:
        time.sleep(0.05)


def neutral_step(name: str) -> Step:
    return Step(name, 1500, 1500, NEUTRAL_DURATION_SEC)


def test_sequence() -> tuple[Step, ...]:
    return (
        Step("Arm and verify both motors neutral/off", 1500, 1500, ARM_DURATION_SEC),
        Step("Left motor full forward command; right neutral/off", 2000, 1500, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Left motor full reverse command; right neutral/off", 1000, 1500, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Right motor full forward command; left neutral/off", 1500, 2000, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Right motor full reverse command; left neutral/off", 1500, 1000, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Both motors full forward command", 2000, 2000, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Both motors full reverse command", 1000, 1000, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Pivot left pattern: left reverse, right forward", 1000, 2000, ACTIVE_DURATION_SEC),
        neutral_step("Both motors neutral/off"),
        Step("Pivot right pattern: left forward, right reverse", 2000, 1000, ACTIVE_DURATION_SEC),
    )


def cleanup() -> None:
    print()
    print("Cleanup: setting S3/S4 to neutral, then disabling PWM")

    try:
        set_channel_us(S3_CHANNEL, 1500)
        set_channel_us(S4_CHANNEL, 1500)
        time.sleep(0.3)
        disable_channel(S3_CHANNEL)
        disable_channel(S4_CHANNEL)
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drive Raspberry Pi PWM S3/S4 test sequence for CyberBrick output probing."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the sequence and expected CyberBrick output without touching sysfs PWM",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    print("S3/S4 RC PWM output validation")
    print("CH1: GPIO18 / physical pin 12 -> S3 -> left/Motor 1 -> GPIO4/GPIO5")
    print("CH2: GPIO19 / physical pin 35 -> S4 -> right/Motor 2 -> GPIO6/GPIO7")
    print(f"Expected CyberBrick output duty for full command: {OUTPUT_DUTY_U16}")
    print("GND must be connected first. Motors must stay disconnected.")
    if args.dry_run:
        print("Dry run: not exporting or driving Raspberry Pi PWM.")

    if not args.dry_run:
        setup_pwm()

    try:
        for index, step in enumerate(test_sequence(), start=1):
            if not running:
                break
            run_step(index, step, args.dry_run)

        print()
        print("Test complete.")

    finally:
        if not args.dry_run:
            cleanup()


if __name__ == "__main__":
    main()
