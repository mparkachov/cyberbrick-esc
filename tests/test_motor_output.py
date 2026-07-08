import unittest

from cyberbrick_esc import config
from cyberbrick_esc import motor_output


class FakePin:
    OUT = 1
    instances = []

    def __init__(self, pin_id, mode):
        self.pin_id = pin_id
        self.mode = mode
        FakePin.instances.append(self)


class FakePWM:
    instances = []

    def __init__(self, pin, freq):
        self.pin = pin
        self.freq = freq
        self.duties = []
        FakePWM.instances.append(self)

    def duty_u16(self, duty):
        self.duties.append(duty)


class MotorOutputTest(unittest.TestCase):
    def setUp(self):
        self.old_pin = motor_output.Pin
        self.old_pwm = motor_output.PWM
        FakePin.instances = []
        FakePWM.instances = []
        motor_output.Pin = FakePin
        motor_output.PWM = FakePWM

    def tearDown(self):
        motor_output.Pin = self.old_pin
        motor_output.PWM = self.old_pwm

    def test_initializes_all_hbridge_inputs_as_zero_duty_pwm(self):
        outputs = motor_output.MotorOutputs()

        self.assertEqual([pin.pin_id for pin in FakePin.instances], [4, 5, 6, 7])
        self.assertTrue(all(pin.mode == FakePin.OUT for pin in FakePin.instances))
        self.assertEqual([pwm.freq for pwm in FakePWM.instances], [config.MOTOR_PWM_HZ] * 4)
        self.assertEqual([pwm.duties for pwm in FakePWM.instances], [[0], [0], [0], [0]])
        self.assertEqual(len(outputs.states()), config.CHANNEL_COUNT)

    def test_final_commands_drive_signed_hbridge_pwm_outputs(self):
        outputs = motor_output.MotorOutputs()

        states = outputs.update([1000, -500])

        self.assertEqual(states[0].forward_pin, 4)
        self.assertEqual(states[0].reverse_pin, 5)
        self.assertEqual(states[0].forward_duty_u16, config.MOTOR_PWM_FULL_COMMAND_DUTY_U16)
        self.assertEqual(states[0].reverse_duty_u16, 0)
        self.assertEqual(states[1].forward_pin, 6)
        self.assertEqual(states[1].reverse_pin, 7)
        self.assertEqual(states[1].forward_duty_u16, 0)
        self.assertEqual(states[1].reverse_duty_u16, 8192)

    def test_neutral_and_malformed_commands_drive_both_sides_low(self):
        outputs = motor_output.MotorOutputs()

        states = outputs.update([True, "1000"])

        self.assertEqual(states[0].forward_duty_u16, 0)
        self.assertEqual(states[0].reverse_duty_u16, 0)
        self.assertEqual(states[1].forward_duty_u16, 0)
        self.assertEqual(states[1].reverse_duty_u16, 0)

    def test_direction_change_zeroes_previous_side_before_driving_new_side(self):
        outputs = motor_output.MotorOutputs()
        outputs.update([1000, 0])
        outputs.update([-1000, 0])

        forward_pwm = FakePWM.instances[0]
        reverse_pwm = FakePWM.instances[1]
        self.assertEqual(forward_pwm.duties[-2:], [config.MOTOR_PWM_FULL_COMMAND_DUTY_U16, 0])
        self.assertEqual(reverse_pwm.duties[-2:], [0, config.MOTOR_PWM_FULL_COMMAND_DUTY_U16])

    def test_output_state_objects_are_reused(self):
        outputs = motor_output.MotorOutputs()
        first = outputs.states()

        second = outputs.update([1000, -1000])

        self.assertIs(first, second)
        self.assertEqual(first[0].forward_duty_u16, config.MOTOR_PWM_FULL_COMMAND_DUTY_U16)
        self.assertEqual(first[1].reverse_duty_u16, config.MOTOR_PWM_FULL_COMMAND_DUTY_U16)

    def test_redundant_pwm_writes_are_skipped_for_stable_commands(self):
        outputs = motor_output.MotorOutputs()
        outputs.update([1000, 0])
        write_counts = [len(pwm.duties) for pwm in FakePWM.instances]

        outputs.update([1000, 0])

        self.assertEqual([len(pwm.duties) for pwm in FakePWM.instances], write_counts)

    def test_output_diagnostic_reports_pin_and_duty(self):
        outputs = motor_output.MotorOutputs()
        states = outputs.update([1000, -1000])

        self.assertEqual(
            motor_output.output_diagnostic(states),
            "out=m0:a4=16384/b5=0,m1:a6=0/b7=16384",
        )

    def test_command_to_duty_clamps_to_supported_range(self):
        self.assertEqual(motor_output.command_to_duty_u16(0), 0)
        self.assertEqual(motor_output.command_to_duty_u16(500), 8192)
        self.assertEqual(motor_output.command_to_duty_u16(-500), 8192)
        self.assertEqual(motor_output.command_to_duty_u16(5000), 16384)
        self.assertEqual(motor_output.command_to_duty_u16(-5000), 16384)
        self.assertEqual(motor_output.command_to_duty_u16("500"), 0)


if __name__ == "__main__":
    unittest.main()
