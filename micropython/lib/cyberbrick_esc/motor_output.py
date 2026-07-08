try:
    from machine import Pin, PWM
except ImportError:
    Pin = None
    PWM = None

from cyberbrick_esc import config


class MotorOutputState:
    __slots__ = (
        "forward_pin",
        "reverse_pin",
        "forward_duty_u16",
        "reverse_duty_u16",
    )

    def __init__(self, forward_pin, reverse_pin, forward_duty_u16=0, reverse_duty_u16=0):
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        self.forward_duty_u16 = forward_duty_u16
        self.reverse_duty_u16 = reverse_duty_u16


class MotorOutputs:
    __slots__ = ("_channels", "_states")

    def __init__(self, channel_pins=config.MOTOR_OUTPUT_PINS, pwm_hz=config.MOTOR_PWM_HZ):
        if Pin is None or PWM is None:
            raise RuntimeError("machine.Pin and machine.PWM are required")

        self._channels = tuple(
            MotorOutputChannel(forward_pin, reverse_pin, pwm_hz)
            for forward_pin, reverse_pin in channel_pins
        )
        self._states = tuple(channel.state() for channel in self._channels)

    def update(self, commands):
        for index, channel in enumerate(self._channels):
            try:
                command = commands[index]
            except (TypeError, IndexError, KeyError):
                command = config.COMMAND_NEUTRAL
            channel.update(command)
        return self.states()

    def states(self):
        return self._states


class MotorOutputChannel:
    __slots__ = (
        "forward_pin_id",
        "reverse_pin_id",
        "forward_pwm",
        "reverse_pwm",
        "forward_duty_u16",
        "reverse_duty_u16",
        "_state",
    )

    def __init__(self, forward_pin_id, reverse_pin_id, pwm_hz):
        self.forward_pin_id = forward_pin_id
        self.reverse_pin_id = reverse_pin_id
        self.forward_pwm = PWM(Pin(forward_pin_id, Pin.OUT), freq=pwm_hz)
        self.reverse_pwm = PWM(Pin(reverse_pin_id, Pin.OUT), freq=pwm_hz)
        self.forward_duty_u16 = -1
        self.reverse_duty_u16 = -1
        self._state = MotorOutputState(forward_pin_id, reverse_pin_id)
        self._set_forward(0)
        self._set_reverse(0)

    def update(self, command):
        command = normalized_output_command(command)
        duty_u16 = command_to_duty_u16(command)
        if command > config.COMMAND_NEUTRAL:
            self._set_reverse(0)
            self._set_forward(duty_u16)
        elif command < config.COMMAND_NEUTRAL:
            self._set_forward(0)
            self._set_reverse(duty_u16)
        else:
            self._set_forward(0)
            self._set_reverse(0)

    def state(self):
        return self._state

    def _set_forward(self, duty_u16):
        if self.forward_duty_u16 == duty_u16:
            return
        set_pwm_duty_u16(self.forward_pwm, duty_u16)
        self.forward_duty_u16 = duty_u16
        self._state.forward_duty_u16 = duty_u16

    def _set_reverse(self, duty_u16):
        if self.reverse_duty_u16 == duty_u16:
            return
        set_pwm_duty_u16(self.reverse_pwm, duty_u16)
        self.reverse_duty_u16 = duty_u16
        self._state.reverse_duty_u16 = duty_u16


def command_to_duty_u16(command):
    command = normalized_output_command(command)
    magnitude = abs(command)
    return (
        magnitude * config.MOTOR_PWM_FULL_COMMAND_DUTY_U16 + config.COMMAND_MAX // 2
    ) // config.COMMAND_MAX


def normalized_output_command(command):
    if isinstance(command, bool) or not isinstance(command, int):
        return 0

    if command > config.COMMAND_MAX:
        return config.COMMAND_MAX

    if command < config.COMMAND_MIN:
        return config.COMMAND_MIN

    return command


def set_pwm_duty_u16(pwm, duty_u16):
    if hasattr(pwm, "duty_u16"):
        pwm.duty_u16(duty_u16)
    elif hasattr(pwm, "duty"):
        pwm.duty(
            (duty_u16 * 1023 + config.MOTOR_PWM_MAX_DUTY_U16 // 2)
            // config.MOTOR_PWM_MAX_DUTY_U16
        )
    else:
        raise RuntimeError("PWM object does not support duty_u16 or duty")


def output_diagnostic(states):
    if states is None:
        return "out=missing"

    parts = []
    for index, state in enumerate(states):
        parts.append(
            "m{}:a{}={}/b{}={}".format(
                index,
                state.forward_pin,
                state.forward_duty_u16,
                state.reverse_pin,
                state.reverse_duty_u16,
            )
        )
    return "out=" + ",".join(parts)
