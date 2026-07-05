---
id: TASK-1.4
title: Motor Output Driver
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 04:44'
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
- [x] #1 Positive commands drive the forward input with PWM and hold the reverse input low.
- [x] #2 Negative commands drive the reverse input with PWM and hold the forward input low.
- [x] #3 Coast stop is low/low and brake stop is high/high.
- [x] #4 Motor inversion and output scaling affect only physical output polarity and magnitude.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Motor output driver maps signed normalized commands to bidirectional H-bridge drive states in src/motor_output.c. Positive commands PWM the forward input and hold reverse low; negative commands PWM the reverse input and hold forward low; coast stop is low/low and brake stop is high/high. Inversion flips only physical polarity after command clamping, and forward/reverse scaling changes only PWM duty magnitude. Current project direction is proof-of-concept with macOS firmware build validation; Twister tests are not part of the active workflow.
<!-- SECTION:FINAL_SUMMARY:END -->
