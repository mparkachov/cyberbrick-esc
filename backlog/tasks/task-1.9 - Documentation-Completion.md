---
id: TASK-1.9
title: Documentation Completion
status: To Do
assignee: []
created_date: '2026-07-04 19:32'
updated_date: '2026-07-04 20:25'
labels:
  - docs
  - safety
milestone: m-0
dependencies:
  - TASK-1.7
  - TASK-1.8
parent_task_id: TASK-1
priority: medium
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update README for the actual MVP workflow, implemented behavior, validation commands, wiring, and unsupported feature boundaries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 README documents required wiring, 3.3 V signal limits, GPIO pin map, center-neutral behavior, and failsafe behavior.
- [ ] #2 README documents hardware validation precautions for /dev/tty.usbmodem1101.
- [ ] #3 README clearly lists intentionally unsupported protocols and rover/autonomy features.
- [ ] #4 README documents just install, just build, just clean, just flash, just log, and the PoC macOS build-validation workflow.
<!-- AC:END -->
