import unittest

from cyberbrick_esc import config
from cyberbrick_esc.led import (
    DIRECTION_FORWARD,
    DIRECTION_NEUTRAL,
    DIRECTION_REVERSE,
    state_from_commands,
)
from cyberbrick_esc.safety import Safety, map_pulse_us, normalize_command


def sample(width_us, timestamp_us=0, valid=True):
    return (width_us, timestamp_us, valid)


def confirmed_update(safety, samples, now_us):
    safety.update(samples, now_us)
    return safety.update(
        samples,
        now_us + config.COMMAND_CHANGE_CONFIRM_MS * 1000,
    )


class ObjectSample:
    def __init__(self, pulse_width_us, timestamp_us, valid):
        self.pulse_width_us = pulse_width_us
        self.timestamp_us = timestamp_us
        self.valid = valid


class SafetyMappingTest(unittest.TestCase):
    def test_public_pulse_mapping(self):
        self.assertEqual(map_pulse_us(1000), -1000)
        self.assertEqual(map_pulse_us(1500), 0)
        self.assertEqual(map_pulse_us(2000), 1000)

    def test_deadband_maps_to_neutral(self):
        self.assertEqual(map_pulse_us(config.NEUTRAL_US - config.DEADBAND_US), 0)
        self.assertEqual(map_pulse_us(config.NEUTRAL_US + config.DEADBAND_US), 0)

    def test_endpoint_deadband_maps_to_full_command(self):
        self.assertEqual(
            map_pulse_us(config.MIN_COMMAND_US + config.ENDPOINT_DEADBAND_US),
            config.COMMAND_MIN,
        )
        self.assertEqual(
            map_pulse_us(config.MAX_COMMAND_US - config.ENDPOINT_DEADBAND_US),
            config.COMMAND_MAX,
        )
        self.assertEqual(map_pulse_us(1300), -500)
        self.assertEqual(map_pulse_us(1700), 500)

    def test_command_normalization_snaps_small_and_endpoint_commands(self):
        self.assertEqual(normalize_command(50), 0)
        self.assertEqual(normalize_command(-50), 0)
        self.assertEqual(normalize_command(900), 1000)
        self.assertEqual(normalize_command(-900), -1000)
        self.assertEqual(normalize_command(500), 500)

    def test_invalid_pulse_rejected(self):
        with self.assertRaises(ValueError):
            map_pulse_us(config.MIN_VALID_US - 1)
        with self.assertRaises(ValueError):
            map_pulse_us(config.MAX_VALID_US + 1)
        with self.assertRaises(ValueError):
            map_pulse_us("1500")
        with self.assertRaises(ValueError):
            map_pulse_us(True)

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
        output = confirmed_update(safety, forward, armed_at_us + 1000)
        self.assertTrue(output.armed)
        self.assertGreater(output.commands[0], 0)
        self.assertEqual(output.commands[1], 0)

    def test_command_change_requires_confirmation(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        command_at_us = armed_at_us + 1000
        output = safety.update((sample(2000, command_at_us), sample(1500, command_at_us)), command_at_us)
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [0, 0])

        output = safety.update(
            (sample(2000, command_at_us), sample(1500, command_at_us)),
            command_at_us + config.COMMAND_CHANGE_CONFIRM_MS * 1000,
        )
        self.assertEqual(output.commands, [1000, 0])

    def test_short_command_spike_is_rejected(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        forward_at_us = armed_at_us + 1000
        output = confirmed_update(
            safety,
            (sample(2000, forward_at_us), sample(1500, forward_at_us)),
            forward_at_us,
        )
        self.assertEqual(output.commands, [1000, 0])

        spike_at_us = forward_at_us + config.COMMAND_CHANGE_CONFIRM_MS * 1000 + 1000
        output = safety.update(
            (sample(1000, spike_at_us), sample(1500, spike_at_us)),
            spike_at_us,
        )
        self.assertEqual(output.commands, [1000, 0])

        recovered_at_us = spike_at_us + 20_000
        output = safety.update(
            (sample(2000, recovered_at_us), sample(1500, recovered_at_us)),
            recovered_at_us,
        )
        self.assertEqual(output.commands, [1000, 0])

    def test_startup_requires_valid_neutral_hold_before_arming(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000

        output = safety.update((sample(2000, 0), sample(1500, 0)), 0)
        self.assertFalse(output.armed)
        self.assertFalse(output.failsafe)
        self.assertEqual(output.commands, [0, 0])

        output = safety.update(
            (sample(2000, armed_at_us), sample(1500, armed_at_us)),
            armed_at_us,
        )
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        neutral_start_us = armed_at_us + 1
        output = safety.update(
            (sample(1500, neutral_start_us), sample(1500, neutral_start_us)),
            neutral_start_us,
        )
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        neutral_held_us = neutral_start_us + config.ARMING_TIME_MS * 1000
        output = safety.update(
            (sample(1500, neutral_held_us), sample(1500, neutral_held_us)),
            neutral_held_us,
        )
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [0, 0])

    def test_brief_non_neutral_glitch_does_not_restart_neutral_arming(self):
        safety = Safety()
        arming_time_us = config.ARMING_TIME_MS * 1000
        glitch_at_us = arming_time_us // 2
        grace_recovered_us = glitch_at_us + (config.ARMING_NON_NEUTRAL_GRACE_MS * 1000) // 2

        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        output = safety.update(
            (sample(1600, glitch_at_us), sample(1500, glitch_at_us)),
            glitch_at_us,
        )
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        output = safety.update(
            (sample(1500, grace_recovered_us), sample(1500, grace_recovered_us)),
            grace_recovered_us,
        )
        self.assertFalse(output.armed)
        self.assertTrue(safety.neutral_pending)

        output = safety.update(
            (sample(1500, arming_time_us), sample(1500, arming_time_us)),
            arming_time_us,
        )
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [0, 0])

    def test_persistent_non_neutral_before_arm_restarts_neutral_arming(self):
        safety = Safety()
        arming_time_us = config.ARMING_TIME_MS * 1000
        glitch_at_us = arming_time_us // 2
        persistent_at_us = glitch_at_us + config.ARMING_NON_NEUTRAL_GRACE_MS * 1000 + 1

        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1600, glitch_at_us), sample(1500, glitch_at_us)), glitch_at_us)
        output = safety.update(
            (sample(1600, persistent_at_us), sample(1500, persistent_at_us)),
            persistent_at_us,
        )
        self.assertFalse(output.armed)
        self.assertFalse(safety.neutral_pending)

        output = safety.update(
            (sample(1500, arming_time_us), sample(1500, arming_time_us)),
            arming_time_us,
        )
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        output = safety.update(
            (
                sample(1500, arming_time_us * 2),
                sample(1500, arming_time_us * 2),
            ),
            arming_time_us * 2,
        )
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [0, 0])

    def test_failsafe_requires_neutral_recovery(self):
        safety = Safety()
        neutral = (sample(1500, 0), sample(1500, 0))
        safety.update(neutral, 0)
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        stale_now = armed_at_us + config.INPUT_TIMEOUT_MS * 1000 + 1
        output = safety.update(neutral, stale_now)
        self.assertTrue(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])

        stale_now = stale_now + config.INPUT_LOSS_LATCH_MS * 1000 + 1
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

    def test_short_input_loss_outputs_zero_without_latching_disarm(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        commanded_at_us = armed_at_us + 1000
        output = confirmed_update(
            safety,
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            commanded_at_us,
        )
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [1000, 0])

        stale_at_us = commanded_at_us + config.INPUT_TIMEOUT_MS * 1000 + 1
        output = safety.update(
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            stale_at_us,
        )
        self.assertTrue(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])

        recovered_at_us = stale_at_us + (config.INPUT_LOSS_LATCH_MS * 1000) // 2
        output = confirmed_update(
            safety,
            (sample(2000, recovered_at_us), sample(1500, recovered_at_us)),
            recovered_at_us,
        )
        self.assertTrue(output.armed)
        self.assertFalse(output.failsafe)
        self.assertEqual(output.commands, [1000, 0])
        self.assertEqual(safety.last_latch_reason, "")

    def test_persistent_input_loss_latches_disarm(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        commanded_at_us = armed_at_us + 1000
        safety.update(
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            commanded_at_us,
        )

        stale_at_us = commanded_at_us + config.INPUT_TIMEOUT_MS * 1000 + 1
        safety.update(
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            stale_at_us,
        )

        latch_at_us = stale_at_us + config.INPUT_LOSS_LATCH_MS * 1000 + 1
        output = safety.update(
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            latch_at_us,
        )
        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])
        self.assertEqual(safety.last_latch_reason, "input_loss")

        recovered_non_neutral_us = latch_at_us + 1
        output = safety.update(
            (
                sample(2000, recovered_non_neutral_us),
                sample(1500, recovered_non_neutral_us),
            ),
            recovered_non_neutral_us,
        )
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

    def test_missing_stale_invalid_or_malformed_input_outputs_zero(self):
        arming_time_us = config.ARMING_TIME_MS * 1000
        cases = (
            None,
            (sample(1500, 0),),
            (sample(1500, 0, False), sample(1500, 0)),
            (sample(1500, 0), sample(1500, 0)),
            (sample(config.MAX_VALID_US + 1, arming_time_us, True), sample(1500, arming_time_us)),
            ((1500,), sample(1500, arming_time_us)),
            (sample("1500", arming_time_us), sample(1500, arming_time_us)),
            (sample(1500, arming_time_us, 1), sample(1500, arming_time_us)),
            (None, sample(1500, arming_time_us)),
        )

        for samples in cases:
            with self.subTest(samples=samples):
                safety = Safety()
                output = safety.update(samples, arming_time_us)
                self.assertFalse(output.armed)
                self.assertTrue(output.failsafe)
                self.assertEqual(output.commands, [0, 0])

    def test_bad_input_disarms_and_clears_previous_command(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        safety.update((sample(1500, 0), sample(1500, 0)), 0)
        safety.update((sample(1500, armed_at_us), sample(1500, armed_at_us)), armed_at_us)

        commanded_at_us = armed_at_us + 1000
        output = confirmed_update(
            safety,
            (sample(2000, commanded_at_us), sample(1500, commanded_at_us)),
            commanded_at_us,
        )
        self.assertTrue(output.armed)
        self.assertEqual(output.commands, [1000, 0])

        bad_at_us = commanded_at_us + 1000
        output = safety.update(
            (sample("2000", bad_at_us), sample(1500, bad_at_us)),
            bad_at_us,
        )

        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])
        self.assertEqual(safety.last_latch_reason, "hard_fault")
        self.assertEqual(safety.last_fault_reason, "pulse_width")

    def test_future_sample_timestamp_is_reported_as_hard_fault(self):
        safety = Safety()
        output = safety.update((sample(1500, 100), sample(1500, 100)), 99)

        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])
        self.assertEqual(safety.last_latch_reason, "hard_fault")
        self.assertEqual(safety.last_fault_reason, "future_timestamp")

    def test_unseen_samples_are_input_loss_not_hard_fault(self):
        safety = Safety()
        output = safety.update((sample(0, 0, False), sample(0, 0, False)), 1000)

        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])
        self.assertEqual(safety.last_latch_reason, "")
        self.assertEqual(safety.last_fault_reason, "")

    def test_malformed_valid_flag_is_reported_as_hard_fault(self):
        safety = Safety()
        output = safety.update((sample(1500, 0, 1), sample(1500, 0)), 0)

        self.assertFalse(output.armed)
        self.assertTrue(output.failsafe)
        self.assertEqual(output.commands, [0, 0])
        self.assertEqual(safety.last_latch_reason, "hard_fault")
        self.assertEqual(safety.last_fault_reason, "sample_field")

    def test_object_samples_are_accepted_when_valid_and_fresh(self):
        safety = Safety()
        armed_at_us = config.ARMING_TIME_MS * 1000
        neutral = (
            ObjectSample(1500, 0, True),
            ObjectSample(1500, 0, True),
        )
        output = safety.update(neutral, 0)
        self.assertFalse(output.armed)
        self.assertEqual(output.commands, [0, 0])

        held_neutral = (
            ObjectSample(1500, armed_at_us, True),
            ObjectSample(1500, armed_at_us, True),
        )
        output = safety.update(held_neutral, armed_at_us)
        self.assertTrue(output.armed)
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
