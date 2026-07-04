---
id: TASK-1.4
title: Motor Output Driver
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
labels:
  - firmware
  - motor
  - test
milestone: m-0
dependencies:
  - TASK-1.2
parent_task_id: TASK-1
priority: high
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Zephyr PWM-backed bidirectional H-bridge output from signed normalized commands.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Positive commands drive the forward input with PWM and hold the reverse input low.
- [ ] #2 Negative commands drive the reverse input with PWM and hold the forward input low.
- [ ] #3 Coast stop is low/low and brake stop is high/high.
- [ ] #4 Motor inversion and output scaling affect only physical output polarity and magnitude.
<!-- AC:END -->
