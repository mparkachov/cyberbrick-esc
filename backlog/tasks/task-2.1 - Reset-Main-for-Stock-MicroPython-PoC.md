---
id: TASK-2.1
title: Reset Main for Stock MicroPython PoC
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - micropython
  - cleanup
dependencies: []
modified_files:
  - README.md
  - AGENTS.md
  - justfile
  - requirements.txt
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10100
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make `main` a clean stock MicroPython PoC while preserving the prior Zephyr implementation on `origin/backup/zephyr`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Active Zephyr app/toolchain files are removed from `main`.
- [ ] #2 README and AGENTS state that `backup/zephyr` preserves the old implementation.
- [ ] #3 No flashing workflow is presented as valid for stock locked CyberBrick boards.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Remove the Zephyr build surface from the active branch, including CMake, Kconfig, app overlay, source/include modules, and Zephyr install scripts. Keep backlog history for the completed Zephyr PoC.
<!-- SECTION:NOTES:END -->
