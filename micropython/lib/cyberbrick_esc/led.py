from cyberbrick_esc import config


DIRECTION_NEUTRAL = 0
DIRECTION_FORWARD = 1
DIRECTION_REVERSE = -1


class StatusLed:
    def __init__(self, pin_id=config.LED_PIN, count=config.LED_COUNT):
        from machine import Pin
        from neopixel import NeoPixel

        self._pixel = NeoPixel(Pin(pin_id, Pin.OUT), count)
        self.show_neutral()

    def show_neutral(self):
        self._apply_state(DIRECTION_NEUTRAL, config.STATUS_LED_NEUTRAL_BRIGHTNESS)

    def update(self, commands):
        direction, brightness = state_from_commands(commands)
        self._apply_state(direction, brightness)

    def _apply_state(self, direction, brightness):
        if direction == DIRECTION_FORWARD:
            color = (0, brightness, 0)
        elif direction == DIRECTION_REVERSE:
            color = (brightness, 0, 0)
        else:
            color = (0, 0, brightness)

        self._pixel[0] = color
        self._pixel.write()


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
