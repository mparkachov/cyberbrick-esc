try:
    from machine import Pin, PWM
except ImportError:
    Pin = None
    PWM = None

from cyberbrick_esc import config


class MotorOutputState:
    __slots__ = (
        "a_pin",
        "b_pin",
        "a_duty_u16",
        "b_duty_u16",
    )

    def __init__(self, a_pin, b_pin, a_duty_u16=0, b_duty_u16=0):
        self.a_pin = a_pin
        self.b_pin = b_pin
        self.a_duty_u16 = a_duty_u16
        self.b_duty_u16 = b_duty_u16


class MotorOutputs:
    __slots__ = ("_channels", "_states")

    def __init__(
        self,
        channel_pins=config.MOTOR_OUTPUT_PINS,
        channel_inverted=config.MOTOR_OUTPUT_INVERTED,
        pwm_hz=config.MOTOR_PWM_HZ,
    ):
        if Pin is None or PWM is None:
            raise RuntimeError("machine.Pin and machine.PWM are required")
        if len(channel_pins) != len(channel_inverted):
            raise ValueError("motor pin and inversion counts must match")

        self._channels = tuple(
            MotorOutputChannel(
                a_pin,
                b_pin,
                channel_inverted[index],
                pwm_hz,
            )
            for index, (a_pin, b_pin) in enumerate(channel_pins)
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
        "a_pin_id",
        "b_pin_id",
        "a_pwm",
        "b_pwm",
        "a_duty_u16",
        "b_duty_u16",
        "inverted",
        "_state",
    )

    def __init__(self, a_pin_id, b_pin_id, inverted, pwm_hz):
        self.a_pin_id = a_pin_id
        self.b_pin_id = b_pin_id
        self.inverted = inverted
        self.a_pwm = PWM(Pin(a_pin_id, Pin.OUT), freq=pwm_hz)
        self.b_pwm = PWM(Pin(b_pin_id, Pin.OUT), freq=pwm_hz)
        self.a_duty_u16 = -1
        self.b_duty_u16 = -1
        self._state = MotorOutputState(a_pin_id, b_pin_id)
        self._set_a(0)
        self._set_b(0)

    def update(self, command):
        command = normalized_output_command(command)
        if self.inverted:
            command = -command
        duty_u16 = command_to_duty_u16(command)
        if command > config.COMMAND_NEUTRAL:
            self._set_b(0)
            self._set_a(duty_u16)
        elif command < config.COMMAND_NEUTRAL:
            self._set_a(0)
            self._set_b(duty_u16)
        else:
            self._set_a(0)
            self._set_b(0)

    def state(self):
        return self._state

    def _set_a(self, duty_u16):
        if self.a_duty_u16 == duty_u16:
            return
        set_pwm_duty_u16(self.a_pwm, duty_u16)
        self.a_duty_u16 = duty_u16
        self._state.a_duty_u16 = duty_u16

    def _set_b(self, duty_u16):
        if self.b_duty_u16 == duty_u16:
            return
        set_pwm_duty_u16(self.b_pwm, duty_u16)
        self.b_duty_u16 = duty_u16
        self._state.b_duty_u16 = duty_u16


def command_to_duty_u16(command):
    command = normalized_output_command(command)
    magnitude = abs(command)
    return (
        magnitude * config.MOTOR_PWM_MAX_DUTY_U16 + config.COMMAND_MAX // 2
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
                state.a_pin,
                state.a_duty_u16,
                state.b_pin,
                state.b_duty_u16,
            )
        )
    return "out=" + ",".join(parts)
