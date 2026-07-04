---
id: TASK-1.5
title: PWM Input Capture
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
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
- [ ] #1 Both-edge GPIO interrupts measure high pulse width in microseconds for both channels.
- [ ] #2 Only pulses in the configured valid range are accepted.
- [ ] #3 Accepted pulses update latest sample width and timestamp.
- [ ] #4 The ISR is short, non-blocking, and never updates motor PWM duty.
<!-- AC:END -->
