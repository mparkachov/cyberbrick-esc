from cyberbrick_esc import config


DIRECTION_NEUTRAL = 0
DIRECTION_FORWARD = 1
DIRECTION_REVERSE = -1


class StatusLed:
    def __init__(self):
        from cyberbrick_esc.pixels import PixelBus

        self._last_color = None
        self._buses = tuple(
            PixelBus(pin_id, count)
            for pin_id, count in zip(config.LED_DATA_PINS, config.LED_PIXEL_COUNTS)
        )
        self.show_neutral()

    def show_neutral(self):
        self._apply_state(DIRECTION_NEUTRAL, config.STATUS_LED_NEUTRAL_BRIGHTNESS)

    def update(self, commands):
        direction, brightness = state_from_commands(commands)
        self._apply_state(direction, brightness)

    def _apply_state(self, direction, brightness):
        color = rgb_from_state(direction, brightness)
        if color == self._last_color:
            return

        self._last_color = color
        for bus in self._buses:
            bus.show(color)


def rgb_from_commands(commands):
    direction, brightness = state_from_commands(commands)
    return rgb_from_state(direction, brightness)


def rgb_from_state(direction, brightness):
    if direction == DIRECTION_FORWARD:
        return (0, brightness, 0)
    if direction == DIRECTION_REVERSE:
        return (brightness, 0, 0)
    return (0, 0, brightness)


def state_from_commands(commands):
    forward = 0
    reverse = 0

    if commands is None:
        return (DIRECTION_NEUTRAL, config.STATUS_LED_NEUTRAL_BRIGHTNESS)

    for command in commands:
        if command > 0:
            forward = max(forward, abs_command(command))
        elif command < 0:
            reverse = max(reverse, abs_command(command))

    if forward > reverse:
        return (DIRECTION_FORWARD, active_brightness_from_command(forward))
    if reverse > forward:
        return (DIRECTION_REVERSE, active_brightness_from_command(reverse))
    return (DIRECTION_NEUTRAL, config.STATUS_LED_NEUTRAL_BRIGHTNESS)


def active_brightness_from_command(magnitude):
    magnitude = max(0, min(config.COMMAND_MAX, magnitude))
    min_brightness = config.STATUS_LED_MIN_ACTIVE_BRIGHTNESS
    value = min_brightness + ((255 - min_brightness) * magnitude) // config.COMMAND_MAX
    return max(min_brightness, min(255, value))


def abs_command(command):
    if command <= config.COMMAND_MIN:
        return config.COMMAND_MAX
    return -command if command < 0 else command
