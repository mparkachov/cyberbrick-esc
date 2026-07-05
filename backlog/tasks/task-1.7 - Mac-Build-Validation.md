---
id: TASK-1.7
title: Mac Build Validation
status: To Do
assignee: []
created_date: '2026-07-04 19:32'
updated_date: '2026-07-04 20:17'
labels:
  - zephyr
  - safety
milestone: m-0
dependencies:
  - TASK-1.3
  - TASK-1.4
  - TASK-1.6
parent_task_id: TASK-1
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Keep validation focused on macOS firmware builds for the proof-of-concept stage. Twister and Ztest suites are intentionally not required unless a maintainer explicitly reintroduces them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `just build` succeeds on macOS after `just install`.
- [ ] #2 No Twister metadata, `testcase.yaml`, or Ztest-only scaffolding is required for the PoC workflow.
- [ ] #3 Firmware validation guidance documents build success as the required software gate at this stage.
- [ ] #4 Hardware-specific behavior is left for manual bring-up validation.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Project direction changed to proof-of-concept Mac-build validation. Twister tests were removed from the active workflow.
<!-- SECTION:NOTES:END -->
