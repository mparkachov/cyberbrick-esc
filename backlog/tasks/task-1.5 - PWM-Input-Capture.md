---
id: TASK-1.5
title: PWM Input Capture
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 04:57'
labels:
  - firmware
  - input
  - safety
milestone: m-0
dependencies:
  - TASK-1.2
parent_task_id: TASK-1
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Capture two hobby PWM inputs on GPIO1 and GPIO0 using Zephyr GPIO interrupts and publish validated pulse samples.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both-edge GPIO interrupts measure high pulse width in microseconds for both channels.
- [x] #2 Only pulses in the configured valid range are accepted.
- [x] #3 Accepted pulses update latest sample width and timestamp.
- [x] #4 The ISR is short, non-blocking, and never updates motor PWM duty.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PWM input capture is implemented in src/pwm_input.c using devicetree aliases esc-input-1 and esc-input-2, mapped in app.overlay to GPIO1 and GPIO0. Each channel configures a GPIO callback with GPIO_INT_EDGE_BOTH, records k_cycle_get_32() on rising edges, converts the falling-edge high interval to microseconds with k_cyc_to_us_floor32(), and publishes the latest accepted sample. pulse_width_valid() accepts only CONFIG_CYBERBRICK_ESC_MIN_VALID_US..CONFIG_CYBERBRICK_ESC_MAX_VALID_US; invalid widths leave the previous sample width and timestamp untouched. The ISR only reads the pin, records timing/sample state, and never calls motor output or PWM duty APIs. Validation: just build succeeded on macOS for esp32c3_devkitm.
<!-- SECTION:FINAL_SUMMARY:END -->
