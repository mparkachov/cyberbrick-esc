#include <errno.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/irq.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/util.h>

#include <cyberbrick_esc/pwm_input.h>

#define ESC_INPUT1_NODE DT_ALIAS(esc_input_1)
#define ESC_INPUT2_NODE DT_ALIAS(esc_input_2)

BUILD_ASSERT(DT_NODE_EXISTS(ESC_INPUT1_NODE), "esc-input-1 devicetree alias is required");
BUILD_ASSERT(DT_NODE_EXISTS(ESC_INPUT2_NODE), "esc-input-2 devicetree alias is required");

struct pwm_input_channel {
	const struct gpio_dt_spec gpio;
	struct gpio_callback callback;
	uint32_t rising_cycle;
	bool rising_seen;
	struct cyberbrick_esc_pulse_sample sample;
};

static struct pwm_input_channel channels[CYBERBRICK_ESC_CHANNEL_COUNT] = {
	{
		.gpio = GPIO_DT_SPEC_GET(ESC_INPUT1_NODE, gpios),
	},
	{
		.gpio = GPIO_DT_SPEC_GET(ESC_INPUT2_NODE, gpios),
	},
};

static bool pulse_width_valid(uint32_t pulse_width_us)
{
	return pulse_width_us >= CONFIG_CYBERBRICK_ESC_MIN_VALID_US &&
	       pulse_width_us <= CONFIG_CYBERBRICK_ESC_MAX_VALID_US;
}

static void pwm_input_callback(const struct device *port,
			       struct gpio_callback *callback, uint32_t pins)
{
	struct pwm_input_channel *channel =
		CONTAINER_OF(callback, struct pwm_input_channel, callback);
	int value;

	ARG_UNUSED(port);
	ARG_UNUSED(pins);

	value = gpio_pin_get_dt(&channel->gpio);
	if (value > 0) {
		channel->rising_cycle = k_cycle_get_32();
		channel->rising_seen = true;
		return;
	}

	if (value == 0 && channel->rising_seen) {
		uint32_t now_cycle = k_cycle_get_32();
		uint32_t pulse_width_us =
			k_cyc_to_us_floor32(now_cycle - channel->rising_cycle);

		channel->rising_seen = false;

		if (pulse_width_valid(pulse_width_us)) {
			channel->sample.pulse_width_us = pulse_width_us;
			channel->sample.timestamp_us = k_uptime_get() * 1000LL;
			channel->sample.valid = true;
		}
	}
}

int cyberbrick_esc_pwm_input_init(void)
{
	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		struct pwm_input_channel *channel = &channels[i];
		int ret;

		if (!gpio_is_ready_dt(&channel->gpio)) {
			return -ENODEV;
		}

		ret = gpio_pin_configure_dt(&channel->gpio, GPIO_INPUT);
		if (ret != 0) {
			return ret;
		}

		gpio_init_callback(&channel->callback, pwm_input_callback,
				   BIT(channel->gpio.pin));

		ret = gpio_add_callback(channel->gpio.port, &channel->callback);
		if (ret != 0) {
			return ret;
		}

		ret = gpio_pin_interrupt_configure_dt(&channel->gpio,
						      GPIO_INT_EDGE_BOTH);
		if (ret != 0) {
			return ret;
		}
	}

	return 0;
}

void cyberbrick_esc_pwm_input_get_samples(
	struct cyberbrick_esc_pulse_sample samples[CYBERBRICK_ESC_CHANNEL_COUNT])
{
	unsigned int key;

	if (samples == NULL) {
		return;
	}

	key = irq_lock();
	for (size_t i = 0; i < CYBERBRICK_ESC_CHANNEL_COUNT; i++) {
		samples[i] = channels[i].sample;
	}
	irq_unlock(key);
}
