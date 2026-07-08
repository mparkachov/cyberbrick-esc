---
id: TASK-2.4
title: ESC Simulator App Skeleton
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
labels:
  - micropython
  - architecture
dependencies:
  - TASK-2.1
modified_files:
  - micropython/main.py
  - micropython/lib/cyberbrick_esc/config.py
  - micropython/lib/cyberbrick_esc/app.py
  - tests/test_app_skeleton.py
parent_task_id: TASK-2
milestone: m-1
priority: medium
ordinal: 10400
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the MicroPython app entrypoint, package layout, and safe default
configuration for the initial visual ESC simulator.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Config defines GPIO1/GPIO0 inputs and the onboard WS2812 LED on GPIO8.
- [x] #2 Config defines 900-2100 us valid range, 1000/1500/2000 us command mapping, 50 us deadband, 150 ms failsafe, 1000 ms neutral arming, and capture-driven nominal 50 Hz safety evaluation.
- [x] #3 App entrypoint initializes LED, input capture, and safety mapping.
- [x] #4 At the initial visual-simulator stage, no motor output pins were configured or written.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The observed stock `boot.py` runs the vendor app directly, so Phase 1 does not deploy the simulator app skeleton. Keep this code dormant until the stock-tool blink and restore workflow is reliable.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The MicroPython ESC simulator app skeleton remains in place for Phase 2.
`main.py` starts `cyberbrick_esc.app.main()`, and the app initializes status LED
feedback, PWM input capture, and safety mapping before running a capture-driven
loop. Native capture nominally evaluates safety at 50 Hz and samples each
channel at 25 Hz, with no additional loop sleep. Configuration centralizes
GPIO1/GPIO0 inputs, the onboard WS2812 LED on GPIO8, pulse timing defaults,
failsafe timing, neutral arming, and capture timeout. Host tests verify the
default skeleton configuration and that reserved motor pins GPIO4-GPIO7 are not
configured or directly referenced by MicroPython source. The later unloaded
GPIO output probe is tracked separately in TASK-2.10.
<!-- SECTION:FINAL_SUMMARY:END -->
