---
id: TASK-2.4
title: ESC Simulator App Skeleton
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 12:14'
labels:
  - micropython
  - architecture
dependencies:
  - TASK-2.1
modified_files:
  - micropython/boot.py
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
Create the MicroPython app entrypoint, package layout, and safe default configuration for the visual ESC simulator.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Config defines GPIO1/GPIO0 inputs and the onboard WS2812 LED on GPIO8.
- [x] #2 Config defines 900-2100 us valid range, 1000/1500/2000 us command mapping, 50 us deadband, 150 ms failsafe, 1000 ms neutral arming, and 200 Hz loop.
- [x] #3 App entrypoint initializes LED, input capture, and safety mapping.
- [x] #4 No motor output pins are configured or written.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The observed stock `boot.py` runs the vendor app directly, so this milestone uses a reversible `boot.py` override that executes the PoC `main.py`.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The MicroPython ESC simulator app skeleton is in place. The reversible PoC `boot.py` executes `main.py`, `main.py` starts `cyberbrick_esc.app.main()`, and the app initializes status LED feedback, PWM input capture, and safety mapping before running the 200 Hz control loop. Configuration centralizes GPIO1/GPIO0 inputs, the onboard WS2812 LED on GPIO8, pulse timing defaults, failsafe timing, neutral arming, and loop rate. Host tests now verify the default skeleton configuration and that reserved motor pins GPIO4-GPIO7 are not configured or directly referenced by MicroPython source.
<!-- SECTION:FINAL_SUMMARY:END -->
