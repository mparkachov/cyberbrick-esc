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
        self.assertEqual(config.LED_DATA_PINS, (8, 20, 21))
        self.assertEqual(config.LED_PIXEL_COUNTS, (1, 4, 4))

    def test_default_signal_config(self):
        self.assertEqual(config.MIN_VALID_US, 900)
        self.assertEqual(config.MAX_VALID_US, 2100)
        self.assertEqual(config.MIN_COMMAND_US, 1000)
        self.assertEqual(config.NEUTRAL_US, 1500)
        self.assertEqual(config.MAX_COMMAND_US, 2000)
        self.assertEqual(config.DEADBAND_US, 50)
        self.assertEqual(config.INPUT_TIMEOUT_MS, 150)
        self.assertEqual(config.ARMING_TIME_MS, 1000)
        self.assertEqual(config.CONTROL_LOOP_HZ, 200)
        self.assertEqual(control_loop_sleep_ms(), 5)

    def test_motor_pins_are_not_configured(self):
        configured_pins = set(config.INPUT_PINS)
        configured_pins.update(config.LED_DATA_PINS)
        self.assertTrue(RESERVED_MOTOR_PINS.isdisjoint(configured_pins))

    def test_micro_python_source_does_not_reference_motor_pins(self):
        offenders = []
        for path in MICROPYTHON_ROOT.rglob("*.py"):
            text = path.read_text()
            for pin in RESERVED_MOTOR_PINS:
                if f"Pin({pin}" in text or f"Pin( {pin}" in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: Pin({pin})")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
