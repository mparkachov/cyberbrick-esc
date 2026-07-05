---
id: TASK-2.7
title: RGB LED ESC Command Feedback
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - micropython
  - feedback
  - safety
dependencies:
  - TASK-2.4
  - TASK-2.6
modified_files:
  - micropython/lib/cyberbrick_esc/led.py
  - tests/test_safety.py
parent_task_id: TASK-2
milestone: m-1
priority: medium
ordinal: 10700
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Show final safe ESC simulator commands on the onboard RGB LED.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Neutral final commands show blue.
- [ ] #2 Dominant forward command shows green with command-based intensity.
- [ ] #3 Dominant reverse command shows red with command-based intensity.
- [ ] #4 Exact opposing forward/reverse ties return to blue.
- [ ] #5 LED feedback is derived only from final safe commands and does not affect arming, failsafe, or input capture.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use one NeoPixel on GPIO8. The LED is proof-of-concept feedback only; it is not a motor output or safety mechanism.
<!-- SECTION:NOTES:END -->
