---
id: TASK-2.6
title: Safety Mapping Core
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
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
- [ ] #1 1000 us maps to `-1000`, 1500 us maps to `0`, and 2000 us maps to `+1000`.
- [ ] #2 Neutral deadband maps to zero command.
- [ ] #3 Startup and failsafe recovery require valid neutral input before arming.
- [ ] #4 Missing, stale, invalid, or malformed input produces safe zero commands.
- [ ] #5 Host safety tests cover mapping, arming, and failsafe recovery.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep this module importable on the host so `just test` can validate pure logic without board hardware.
<!-- SECTION:NOTES:END -->
