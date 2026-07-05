---
id: TASK-2.5
title: PWM Input Capture
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - micropython
  - input
  - safety
dependencies:
  - TASK-2.4
modified_files:
  - micropython/lib/cyberbrick_esc/pwm_input.py
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
- [ ] #1 `Pin.irq` captures rising and falling edges on both input channels.
- [ ] #2 Interrupt handlers are short and do not print or intentionally allocate.
- [ ] #3 Valid samples include pulse width and timestamp.
- [ ] #4 Invalid pulse widths are ignored and do not update the last-valid timestamp.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use `time.ticks_us()` and `time.ticks_diff()` for pulse measurement. Keep hardware-specific pin numbers in config.
<!-- SECTION:NOTES:END -->
