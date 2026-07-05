---
id: TASK-1.6
title: Closed ESC Integration
status: Done
assignee: []
created_date: '2026-07-04 19:32'
updated_date: '2026-07-05 05:00'
labels:
  - firmware
  - integration
  - safety
milestone: m-0
dependencies:
  - TASK-1.3
  - TASK-1.4
  - TASK-1.5
parent_task_id: TASK-1
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Connect PWM input, safety, and motor output into direct dual ESC behavior in the main control loop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Input 1 controls Motor 1 and Input 2 controls Motor 2 in direct mode.
- [x] #2 Missing or malformed input stops both motors according to failsafe policy.
- [x] #3 Initialization failures leave outputs safe.
- [x] #4 No board-specific pin numbers appear outside devicetree overlays.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Closed ESC integration is implemented in src/main.c. The control loop reads two PWM input samples, passes them to safety in channel order, and applies the resulting two-command array directly to motor output, so Input 1 drives Motor 1 and Input 2 drives Motor 2. Missing or malformed input is handled by safety.c as failsafe, producing neutral zero commands for both channels before motor output apply. Initialization failures leave outputs safe: motor output init failure and PWM input init failure both attempt motor_output_stop() before returning, and motor_output_init() stops outputs after successful device readiness checks. Source and build config contain no board-specific pin numbers; hardware pins remain in app.overlay. Validation: just build succeeded on macOS for esp32c3_devkitm and git diff --check passed.
<!-- SECTION:FINAL_SUMMARY:END -->
