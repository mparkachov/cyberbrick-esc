---
id: TASK-1.3
title: Safety Mapping Core
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
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
- [ ] #1 1000 us maps to -1000, 1500 us maps to 0, and 2000 us maps to +1000.
- [ ] #2 Neutral deadband maps to zero and command output is clamped to -1000..+1000.
- [ ] #3 Invalid pulse widths do not update valid timestamps or command nonzero output.
- [ ] #4 Startup and failsafe recovery require both channels valid and neutral for the configured arming time.
<!-- AC:END -->
