---
id: TASK-2.7
title: RGB LED ESC Command Feedback
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 17:26'
labels:
  - micropython
  - feedback
  - safety
dependencies:
  - TASK-2.4
  - TASK-2.6
modified_files:
  - micropython/lib/cyberbrick_esc/led.py
  - tests/test_led.py
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
- [x] #1 Neutral final commands show blue.
- [x] #2 Dominant forward command shows green with command-based intensity.
- [x] #3 Dominant reverse command shows red with command-based intensity.
- [x] #4 Exact opposing forward/reverse ties return to blue.
- [x] #5 LED feedback is derived only from final safe commands and does not affect arming, failsafe, or input capture.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use the direct WS2812 candidate-pin driver until the visible LED data pin is confirmed. The LED is proof-of-concept feedback only; it is not a motor output or safety mechanism.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
RGB LED ESC command feedback is implemented as a visual-only mapping from final safe command values to RGB state. Neutral commands and exact opposing direction ties produce blue, dominant positive command magnitude produces green with scaled intensity, and dominant negative command magnitude produces red with scaled intensity. `StatusLed.update()` derives LED state from its command argument only and writes that RGB value to all configured WS2812 candidate buses. The app loop passes `Safety.update(...).commands` to LED feedback after input capture and safety processing. Host LED tests cover pure command-to-color behavior, intensity scaling, tie behavior, configured bus writes, the command-only update surface, and app-loop dataflow.
<!-- SECTION:FINAL_SUMMARY:END -->
