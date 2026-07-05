import inspect
import unittest

from cyberbrick_esc import config
from cyberbrick_esc import pwm_input


class FakePin:
    IN = 0
    IRQ_RISING = 1
    IRQ_FALLING = 2

    instances = []

    def __init__(self, pin_id, mode):
        self.pin_id = pin_id
        self.mode = mode
        self.handler = None
        self.trigger = None
        self._value = 0
        FakePin.instances.append(self)

    def irq(self, handler, trigger):
        self.handler = handler
        self.trigger = trigger

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class FakeClock:
    now_us = 0


class PwmInputCaptureTest(unittest.TestCase):
    def setUp(self):
        self.old_pin = pwm_input.Pin
        self.old_disable_irq = pwm_input.disable_irq
        self.old_enable_irq = pwm_input.enable_irq
        self.old_ticks_us = pwm_input.ticks_us
        self.irq_calls = []
        FakePin.instances = []
        FakeClock.now_us = 0

        pwm_input.Pin = FakePin
        pwm_input.disable_irq = self.disable_irq
        pwm_input.enable_irq = self.enable_irq
        pwm_input.ticks_us = self.ticks_us

    def tearDown(self):
        pwm_input.Pin = self.old_pin
        pwm_input.disable_irq = self.old_disable_irq
        pwm_input.enable_irq = self.old_enable_irq
        pwm_input.ticks_us = self.old_ticks_us

    def disable_irq(self):
        self.irq_calls.append("disable")
        return "irq-state"

    def enable_irq(self, state):
        self.irq_calls.append(("enable", state))

    def ticks_us(self):
        return FakeClock.now_us

    def trigger_edge(self, pin, value, timestamp_us):
        FakeClock.now_us = timestamp_us
        pin.set_value(value)
        pin.handler(pin)

    def test_default_inputs_capture_both_edges_on_both_channels(self):
        inputs = pwm_input.PwmInput()

        self.assertEqual([pin.pin_id for pin in FakePin.instances], list(config.INPUT_PINS))
        for pin in FakePin.instances:
            self.assertEqual(pin.mode, FakePin.IN)
            self.assertEqual(pin.trigger, FakePin.IRQ_RISING | FakePin.IRQ_FALLING)
            self.assertIsNotNone(pin.handler)

        self.trigger_edge(FakePin.instances[0], 1, 1000)
        self.trigger_edge(FakePin.instances[0], 0, 2500)
        self.trigger_edge(FakePin.instances[1], 1, 3000)
        self.trigger_edge(FakePin.instances[1], 0, 4500)

        samples = inputs.samples()
        self.assertEqual([sample.pulse_width_us for sample in samples], [1500, 1500])
        self.assertEqual([sample.timestamp_us for sample in samples], [2500, 4500])
        self.assertTrue(all(sample.valid for sample in samples))

    def test_invalid_width_does_not_replace_last_valid_sample(self):
        inputs = pwm_input.PwmInput()
        pin = FakePin.instances[0]

        self.trigger_edge(pin, 1, 1000)
        self.trigger_edge(pin, 0, 2500)
        valid_sample = inputs.samples()[0]
        self.assertEqual(valid_sample.pulse_width_us, 1500)
        self.assertEqual(valid_sample.timestamp_us, 2500)
        self.assertTrue(valid_sample.valid)

        self.trigger_edge(pin, 1, 4000)
        self.trigger_edge(pin, 0, 4700)
        sample_after_invalid = inputs.samples()[0]

        self.assertEqual(sample_after_invalid.pulse_width_us, 1500)
        self.assertEqual(sample_after_invalid.timestamp_us, 2500)
        self.assertTrue(sample_after_invalid.valid)

    def test_falling_edge_without_rising_edge_is_ignored(self):
        inputs = pwm_input.PwmInput()
        self.trigger_edge(FakePin.instances[0], 0, 2500)

        sample = inputs.samples()[0]
        self.assertEqual(sample.pulse_width_us, 0)
        self.assertEqual(sample.timestamp_us, 0)
        self.assertFalse(sample.valid)

    def test_samples_are_copied_with_interrupts_disabled(self):
        inputs = pwm_input.PwmInput()
        self.trigger_edge(FakePin.instances[0], 1, 1000)
        self.trigger_edge(FakePin.instances[0], 0, 2500)

        samples = inputs.samples()

        self.assertEqual(self.irq_calls[-2:], ["disable", ("enable", "irq-state")])
        self.assertIsInstance(samples[0], pwm_input.PulseSample)
        self.assertIsNot(samples[0], inputs._channels[0])

    def test_irq_handler_remains_short_and_non_printing(self):
        source = inspect.getsource(pwm_input.PwmInputChannel._handle_edge)

        self.assertNotIn("print", source)
        self.assertNotIn("PulseSample", source)
        self.assertNotIn("[", source)
        self.assertNotIn("{", source)
