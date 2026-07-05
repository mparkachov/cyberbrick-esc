---
id: TASK-2.6
title: Safety Mapping Core
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 17:20'
labels:
  - micropython
  - safety
dependencies:
  - TASK-2.4
modified_files:
  - micropython/lib/cyberbrick_esc/safety.py
  - tests/test_safety.py
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10600
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Port the Zephyr PoC safety behavior into pure MicroPython-compatible logic.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 1000 us maps to `-1000`, 1500 us maps to `0`, and 2000 us maps to `+1000`.
- [x] #2 Neutral deadband maps to zero command.
- [x] #3 Startup and failsafe recovery require valid neutral input before arming.
- [x] #4 Missing, stale, invalid, or malformed input produces safe zero commands.
- [x] #5 Host safety tests cover mapping, arming, and failsafe recovery.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep this module importable on the host so `just test` can validate pure logic without board hardware.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The pure MicroPython safety core now enforces the center-neutral ESC mapping and safe-state rules with host-testable logic. `map_pulse_us()` maps 1000/1500/2000 us to -1000/0/+1000, applies the neutral deadband, and rejects malformed pulse values. `Safety.update()` requires both channels to provide valid fresh neutral input before startup arming or failsafe recovery, returns zero commands for unarmed state, and disarms to zero commands on missing, stale, invalid, or malformed input. Host tests cover mapping, deadband, startup arming, failsafe recovery, object-backed samples, and malformed sample cases.
<!-- SECTION:FINAL_SUMMARY:END -->
