---
id: TASK-1.10
title: RGB LED Motor State Feedback
status: Done
assignee: []
created_date: '2026-07-05 05:08'
updated_date: '2026-07-05 06:07'
labels:
  - firmware
  - feedback
  - safety
dependencies:
  - TASK-1.6
  - TASK-1.7
modified_files:
  - CMakeLists.txt
  - Kconfig
  - app.overlay
  - src/main.c
  - src/status_led.c
  - include/cyberbrick_esc/status_led.h
  - README.md
  - AGENTS.md
parent_task_id: TASK-1
priority: medium
ordinal: 8500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add board LED visual feedback for proof-of-concept motor behavior testing. The onboard multi-color LED should show what the firmware would command the motors to do while motors are disconnected or the vehicle is physically safe.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 On boot and whenever both motor commands are neutral, the board LED is blue to indicate powered, neutral, and motors should not be moving.
- [x] #2 When either motor command is forward, the board LED is green, with intensity reflecting commanded forward speed.
- [x] #3 When either motor command is reverse, the board LED is red, with intensity reflecting commanded reverse speed.
- [x] #4 If channels disagree in direction, the LED behavior is deterministic and documented, for example using the dominant absolute command or a safe neutral/error indication.
- [x] #5 LED hardware pins or PWM channels are described through devicetree/Kconfig and no board-specific LED pin numbers are hard-coded in business logic.
- [x] #6 The feature does not affect safety, arming, failsafe, input capture, or motor output commands; it is visual feedback only.
- [x] #7 just build succeeds on macOS.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use Zephyr LED/PWM/GPIO APIs as appropriate for the actual board LED hardware. Treat this as PoC visual feedback, not a production status indicator. Prefer deriving LED state from the final safe motor command array after safety processing so it reflects what would happen to connected motors.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented PoC RGB motor-state feedback using Zephyr's LED strip API and the ESP32-C3 onboard WS2812 devicetree wiring. The LED is initialized blue at boot and then follows the final safe motor command array after safety processing: dominant forward command shows green with speed-based brightness, dominant reverse command shows red with speed-based brightness, and neutral or exact mixed ties show blue. LED update failures are logged and disable only visual feedback; they do not affect arming, failsafe, input capture, or motor output commands. README and AGENTS document the behavior for future work. Verified with just build on macOS.
<!-- SECTION:FINAL_SUMMARY:END -->
