#ifndef CYBERBRICK_ESC_PWM_INPUT_H_
#define CYBERBRICK_ESC_PWM_INPUT_H_

#include <cyberbrick_esc/safety.h>

int cyberbrick_esc_pwm_input_init(void);
void cyberbrick_esc_pwm_input_get_samples(
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT]);

#endif

