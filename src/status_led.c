#include <errno.h>
#include <stddef.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/led_strip.h>
#include <zephyr/sys/util.h>

#include <cyberbrick_esc/status_led.h>

#if IS_ENABLED(CONFIG_CYBERBRICK_ESC_STATUS_LED) && DT_NODE_EXISTS(DT_ALIAS(led_strip))
#define STATUS_LED_HAS_STRIP 1
#define STATUS_LED_NODE DT_ALIAS(led_strip)
#else
#define STATUS_LED_HAS_STRIP 0
#endif

enum status_led_direction {
	STATUS_LED_DIRECTION_NEUTRAL,
	STATUS_LED_DIRECTION_FORWARD,
	STATUS_LED_DIRECTION_REVERSE,
};

struct status_led_state {
	enum status_led_direction direction;
	uint8_t brightness;
};

static int16_t abs_command(int16_t command)
{
	if (command <= CYBERBRICK_ESC_COMMAND_MIN) {
		return CYBERBRICK_ESC_COMMAND_MAX;
	}

	return command < 0 ? -command : command;
}

static uint8_t active_brightness_from_command(int16_t magnitude)
{
	uint32_t min_brightness = CONFIG_CYBERBRICK_ESC_STATUS_LED_MIN_ACTIVE_BRIGHTNESS;
	uint32_t range = 255U - min_brightness;
	uint32_t brightness;

	magnitude = CLAMP(magnitude, 0, CYBERBRICK_ESC_COMMAND_MAX);
	brightness = min_brightness +
		     (range * (uint32_t)magnitude) / CYBERBRICK_ESC_COMMAND_MAX;

	return (uint8_t)CLAMP(brightness, min_brightness, 255U);
}

static struct status_led_state state_from_commands(
	const int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT])
{
	int16_t forward = 0;
	int16_t reverse = 0;

	if (command == NULL) {
		return (struct status_led_state){
			.direction = STATUS_LED_DIRECTION_NEUTRAL,
			.brightness = CONFIG_CYBERBRICK_ESC_STATUS_LED_NEUTRAL_BRIGHTNESS,
		};
	}

	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		if (command[i] > 0) {
			forward = MAX(forward, abs_command(command[i]));
		} else if (command[i] < 0) {
			reverse = MAX(reverse, abs_command(command[i]));
		}
	}

	if (forward > reverse) {
		return (struct status_led_state){
			.direction = STATUS_LED_DIRECTION_FORWARD,
			.brightness = active_brightness_from_command(forward),
		};
	}

	if (reverse > forward) {
		return (struct status_led_state){
			.direction = STATUS_LED_DIRECTION_REVERSE,
			.brightness = active_brightness_from_command(reverse),
		};
	}

	return (struct status_led_state){
		.direction = STATUS_LED_DIRECTION_NEUTRAL,
		.brightness = CONFIG_CYBERBRICK_ESC_STATUS_LED_NEUTRAL_BRIGHTNESS,
	};
}

static int apply_state(struct status_led_state state)
{
#if STATUS_LED_HAS_STRIP
	static const struct device *const strip = DEVICE_DT_GET(STATUS_LED_NODE);
	struct led_rgb pixel = { 0 };

	switch (state.direction) {
	case STATUS_LED_DIRECTION_FORWARD:
		pixel.g = state.brightness;
		break;
	case STATUS_LED_DIRECTION_REVERSE:
		pixel.r = state.brightness;
		break;
	case STATUS_LED_DIRECTION_NEUTRAL:
	default:
		pixel.b = state.brightness;
		break;
	}

	if (!device_is_ready(strip)) {
		return -ENODEV;
	}

	return led_strip_update_rgb(strip, &pixel, 1);
#else
	ARG_UNUSED(state);
	return 0;
#endif
}

int cyberbrick_esc_status_led_init(void)
{
	return cyberbrick_esc_status_led_show_neutral();
}

int cyberbrick_esc_status_led_update(
	const int16_t command[CYBERBRICK_ESC_CHANNEL_COUNT])
{
	return apply_state(state_from_commands(command));
}

int cyberbrick_esc_status_led_show_neutral(void)
{
	return apply_state((struct status_led_state){
		.direction = STATUS_LED_DIRECTION_NEUTRAL,
		.brightness = CONFIG_CYBERBRICK_ESC_STATUS_LED_NEUTRAL_BRIGHTNESS,
	});
}
