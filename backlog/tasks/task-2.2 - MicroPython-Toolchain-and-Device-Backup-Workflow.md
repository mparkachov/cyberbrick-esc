---
id: TASK-2.2
title: MicroPython Toolchain and Device Backup Workflow
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - tooling
  - micropython
  - safety
dependencies:
  - TASK-2.1
modified_files:
  - justfile
  - requirements.txt
  - .gitignore
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10200
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install and verify local MicroPython upload tooling and ensure the stock board filesystem is backed up before deployment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `just install` creates `.venv` and installs `mpremote`.
- [ ] #2 `just mp-list` lists available MicroPython serial devices.
- [ ] #3 `just mp-backup` saves the current board filesystem under gitignored `device-backups/`.
- [ ] #4 `just mp-repl` opens the stock MicroPython REPL.
- [ ] #5 `DEVICE=...` overrides the default `DEVICE=auto`.
- [ ] #6 Filesystem recipes interrupt the running stock app before entering raw REPL.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use `mpremote` only. Do not use `esptool`, `west flash`, or any firmware replacement path for stock locked boards.
<!-- SECTION:NOTES:END -->
