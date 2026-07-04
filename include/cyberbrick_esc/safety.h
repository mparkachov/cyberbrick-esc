#ifndef CYBERBRICK_ESC_SAFETY_H_
#define CYBERBRICK_ESC_SAFETY_H_

#include <stdbool.h>
#include <stdint.h>

#define CYBERBRICK_ESC_CHANNEL_COUNT 2
#define CYBERBRICK_ESC_COMMAND_MIN (-1000)
#define CYBERBRICK_ESC_COMMAND_NEUTRAL 0
#define CYBERBRICK_ESC_COMMAND_MAX 1000

struct cyberbrick_esc_pulse_sample {
	bool valid;
	uint32_t pulse_width_us;
	int64_t timestamp_us;
};

struct cyberbrick_esc_safety_config {
	uint32_t input_timeout_us;
	uint32_t arming_time_us;
	uint32_t min_valid_us;
	uint32_t max_valid_us;
	uint32_t min_command_us;
	uint32_t neutral_us;
	uint32_t max_command_us;
	uint32_t deadband_us;
};

struct cyberbrick_esc_safety {
	bool armed;
	bool failsafe;
	bool neutral_pending;
	int64_t neutral_since_us;
};

struct cyberbrick_esc_safety_output {
	int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT];
	bool armed;
	bool failsafe;
};

void cyberbrick_esc_safety_init(struct cyberbrick_esc_safety *safety);
int cyberbrick_esc_map_pulse_us(const struct cyberbrick_esc_safety_config *config,
				uint32_t pulse_width_us, int16_t *command);
void cyberbrick_esc_safety_update(struct cyberbrick_esc_safety *safety,
				  const struct cyberbrick_esc_safety_config *config,
				  const struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT],
				  int64_t now_us,
				  struct cyberbrick_esc_safety_output *output);

#endif

