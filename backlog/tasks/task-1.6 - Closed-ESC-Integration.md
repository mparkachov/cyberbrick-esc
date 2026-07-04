---
id: TASK-1.6
title: Closed ESC Integration
status: To Do
assignee: []
created_date: '2026-07-04 19:32'
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
- [ ] #1 Input 1 controls Motor 1 and Input 2 controls Motor 2 in direct mode.
- [ ] #2 Missing or malformed input stops both motors according to failsafe policy.
- [ ] #3 Initialization failures leave outputs safe.
- [ ] #4 No board-specific pin numbers appear outside devicetree overlays.
<!-- AC:END -->
