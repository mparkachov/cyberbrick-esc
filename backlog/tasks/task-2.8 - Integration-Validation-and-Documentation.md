---
id: TASK-2.8
title: Integration, Validation, and Documentation
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - documentation
  - validation
  - micropython
dependencies:
  - TASK-2.2
  - TASK-2.3
  - TASK-2.5
  - TASK-2.6
  - TASK-2.7
modified_files:
  - README.md
  - AGENTS.md
  - justfile
parent_task_id: TASK-2
milestone: m-1
priority: medium
ordinal: 10800
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the MicroPython simulator milestone usable, recoverable, and documented.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `just deploy` installs `main.py` and `cyberbrick_esc` library files.
- [ ] #2 README documents wiring, 3.3 V signal limits, blink, deploy, backup, restore, failsafe behavior, and intentionally unsupported features.
- [ ] #3 `just test` passes host safety tests.
- [ ] #4 Documentation states that GPIO4-GPIO7 motor outputs are not driven in this milestone.
- [ ] #5 Documentation preserves the warning against force-flashing plaintext firmware to locked stock boards.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hardware validation requires a connected stock board in MicroPython REPL mode. Keep validation steps motors-disconnected and visual-first.
<!-- SECTION:NOTES:END -->
