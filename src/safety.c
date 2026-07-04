#include <errno.h>
#include <stddef.h>

#include <cyberbrick_esc/safety.h>

static int16_t clamp_command(int32_t command)
{
	if (command > CYBERBRICK_ESC_COMMAND_MAX) {
		return CYBERBRICK_ESC_COMMAND_MAX;
	}

	if (command < CYBERBRICK_ESC_COMMAND_MIN) {
		return CYBERBRICK_ESC_COMMAND_MIN;
	}

	return (int16_t)command;
}

static bool config_valid(const struct cyberbrick_esc_safety_config *config)
{
	return config != NULL &&
	       config->min_valid_us < config->max_valid_us &&
	       config->min_command_us < config->neutral_us &&
	       config->neutral_us < config->max_command_us &&
	       config->min_valid_us <= config->min_command_us &&
	       config->max_command_us <= config->max_valid_us;
}

static bool sample_fresh(const struct cyberbrick_esc_pulse_sample *sample,
			 int64_t now_us, uint32_t timeout_us)
{
	if (!sample->valid || sample->timestamp_us > now_us) {
		return false;
	}

	return (uint64_t)(now_us - sample->timestamp_us) <= timeout_us;
}

static void set_safe_output(const struct cyberbrick_esc_safety *safety,
			    struct cyberbrick_esc_safety_output *output)
{
	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		output->command[i] = CYBERBRICK_ESC_COMMAND_NEUTRAL;
	}

	output->armed = safety->armed;
	output->failsafe = safety->failsafe;
}

void cyberbrick_esc_safety_init(struct cyberbrick_esc_safety *safety)
{
	if (safety == NULL) {
		return;
	}

	safety->armed = false;
	safety->failsafe = false;
	safety->neutral_pending = false;
	safety->neutral_since_us = 0;
}

int cyberbrick_esc_map_pulse_us(const struct cyberbrick_esc_safety_config *config,
				uint32_t pulse_width_us, int16_t *command)
{
	int32_t mapped;

	if (!config_valid(config) || command == NULL) {
		return -EINVAL;
	}

	if (pulse_width_us < config->min_valid_us ||
	    pulse_width_us > config->max_valid_us) {
		return -EINVAL;
	}

	if (pulse_width_us <= config->min_command_us) {
		*command = CYBERBRICK_ESC_COMMAND_MIN;
		return 0;
	}

	if (pulse_width_us >= config->max_command_us) {
		*command = CYBERBRICK_ESC_COMMAND_MAX;
		return 0;
	}

	if (pulse_width_us >= config->neutral_us - config->deadband_us &&
	    pulse_width_us <= config->neutral_us + config->deadband_us) {
		*command = CYBERBRICK_ESC_COMMAND_NEUTRAL;
		return 0;
	}

	if (pulse_width_us < config->neutral_us) {
		uint32_t span_us = config->neutral_us - config->min_command_us;
		uint32_t delta_us = config->neutral_us - pulse_width_us;

		mapped = -((int32_t)((delta_us * CYBERBRICK_ESC_COMMAND_MAX) +
				     (span_us / 2U)) /
			   (int32_t)span_us);
	} else {
		uint32_t span_us = config->max_command_us - config->neutral_us;
		uint32_t delta_us = pulse_width_us - config->neutral_us;

		mapped = (int32_t)((delta_us * CYBERBRICK_ESC_COMMAND_MAX) +
				   (span_us / 2U)) /
			 (int32_t)span_us;
	}

	*command = clamp_command(mapped);
	return 0;
}

void cyberbrick_esc_safety_update(struct cyberbrick_esc_safety *safety,
				  const struct cyberbrick_esc_safety_config *config,
				  const struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT],
				  int64_t now_us,
				  struct cyberbrick_esc_safety_output *output)
{
	int16_t mapped[CYBERBRICK_ESC_CHANNEL_COUNT] = { 0 };
	bool all_fresh = true;
	bool all_neutral = true;

	if (safety == NULL || output == NULL || !config_valid(config) ||
	    samples == NULL) {
		return;
	}

	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		if (!sample_fresh(&samples[i], now_us, config->input_timeout_us) ||
		    cyberbrick_esc_map_pulse_us(config, samples[i].pulse_width_us,
						&mapped[i]) != 0) {
			all_fresh = false;
			break;
		}

		if (mapped[i] != CYBERBRICK_ESC_COMMAND_NEUTRAL) {
			all_neutral = false;
		}
	}

	if (!all_fresh) {
		safety->armed = false;
		safety->failsafe = true;
		safety->neutral_pending = false;
		set_safe_output(safety, output);
		return;
	}

	if (!safety->armed) {
		if (all_neutral) {
			if (!safety->neutral_pending) {
				safety->neutral_pending = true;
				safety->neutral_since_us = now_us;
			}

			if ((uint64_t)(now_us - safety->neutral_since_us) >=
			    config->arming_time_us) {
				safety->armed = true;
				safety->failsafe = false;
			}
		} else {
			safety->neutral_pending = false;
		}

		set_safe_output(safety, output);
		return;
	}

	safety->failsafe = false;
	safety->neutral_pending = false;
	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		output->command[i] = mapped[i];
	}
	output->armed = true;
	output->failsafe = false;
}

