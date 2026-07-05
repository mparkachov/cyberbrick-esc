#ifndef CYBERBRICK_ESC_STATUS_LED_H_
#define CYBERBRICK_ESC_STATUS_LED_H_

#include <stdint.h>

#include <cyberbrick_esc/safety.h>

int cyberbrick_esc_status_led_init(void);
int cyberbrick_esc_status_led_update(
	const int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT]);
int cyberbrick_esc_status_led_show_neutral(void);

#endif
