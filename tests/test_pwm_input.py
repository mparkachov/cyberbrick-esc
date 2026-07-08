import unittest

from cyberbrick_esc import config
from cyberbrick_esc import pwm_input


class FakePin:
    IN = 0
    instances = []

    def __init__(self, pin_id, mode):
        self.pin_id = pin_id
        self.mode = mode
        FakePin.instances.append(self)


class FakeClock:
    now_us = 0


class FakePulseReader:
    values = []
    calls = []

    @classmethod
    def read(cls, pin, pulse_level, timeout_us):
        cls.calls.append((pin.pin_id, pulse_level, timeout_us))
        FakeClock.now_us += 20000
        return cls.values.pop(0)


class PwmInputCaptureTest(unittest.TestCase):
    def setUp(self):
        self.old_pin = pwm_input.Pin
        self.old_time_pulse_us = pwm_input.time_pulse_us
        self.old_ticks_us = pwm_input.ticks_us
        FakePin.instances = []
        FakePulseReader.values = []
        FakePulseReader.calls = []
        FakeClock.now_us = 0

        pwm_input.Pin = FakePin
        pwm_input.time_pulse_us = FakePulseReader.read
        pwm_input.ticks_us = self.ticks_us

    def tearDown(self):
        pwm_input.Pin = self.old_pin
        pwm_input.time_pulse_us = self.old_time_pulse_us
        pwm_input.ticks_us = self.old_ticks_us

    def ticks_us(self):
        return FakeClock.now_us

    def capture(self, inputs, *widths):
        FakePulseReader.values.extend(widths)
        samples = None
        for _ in widths:
            samples = inputs.samples()
        return samples

    def test_default_inputs_use_native_capture_without_gpio_irq(self):
        inputs = pwm_input.PwmInput()

        self.assertEqual([pin.pin_id for pin in FakePin.instances], list(config.INPUT_PINS))
        self.assertTrue(all(pin.mode == FakePin.IN for pin in FakePin.instances))
        self.assertTrue(all(not hasattr(pin, "handler") for pin in FakePin.instances))

        samples = self.capture(inputs, 1500, 1501)

        self.assertEqual(
            FakePulseReader.calls,
            [
                (config.INPUT_PINS[0], 1, config.PWM_CAPTURE_TIMEOUT_US),
                (config.INPUT_PINS[1], 1, config.PWM_CAPTURE_TIMEOUT_US),
            ],
        )
        self.assertEqual([sample.pulse_width_us for sample in samples], [1500, 1501])
        self.assertEqual([sample.timestamp_us for sample in samples], [20000, 40000])
        self.assertEqual([sample.last_capture_us for sample in samples], [1500, 1501])
        self.assertEqual([sample.capture_count for sample in samples], [1, 1])
        self.assertEqual([sample.rejected_count for sample in samples], [0, 0])
        self.assertTrue(all(sample.valid for sample in samples))

    def test_samples_capture_one_alternating_channel_per_call(self):
        inputs = pwm_input.PwmInput()

        first = self.capture(inputs, 1500)
        self.assertTrue(first[0].valid)
        self.assertFalse(first[1].valid)

        second = self.capture(inputs, 1500)
        self.assertTrue(second[0].valid)
        self.assertTrue(second[1].valid)

        third = self.capture(inputs, 1600)
        self.assertEqual(FakePulseReader.calls[-1][0], config.INPUT_PINS[0])
        self.assertEqual(third[0].pulse_width_us, 1600)

    def test_invalid_width_and_timeout_preserve_last_valid_sample(self):
        inputs = pwm_input.PwmInput()
        samples = self.capture(inputs, 1500, 1500)
        original_width = samples[0].pulse_width_us
        original_timestamp = samples[0].timestamp_us

        self.capture(inputs, 3000, 1500)
        samples = self.capture(inputs, -2, 1500)

        self.assertEqual(samples[0].pulse_width_us, original_width)
        self.assertEqual(samples[0].timestamp_us, original_timestamp)
        self.assertEqual(samples[0].last_capture_us, -2)
        self.assertEqual(samples[0].rejected_count, 2)
        self.assertTrue(samples[0].valid)

    def test_initial_timeout_does_not_publish_a_sample(self):
        inputs = pwm_input.PwmInput()

        samples = self.capture(inputs, -2)

        self.assertEqual(samples[0].pulse_width_us, 0)
        self.assertEqual(samples[0].timestamp_us, 0)
        self.assertEqual(samples[0].last_capture_us, -2)
        self.assertEqual(samples[0].rejected_count, 1)
        self.assertFalse(samples[0].valid)

    def test_median_filter_rejects_isolated_valid_width_spike(self):
        inputs = pwm_input.PwmInput()
        samples = self.capture(
            inputs,
            1500,
            1500,
            1510,
            1500,
            1490,
            1500,
            1000,
            1500,
        )

        self.assertEqual(samples[0].pulse_width_us, 1490)
        self.assertEqual(samples[0].timestamp_us, 140000)
        self.assertTrue(samples[0].valid)

    def test_median_filter_accepts_persistent_width_change(self):
        inputs = pwm_input.PwmInput()
        samples = self.capture(
            inputs,
            1500,
            1500,
            1500,
            1500,
            1500,
            1500,
            2000,
            1500,
            2000,
            1500,
        )

        self.assertEqual(samples[0].pulse_width_us, 2000)

    def test_sample_objects_are_reused_without_interrupt_snapshot(self):
        inputs = pwm_input.PwmInput()
        first = inputs._samples
        self.capture(inputs, 1500, 1500)
        second = inputs._samples

        self.assertIs(first, second)
        self.assertIs(first[0], inputs._channels[0].current_sample)


if __name__ == "__main__":
    unittest.main()
