#include <errno.h>

#include <zephyr/ztest.h>

#include <cyberbrick_esc/motor_output.h>
#include <cyberbrick_esc/safety.h>

static const struct cyberbrick_esc_safety_config test_config = {
	.input_timeout_us = 150000,
	.arming_time_us = 1000000,
	.min_valid_us = 900,
	.max_valid_us = 2100,
	.min_command_us = 1000,
	.neutral_us = 1500,
	.max_command_us = 2000,
	.deadband_us = 50,
};

static void set_samples(struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT],
			uint32_t pulse_0_us, uint32_t pulse_1_us, int64_t now_us)
{
	samples[0].valid = true;
	samples[0].pulse_width_us = pulse_0_us;
	samples[0].timestamp_us = now_us;
	samples[1].valid = true;
	samples[1].pulse_width_us = pulse_1_us;
	samples[1].timestamp_us = now_us;
}

ZTEST(cyberbrick_esc_safety, test_pulse_mapping_points)
{
	int16_t command;

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 1000, &command));
	zassert_equal(command, -1000);

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 1500, &command));
	zassert_equal(command, 0);

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 2000, &command));
	zassert_equal(command, 1000);
}

ZTEST(cyberbrick_esc_safety, test_deadband_and_clamping)
{
	int16_t command;

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 1450, &command));
	zassert_equal(command, 0);

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 1550, &command));
	zassert_equal(command, 0);

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 900, &command));
	zassert_equal(command, -1000);

	zassert_ok(cyberbrick_esc_map_pulse_us(&test_config, 2100, &command));
	zassert_equal(command, 1000);
}

ZTEST(cyberbrick_esc_safety, test_invalid_pulse_rejection)
{
	struct cyberbrick_esc_safety safety;
	struct cyberbrick_esc_safety_output output;
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT];
	int16_t command = 123;

	zassert_equal(cyberbrick_esc_map_pulse_us(&test_config, 899, &command),
		      -EINVAL);
	zassert_equal(command, 123);
	zassert_equal(cyberbrick_esc_map_pulse_us(&test_config, 2101, &command),
		      -EINVAL);

	cyberbrick_esc_safety_init(&safety);
	set_samples(samples, 800, 1500, 0);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 0, &output);

	zassert_false(output.armed);
	zassert_true(output.failsafe);
	zassert_equal(output.command[0], 0);
	zassert_equal(output.command[1], 0);
}

ZTEST(cyberbrick_esc_safety, test_neutral_required_before_arming)
{
	struct cyberbrick_esc_safety safety;
	struct cyberbrick_esc_safety_output output;
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT];

	cyberbrick_esc_safety_init(&safety);

	set_samples(samples, 1600, 1500, 0);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 0, &output);
	zassert_false(output.armed);
	zassert_equal(output.command[0], 0);

	set_samples(samples, 1500, 1500, 0);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 0, &output);
	zassert_false(output.armed);

	set_samples(samples, 1500, 1500, 999000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 999000, &output);
	zassert_false(output.armed);

	set_samples(samples, 1500, 1500, 1000000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1000000, &output);
	zassert_true(output.armed);
	zassert_equal(output.command[0], 0);
	zassert_equal(output.command[1], 0);
}

ZTEST(cyberbrick_esc_safety, test_failsafe_and_neutral_recovery)
{
	struct cyberbrick_esc_safety safety;
	struct cyberbrick_esc_safety_output output;
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT];

	cyberbrick_esc_safety_init(&safety);
	set_samples(samples, 1500, 1500, 0);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 0, &output);
	set_samples(samples, 1500, 1500, 1000000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1000000, &output);
	zassert_true(output.armed);

	set_samples(samples, 1700, 1500, 1010000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1010000, &output);
	zassert_true(output.armed);
	zassert_true(output.command[0] > 0);

	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1200001, &output);
	zassert_false(output.armed);
	zassert_true(output.failsafe);
	zassert_equal(output.command[0], 0);

	set_samples(samples, 1700, 1500, 1210000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1210000, &output);
	zassert_false(output.armed);
	zassert_equal(output.command[0], 0);

	set_samples(samples, 1500, 1500, 1220000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 1220000, &output);
	zassert_false(output.armed);

	set_samples(samples, 1500, 1500, 2220000);
	cyberbrick_esc_safety_update(&safety, &test_config, samples, 2220000, &output);
	zassert_true(output.armed);
	zassert_false(output.failsafe);
}

ZTEST(cyberbrick_esc_safety, test_motor_forward_reverse_and_stop_states)
{
	const struct cyberbrick_esc_motor_config config = {
		.inverted = false,
		.max_forward_permille = 1000,
		.max_reverse_permille = 1000,
		.stop_mode = CYBERBRICK_ESC_STOP_MODE_COAST,
	};
	struct cyberbrick_esc_motor_state state;

	cyberbrick_esc_motor_make_state(500, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_PWM);
	zassert_equal(state.input_a.duty_permille, 500);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_LOW);

	cyberbrick_esc_motor_make_state(-250, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_LOW);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_PWM);
	zassert_equal(state.input_b.duty_permille, 250);

	cyberbrick_esc_motor_make_state(0, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_LOW);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_LOW);
}

ZTEST(cyberbrick_esc_safety, test_motor_brake_inversion_and_scaling)
{
	struct cyberbrick_esc_motor_config config = {
		.inverted = false,
		.max_forward_permille = 500,
		.max_reverse_permille = 250,
		.stop_mode = CYBERBRICK_ESC_STOP_MODE_BRAKE,
	};
	struct cyberbrick_esc_motor_state state;

	cyberbrick_esc_motor_make_state(0, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_HIGH);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_HIGH);

	cyberbrick_esc_motor_make_state(1000, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_PWM);
	zassert_equal(state.input_a.duty_permille, 500);

	cyberbrick_esc_motor_make_state(-1000, &config, &state);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_PWM);
	zassert_equal(state.input_b.duty_permille, 250);

	config.inverted = true;
	cyberbrick_esc_motor_make_state(400, &config, &state);
	zassert_equal(state.input_a.mode, CYBERBRICK_ESC_PIN_LOW);
	zassert_equal(state.input_b.mode, CYBERBRICK_ESC_PIN_PWM);
	zassert_equal(state.input_b.duty_permille, 100);
}

ZTEST_SUITE(cyberbrick_esc_safety, NULL, NULL, NULL, NULL, NULL);
