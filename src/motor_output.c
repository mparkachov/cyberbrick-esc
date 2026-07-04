#include <errno.h>
#include <stddef.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/pwm.h>
#include <zephyr/kernel.h>

#include <cyberbrick_esc/motor_output.h>

#ifndef CONFIG_CYBERBRICK_ESC_OUTPUT_PWM_HZ
#define CONFIG_CYBERBRICK_ESC_OUTPUT_PWM_HZ 1000
#endif

#ifndef CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_FORWARD_PERMILLE
#define CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_FORWARD_PERMILLE 1000
#endif

#ifndef CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_REVERSE_PERMILLE
#define CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_REVERSE_PERMILLE 1000
#endif

#ifndef CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_FORWARD_PERMILLE
#define CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_FORWARD_PERMILLE 1000
#endif

#ifndef CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_REVERSE_PERMILLE
#define CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_REVERSE_PERMILLE 1000
#endif

#define MOTOR_OUTPUT_HAS_DT (DT_NODE_EXISTS(DT_ALIAS(motor_1_a)) && \
			     DT_NODE_EXISTS(DT_ALIAS(motor_1_b)) && \
			     DT_NODE_EXISTS(DT_ALIAS(motor_2_a)) && \
			     DT_NODE_EXISTS(DT_ALIAS(motor_2_b)))

static int16_t clamp_command(int16_t command)
{
	if (command > CYBERBRICK_ESC_COMMAND_MAX) {
		return CYBERBRICK_ESC_COMMAND_MAX;
	}

	if (command < CYBERBRICK_ESC_COMMAND_MIN) {
		return CYBERBRICK_ESC_COMMAND_MIN;
	}

	return command;
}

static uint16_t clamp_permille(uint16_t value)
{
	if (value > 1000U) {
		return 1000U;
	}

	return value;
}

void cyberbrick_esc_motor_make_state(int16_t command,
				     const struct cyberbrick_esc_motor_config *config,
				     struct cyberbrick_esc_motor_state *state)
{
	int32_t physical_command;
	uint16_t duty_permille;

	if (config == NULL || state == NULL) {
		return;
	}

	physical_command = clamp_command(command);
	if (config->inverted) {
		physical_command = -physical_command;
	}

	if (physical_command == CYBERBRICK_ESC_COMMAND_NEUTRAL) {
		if (config->stop_mode == CYBERBRICK_ESC_STOP_MODE_BRAKE) {
			state->input_a.mode = CYBERBRICK_ESC_PIN_HIGH;
			state->input_b.mode = CYBERBRICK_ESC_PIN_HIGH;
		} else {
			state->input_a.mode = CYBERBRICK_ESC_PIN_LOW;
			state->input_b.mode = CYBERBRICK_ESC_PIN_LOW;
		}
		state->input_a.duty_permille = 0U;
		state->input_b.duty_permille = 0U;
		return;
	}

	if (physical_command > 0) {
		duty_permille = (uint16_t)((physical_command *
					    clamp_permille(config->max_forward_permille)) /
					   CYBERBRICK_ESC_COMMAND_MAX);
		state->input_a.mode = CYBERBRICK_ESC_PIN_PWM;
		state->input_a.duty_permille = duty_permille;
		state->input_b.mode = CYBERBRICK_ESC_PIN_LOW;
		state->input_b.duty_permille = 0U;
	} else {
		duty_permille = (uint16_t)((-physical_command *
					    clamp_permille(config->max_reverse_permille)) /
					   CYBERBRICK_ESC_COMMAND_MAX);
		state->input_a.mode = CYBERBRICK_ESC_PIN_LOW;
		state->input_a.duty_permille = 0U;
		state->input_b.mode = CYBERBRICK_ESC_PIN_PWM;
		state->input_b.duty_permille = duty_permille;
	}
}

#define CONFIGURED_STOP_MODE \
	(IS_ENABLED(CONFIG_CYBERBRICK_ESC_STOP_MODE_BRAKE) ? \
	 CYBERBRICK_ESC_STOP_MODE_BRAKE : CYBERBRICK_ESC_STOP_MODE_COAST)

static const struct cyberbrick_esc_motor_config motor_configs[CYBERBRICK_ESC_CHANNEL_COUNT] = {
	{
		.inverted = IS_ENABLED(CONFIG_CYBERBRICK_ESC_MOTOR1_INVERT),
		.max_forward_permille = CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_FORWARD_PERMILLE,
		.max_reverse_permille = CONFIG_CYBERBRICK_ESC_MOTOR1_MAX_REVERSE_PERMILLE,
		.stop_mode = CONFIGURED_STOP_MODE,
	},
	{
		.inverted = IS_ENABLED(CONFIG_CYBERBRICK_ESC_MOTOR2_INVERT),
		.max_forward_permille = CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_FORWARD_PERMILLE,
		.max_reverse_permille = CONFIG_CYBERBRICK_ESC_MOTOR2_MAX_REVERSE_PERMILLE,
		.stop_mode = CONFIGURED_STOP_MODE,
	},
};

#if MOTOR_OUTPUT_HAS_DT
static const struct pwm_dt_spec motor_pwms[CYBERBRICK_ESC_CHANNEL_COUNT][2] = {
	{
		PWM_DT_SPEC_GET(DT_ALIAS(motor_1_a)),
		PWM_DT_SPEC_GET(DT_ALIAS(motor_1_b)),
	},
	{
		PWM_DT_SPEC_GET(DT_ALIAS(motor_2_a)),
		PWM_DT_SPEC_GET(DT_ALIAS(motor_2_b)),
	},
};
#endif

static uint32_t output_period_ns(void)
{
	return NSEC_PER_SEC / CONFIG_CYBERBRICK_ESC_OUTPUT_PWM_HZ;
}

#if MOTOR_OUTPUT_HAS_DT
static int apply_pin_drive(const struct pwm_dt_spec *pwm,
			   const struct cyberbrick_esc_pin_drive *drive)
{
	uint32_t period_ns = output_period_ns();
	uint32_t pulse_ns;

	switch (drive->mode) {
	case CYBERBRICK_ESC_PIN_HIGH:
		pulse_ns = period_ns;
		break;
	case CYBERBRICK_ESC_PIN_PWM:
		pulse_ns = (period_ns * drive->duty_permille) / 1000U;
		break;
	case CYBERBRICK_ESC_PIN_LOW:
	default:
		pulse_ns = 0U;
		break;
	}

	return pwm_set_dt(pwm, period_ns, pulse_ns);
}

static int apply_motor_state(size_t index,
			     const struct cyberbrick_esc_motor_state *state)
{
	int ret;

	ret = apply_pin_drive(&motor_pwms[index][0], &state->input_a);
	if (ret != 0) {
		return ret;
	}

	return apply_pin_drive(&motor_pwms[index][1], &state->input_b);
}
#endif

int cyberbrick_esc_motor_output_init(void)
{
#if MOTOR_OUTPUT_HAS_DT
	for (size_t motor = 0; motor < CYBERBRICK_ESC_CHANNEL_COUNT; motor++) {
		for (size_t input = 0; input < 2; input++) {
			if (!pwm_is_ready_dt(&motor_pwms[motor][input])) {
				return -ENODEV;
			}
		}
	}
#endif

	return cyberbrick_esc_motor_output_stop();
}

int cyberbrick_esc_motor_output_apply(const int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT])
{
	struct cyberbrick_esc_motor_state state;
	int16_t safe_command[CYBERBRICK_ESC_CHANNEL_COUNT] = { 0 };

	if (command != NULL) {
		for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
			safe_command[i] = clamp_command(command[i]);
		}
	}

	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		cyberbrick_esc_motor_make_state(safe_command[i], &motor_configs[i],
						&state);
#if MOTOR_OUTPUT_HAS_DT
		int ret = apply_motor_state(i, &state);

		if (ret != 0) {
			return ret;
		}
#endif
	}

	return 0;
}

int cyberbrick_esc_motor_output_stop(void)
{
	int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT] = { 0 };

	return cyberbrick_esc_motor_output_apply(command);
}
