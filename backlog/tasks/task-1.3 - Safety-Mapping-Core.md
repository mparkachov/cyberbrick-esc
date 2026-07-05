---
id: TASK-1.3
title: Safety Mapping Core
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 04:35'
labels:
  - firmware
  - safety
  - test
milestone: m-0
dependencies:
  - TASK-1.2
parent_task_id: TASK-1
priority: high
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement hardware-independent pulse mapping, command clamping, neutral deadband, arming, failsafe, and recovery logic.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 1000 us maps to -1000, 1500 us maps to 0, and 2000 us maps to +1000.
- [x] #2 Neutral deadband maps to zero and command output is clamped to -1000..+1000.
- [x] #3 Invalid pulse widths do not update valid timestamps or command nonzero output.
- [x] #4 Startup and failsafe recovery require both channels valid and neutral for the configured arming time.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Safety mapping core is implemented in src/safety.c and covered by tests/safety. Mapping verifies 1000 us -> -1000, 1500 us -> 0, and 2000 us -> +1000. Deadband, clamping, invalid pulse rejection, neutral-before-arm startup, failsafe transition, and neutral-only recovery are covered. The input sampler only updates valid timestamps for pulse widths inside the configured valid range. Local verification: standalone safety test compiled with cc -std=c11 -Wall -Wextra -Werror and passed; just build succeeded. Twister output is kept under build/twister-out; on this macOS host native_sim is filtered because Zephyr reports it requires Linux.
<!-- SECTION:FINAL_SUMMARY:END -->
