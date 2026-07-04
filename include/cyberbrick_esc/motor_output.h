#ifndef CYBERBRICK_ESC_MOTOR_OUTPUT_H_
#define CYBERBRICK_ESC_MOTOR_OUTPUT_H_

#include <stdbool.h>
#include <stdint.h>

#include <cyberbrick_esc/safety.h>

enum cyberbrick_esc_stop_mode {
	CYBERBRICK_ESC_STOP_MODE_COAST,
	CYBERBRICK_ESC_STOP_MODE_BRAKE,
};

enum cyberbrick_esc_pin_drive_mode {
	CYBERBRICK_ESC_PIN_LOW,
	CYBERBRICK_ESC_PIN_HIGH,
	CYBERBRICK_ESC_PIN_PWM,
};

struct cyberbrick_esc_motor_config {
	bool inverted;
	uint16_t max_forward_permille;
	uint16_t max_reverse_permille;
	enum cyberbrick_esc_stop_mode stop_mode;
};

struct cyberbrick_esc_pin_drive {
	enum cyberbrick_esc_pin_drive_mode mode;
	uint16_t duty_permille;
};

struct cyberbrick_esc_motor_state {
	struct cyberbrick_esc_pin_drive input_a;
	struct cyberbrick_esc_pin_drive input_b;
};

void cyberbrick_esc_motor_make_state(int16_t command,
				     const struct cyberbrick_esc_motor_config *config,
				     struct cyberbrick_esc_motor_state *state);

int cyberbrick_esc_motor_output_init(void);
int cyberbrick_esc_motor_output_apply(const int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT]);
int cyberbrick_esc_motor_output_stop(void);

#endif

