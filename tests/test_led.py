import inspect
import unittest

from cyberbrick_esc import config
from cyberbrick_esc import app
from cyberbrick_esc import pixels
from cyberbrick_esc.led import (
    DIRECTION_FORWARD,
    DIRECTION_NEUTRAL,
    DIRECTION_REVERSE,
    StatusLed,
    active_brightness_from_command,
    rgb_from_commands,
    state_from_commands,
)


class FakePixelBus:
    instances = []

    def __init__(self, pin_id, count):
        self.pin_id = pin_id
        self.count = count
        self.colors = []
        FakePixelBus.instances.append(self)

    def show(self, rgb):
        self.colors.append(rgb)


class LedCommandStateTest(unittest.TestCase):
    def test_neutral_commands_show_blue(self):
        self.assertEqual(
            rgb_from_commands([0, 0]),
            (0, 0, config.STATUS_LED_NEUTRAL_BRIGHTNESS),
        )

    def test_dominant_forward_shows_green_with_scaled_intensity(self):
        low = state_from_commands([250, 0])
        high = state_from_commands([650, -250])

        self.assertEqual(low[0], DIRECTION_FORWARD)
        self.assertEqual(high[0], DIRECTION_FORWARD)
        self.assertGreater(high[1], low[1])
        self.assertEqual(high[1], active_brightness_from_command(650))
        self.assertEqual(rgb_from_commands([650, -250]), (0, high[1], 0))

    def test_dominant_reverse_shows_red_with_scaled_intensity(self):
        low = state_from_commands([0, -250])
        high = state_from_commands([500, -650])

        self.assertEqual(low[0], DIRECTION_REVERSE)
        self.assertEqual(high[0], DIRECTION_REVERSE)
        self.assertGreater(high[1], low[1])
        self.assertEqual(high[1], active_brightness_from_command(650))
        self.assertEqual(rgb_from_commands([500, -650]), (high[1], 0, 0))

    def test_full_commands_show_full_brightness(self):
        self.assertEqual(active_brightness_from_command(config.COMMAND_MAX), 255)
        self.assertEqual(rgb_from_commands([config.COMMAND_MAX, 0]), (0, 255, 0))
        self.assertEqual(rgb_from_commands([config.COMMAND_MIN, 0]), (255, 0, 0))

    def test_exact_opposing_ties_return_blue(self):
        self.assertEqual(state_from_commands([500, -500])[0], DIRECTION_NEUTRAL)
        self.assertEqual(state_from_commands([1000, -1000])[0], DIRECTION_NEUTRAL)
        self.assertEqual(
            rgb_from_commands([1000, -1000]),
            (0, 0, config.STATUS_LED_NEUTRAL_BRIGHTNESS),
        )


class StatusLedTest(unittest.TestCase):
    def setUp(self):
        self.old_pixel_bus = pixels.PixelBus
        FakePixelBus.instances = []
        pixels.PixelBus = FakePixelBus

    def tearDown(self):
        pixels.PixelBus = self.old_pixel_bus

    def latest_colors(self):
        return [bus.colors[-1] for bus in FakePixelBus.instances]

    def test_status_led_writes_rgb_state_to_all_configured_buses(self):
        led = StatusLed()

        self.assertEqual([bus.pin_id for bus in FakePixelBus.instances], list(config.LED_DATA_PINS))
        self.assertEqual([bus.count for bus in FakePixelBus.instances], list(config.LED_PIXEL_COUNTS))
        self.assertEqual(
            self.latest_colors(),
            [(0, 0, config.STATUS_LED_NEUTRAL_BRIGHTNESS)] * len(config.LED_DATA_PINS),
        )

        led.update([1000, -500])
        self.assertEqual(self.latest_colors(), [(0, 255, 0)] * len(config.LED_DATA_PINS))

        led.update([250, -1000])
        self.assertEqual(self.latest_colors(), [(255, 0, 0)] * len(config.LED_DATA_PINS))

        led.update([1000, -1000])
        self.assertEqual(
            self.latest_colors(),
            [(0, 0, config.STATUS_LED_NEUTRAL_BRIGHTNESS)] * len(config.LED_DATA_PINS),
        )

    def test_status_led_skips_redundant_bus_writes(self):
        led = StatusLed()
        initial_write_counts = [len(bus.colors) for bus in FakePixelBus.instances]

        led.update([0, 0])
        self.assertEqual(
            [len(bus.colors) for bus in FakePixelBus.instances],
            initial_write_counts,
        )

        led.update([1000, 0])
        after_change_counts = [len(bus.colors) for bus in FakePixelBus.instances]
        self.assertEqual(after_change_counts, [count + 1 for count in initial_write_counts])

        led.update([1000, 0])
        self.assertEqual(
            [len(bus.colors) for bus in FakePixelBus.instances],
            after_change_counts,
        )

    def test_led_update_depends_only_on_command_argument(self):
        signature = inspect.signature(StatusLed.update)
        self.assertEqual(list(signature.parameters), ["self", "commands"])

        source = inspect.getsource(StatusLed.update)
        self.assertIn("state_from_commands(commands)", source)
        self.assertNotIn("armed", source)
        self.assertNotIn("failsafe", source)
        self.assertNotIn("samples", source)


class AppLedIntegrationTest(unittest.TestCase):
    def test_app_passes_final_safe_commands_to_led_feedback(self):
        old_status_led = app.StatusLed
        old_pwm_input = app.PwmInput
        old_safety = app.Safety
        old_sleep_ms = app.sleep_ms
        old_ticks_us = app.ticks_us

        events = []
        raw_samples = object()
        final_commands = [500, -250]

        class StopLoop(Exception):
            pass

        class FakeOutput:
            def __init__(self):
                self.commands = final_commands
                self.armed = True
                self.failsafe = False

        class FakeLed:
            def update(self, commands):
                events.append(("led", commands))

        class FakeInputs:
            def samples(self):
                events.append(("samples", raw_samples))
                return raw_samples

        class FakeSafety:
            def update(self, samples, now_us):
                events.append(("safety", samples, now_us))
                return FakeOutput()

        def fake_sleep_ms(milliseconds):
            events.append(("sleep", milliseconds))
            raise StopLoop()

        def fake_ticks_us():
            events.append(("ticks", 123456))
            return 123456

        try:
            app.StatusLed = FakeLed
            app.PwmInput = FakeInputs
            app.Safety = FakeSafety
            app.sleep_ms = fake_sleep_ms
            app.ticks_us = fake_ticks_us

            with self.assertRaises(StopLoop):
                app.main()
        finally:
            app.StatusLed = old_status_led
            app.PwmInput = old_pwm_input
            app.Safety = old_safety
            app.sleep_ms = old_sleep_ms
            app.ticks_us = old_ticks_us

        self.assertEqual(
            events,
            [
                ("samples", raw_samples),
                ("ticks", 123456),
                ("safety", raw_samples, 123456),
                ("led", final_commands),
                ("sleep", config.CONTROL_LOOP_SLEEP_MS),
            ],
        )
