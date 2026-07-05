import unittest

from cyberbrick_esc import config
from cyberbrick_esc.led import (
    DIRECTION_FORWARD,
    DIRECTION_NEUTRAL,
    DIRECTION_REVERSE,
    state_from_commands,
)
from cyberbrick_esc.safety import Safety, map_pulse_us


def sample(width_us, timestamp_us=0, valid=True):
    return (width_us, timestamp_us, valid)


class SafetyMappingTest(unittest.TestCase):
    def test_public_pulse_mapping(self):
        self.assertEqual(map_pulse_us(1000), -1000)
        self.assertEqual(map_pulse_us(1500), 0)
        self.assertEqual(map_pulse_us(2000), 1000)

    def test_deadband_maps_to_neutral(self):
        self.assertEqual(map_pulse_us(config.NEUTRAL_US - config.DEADBAND_US), 0)
        self.assertEqual(map_pulse_us(config.NEUTRAL_US + config.DEADBAND_US), 0)

    def test_invalid_pulse_rejected(self):
        with self.assertRaises(ValueError):
            map_pulse_us(config.MIN_VALID_US - 1)
        with self.assertRaises(ValueError):
            map_pulse_us(config.MAX_VALID_US + 1)

    def test_neutral_before_arm_then_command(self):
        safety = Safety()
        neutral = (sample(1500, 0), sample(1500, 0))
        armed_at_us = config.ARMING_TIME_MS * 1000

        output = safety.update(neutral, 0)
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        output = safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [0, 0])

        forward = (
            sample(1750, armed_at_us + 1000),
            sample(1500, armed_at_us + 1000),
        )
        output = safety.update(forward, armed_at_us + 1000)
        self.assertTrue(output.armed)
        self.assertGreater(output.commands[0], 0)
        self.assertEqual(output.commands[1], 0)

    def test_failsafe_requires_neutral_recovery(self):
        safety = Safety()
        neutral = (sample(1500, 0), sample(1500, 0))
        safety.update(neutral, 0)
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        stale_now = armed_at_us + config.INPUT_TIMEOUT_MS * 1000 + 1
        output = safety.update(neutral, stale_now)
        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])

        non_neutral = (sample(2000, stale_now + 1), sample(1500, stale_now + 1))
        output = safety.update(non_neutral, stale_now + 1)
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        recover_start = stale_now + 2
        fresh_neutral = (sample(1500, recover_start), sample(1500, recover_start))
        safety.update(fresh_neutral, recover_start)
        recovered_at_us = recover_start + config.ARMING_TIME_MS * 1000
        output = safety.update(
            (sample(1500, recovered_at_us), sample(1500, recovered_at_us)),
            recovered_at_us,
        )
        self.assertTrue(output.armed)
        self.assertFalse(output.failsafe)
        self.assertEqual(output.commands, [0, 0])


class LedStateTest(unittest.TestCase):
    def test_led_state_uses_dominant_command(self):
        self.assertEqual(state_from_commands([0, 0])[0], DIRECTION_NEUTRAL)
        self.assertEqual(state_from_commands([250, 0])[0], DIRECTION_FORWARD)
        self.assertEqual(state_from_commands([0, -250])[0], DIRECTION_REVERSE)
        self.assertEqual(state_from_commands([500, -500])[0], DIRECTION_NEUTRAL)
        self.assertEqual(state_from_commands([750, -500])[0], DIRECTION_FORWARD)
        self.assertEqual(state_from_commands([250, -750])[0], DIRECTION_REVERSE)


if __name__ == "__main__":
    unittest.main()
