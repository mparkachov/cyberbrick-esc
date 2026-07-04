---
id: TASK-1.7
title: Tests And Twister
status: To Do
assignee: []
created_date: '2026-07-04 19:32'
labels:
  - test
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
Add Ztest/Twister coverage for hardware-independent mapping, safety state, and motor output state generation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 west twister -T tests covers pulse mapping, deadband, clamping, and invalid rejection.
- [ ] #2 west twister -T tests covers neutral arming, failsafe transition, and neutral-required recovery.
- [ ] #3 west twister -T tests covers brake/coast, forward/reverse output generation, inversion, and scaling.
- [ ] #4 Tests run without physical hardware.
<!-- AC:END -->
