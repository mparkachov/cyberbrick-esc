#include <stdint.h>

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include <cyberbrick_esc/motor_output.h>
#include <cyberbrick_esc/pwm_input.h>
#include <cyberbrick_esc/safety.h>

LOG_MODULE_REGISTER(cyberbrick_esc, LOG_LEVEL_INF);

BUILD_ASSERT(CONFIG_CYBERBRICK_ESC_CONTROL_LOOP_HZ > 0,
	     "Control loop rate must be positive");

static const struct cyberbrick_esc_safety_config safety_config = {
	.input_timeout_us = CONFIG_CYBERBRICK_ESC_INPUT_TIMEOUT_MS * 1000U,
	.arming_time_us = CONFIG_CYBERBRICK_ESC_ARMING_TIME_MS * 1000U,
	.min_valid_us = CONFIG_CYBERBRICK_ESC_MIN_VALID_US,
	.max_valid_us = CONFIG_CYBERBRICK_ESC_MAX_VALID_US,
	.min_command_us = CONFIG_CYBERBRICK_ESC_MIN_COMMAND_US,
	.neutral_us = CONFIG_CYBERBRICK_ESC_NEUTRAL_US,
	.max_command_us = CONFIG_CYBERBRICK_ESC_MAX_COMMAND_US,
	.deadband_us = CONFIG_CYBERBRICK_ESC_DEADBAND_US,
};

static uint32_t control_loop_sleep_ms(void)
{
	uint32_t sleep_ms = 1000U / CONFIG_CYBERBRICK_ESC_CONTROL_LOOP_HZ;

	return sleep_ms == 0U ? 1U : sleep_ms;
}

int main(void)
{
	struct cyberbrick_esc_safety safety;
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT];
	struct cyberbrick_esc_safety_output output;
	bool last_armed = false;
	bool last_failsafe = false;
	int ret;

	LOG_INF("CyberBrick ESC boot");

	cyberbrick_esc_safety_init(&safety);

	ret = cyberbrick_esc_motor_output_init();
	if (ret != 0) {
		(void)cyberbrick_esc_motor_output_stop();
		LOG_ERR("Motor output init failed: %d", ret);
		return ret;
	}

	ret = cyberbrick_esc_pwm_input_init();
	if (ret != 0) {
		(void)cyberbrick_esc_motor_output_stop();
		LOG_ERR("PWM input init failed: %d", ret);
		return ret;
	}

	LOG_INF("Waiting for neutral input before arming");

	while (true) {
		cyberbrick_esc_pwm_input_get_samples(samples);
		cyberbrick_esc_safety_update(&safety, &safety_config, samples,
					     k_uptime_get() * 1000LL, &output);

		ret = cyberbrick_esc_motor_output_apply(output.command);
		if (ret != 0) {
			(void)cyberbrick_esc_motor_output_stop();
			LOG_ERR("Motor output apply failed: %d", ret);
		}

		if (output.armed != last_armed || output.failsafe != last_failsafe) {
			LOG_INF("state armed=%d failsafe=%d", output.armed,
				output.failsafe);
			last_armed = output.armed;
			last_failsafe = output.failsafe;
		}

		k_msleep(control_loop_sleep_ms());
	}

	return 0;
}
