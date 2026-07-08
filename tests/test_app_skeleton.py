import unittest
from pathlib import Path

from cyberbrick_esc import config
from cyberbrick_esc.app import control_loop_sleep_ms


REPO_ROOT = Path(__file__).resolve().parents[1]
MICROPYTHON_ROOT = REPO_ROOT / "micropython"
RESERVED_MOTOR_PINS = {4, 5, 6, 7}


class AppSkeletonConfigTest(unittest.TestCase):
    def test_default_pin_config(self):
        self.assertEqual(config.INPUT_PINS, (1, 0))
        self.assertEqual(config.LED_DATA_PINS, (8,))
        self.assertEqual(config.LED_PIXEL_COUNTS, (1,))
        self.assertEqual(config.MOTOR_OUTPUT_PINS, ((4, 5), (6, 7)))

    def test_default_signal_config(self):
        self.assertEqual(config.MIN_VALID_US, 900)
        self.assertEqual(config.MAX_VALID_US, 2100)
        self.assertEqual(config.MIN_COMMAND_US, 1000)
        self.assertEqual(config.NEUTRAL_US, 1500)
        self.assertEqual(config.MAX_COMMAND_US, 2000)
        self.assertEqual(config.DEADBAND_US, 50)
        self.assertEqual(config.ENDPOINT_DEADBAND_US, 150)
        self.assertEqual(config.INPUT_TIMEOUT_MS, 150)
        self.assertEqual(config.INPUT_LOSS_LATCH_MS, 1500)
        self.assertEqual(config.ARMING_TIME_MS, 1000)
        self.assertEqual(config.ARMING_NON_NEUTRAL_GRACE_MS, 300)
        self.assertEqual(config.COMMAND_CHANGE_CONFIRM_MS, 80)
        self.assertEqual(config.COMMAND_NEUTRAL_SNAP, 100)
        self.assertEqual(config.COMMAND_ENDPOINT_SNAP, 900)
        self.assertEqual(config.CONTROL_LOOP_HZ, 50)
        self.assertEqual(config.CONTROL_LOOP_SLEEP_MS, 0)
        self.assertEqual(config.PWM_CAPTURE_TIMEOUT_US, 30000)
        self.assertEqual(config.MOTOR_PWM_HZ, 20000)
        self.assertEqual(config.MOTOR_PWM_MAX_DUTY_U16, 65535)
        self.assertEqual(config.MOTOR_PWM_FULL_COMMAND_DUTY_U16, 16384)
        self.assertEqual(control_loop_sleep_ms(), 0)

    def test_motor_output_pins_are_not_inputs_or_leds(self):
        configured_non_output_pins = set(config.INPUT_PINS)
        configured_non_output_pins.update(config.LED_DATA_PINS)
        output_pins = {pin for pair in config.MOTOR_OUTPUT_PINS for pin in pair}

        self.assertEqual(output_pins, RESERVED_MOTOR_PINS)
        self.assertTrue(RESERVED_MOTOR_PINS.isdisjoint(configured_non_output_pins))

    def test_only_motor_output_module_instantiates_reserved_motor_pins(self):
        offenders = []
        for path in MICROPYTHON_ROOT.rglob("*.py"):
            if path.name == "motor_output.py":
                continue
            text = path.read_text()
            for pin in RESERVED_MOTOR_PINS:
                if f"Pin({pin}" in text or f"Pin( {pin}" in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: Pin({pin})")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
