---
id: TASK-2.5
title: PWM Input Capture
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 12:19'
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
Measure two standard hobby PWM input channels through stock MicroPython GPIO edge interrupts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `Pin.irq` captures rising and falling edges on both input channels.
- [x] #2 Interrupt handlers are short and do not print or intentionally allocate.
- [x] #3 Valid samples include pulse width and timestamp.
- [x] #4 Invalid pulse widths are ignored and do not update the last-valid timestamp.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use `time.ticks_us()` and `time.ticks_diff()` for pulse measurement. Keep hardware-specific pin numbers in config.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PWM input capture is implemented through one `Pin.irq` handler per configured channel using both rising and falling edges. Rising edges store the start timestamp, falling edges compute pulse width with `ticks_diff`, and only 900-2100 us pulses replace the last valid sample timestamp. Host tests use a fake `machine.Pin` and clock to verify both default GPIO1/GPIO0 channels, valid sample width/timestamp capture, stale preservation after malformed pulses, falling-edge ignore behavior, interrupt-disabled snapshots, and the non-printing short IRQ handler shape.
<!-- SECTION:FINAL_SUMMARY:END -->
