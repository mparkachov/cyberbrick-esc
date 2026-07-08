---
id: TASK-2.5
title: PWM Input Capture
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-08 00:00'
labels:
  - micropython
  - input
  - safety
dependencies:
  - TASK-2.4
modified_files:
  - micropython/lib/cyberbrick_esc/pwm_input.py
  - tests/test_pwm_input.py
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measure two standard hobby PWM input channels through the most reliable capture
API exposed by the stock MicroPython runtime.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Native `machine.time_pulse_us` capture alternates between both input channels.
- [x] #2 No scheduled Python GPIO interrupt handler is used for edge timestamps.
- [x] #3 Valid samples include pulse width and timestamp.
- [x] #4 Invalid pulse widths are ignored and do not update the last-valid timestamp.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use native `machine.time_pulse_us` for pulse measurement and `time.ticks_us`
for last-valid timestamps. Keep hardware-specific pin numbers in config.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardware investigation replaced the original scheduled `Pin.irq` path. Scope
comparison showed stable source pulses while Python callback timestamps moved
substantially under runtime load. The active implementation alternates
GPIO1/GPIO0 through native `machine.time_pulse_us`, reuses sample objects, and
keeps the three-sample median. Only 900-2100 us measurements replace the
last-valid width and timestamp; timeouts and malformed measurements are
ignored until freshness expires. Host tests verify alternating channel order,
native call configuration, initial timeout behavior, stale preservation,
median rejection, and persistent command changes. Native polling remains
preemptible and is explicitly documented as a stock-runtime PoC limitation.
<!-- SECTION:FINAL_SUMMARY:END -->
