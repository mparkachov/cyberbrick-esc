---
id: TASK-2.2
title: MicroPython Toolchain and Device Backup Workflow
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 12:06'
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
  - scripts/mp_prepare_repl.py
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
- [x] #1 `just install` creates `.venv` and installs `mpremote`.
- [x] #2 `just mp-list` lists available MicroPython serial devices.
- [x] #3 `just mp-backup` saves the current board filesystem under gitignored `device-backups/`.
- [x] #4 `just mp-repl` opens the stock MicroPython REPL.
- [x] #5 `DEVICE=...` overrides the default `DEVICE=auto`.
- [x] #6 Filesystem recipes interrupt the running stock app before entering raw REPL.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use `mpremote` only. Do not use `esptool`, `west flash`, or any firmware replacement path for stock locked boards.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The MicroPython toolchain and backup workflow is implemented. `requirements.txt` pins `mpremote>=1.26,<2`; `just install` completed and installed `mpremote 1.28.0`; `just mp-list` lists the connected CyberBrick device at `/dev/cu.usbmodem1101`; and existing gitignored `device-backups/` snapshots contain the board filesystem tree and files. Filesystem and REPL recipes resolve `DEVICE=auto` or an explicit `DEVICE`, send Ctrl-C through `scripts/mp_prepare_repl.py`, and use `mpremote resume` before raw filesystem access so the stock app does not restart before operations. Live serial opening from the Codex sandbox is blocked by macOS permissions, but the workflow has been exercised locally through the successful backup/deploy-blink flow.
<!-- SECTION:FINAL_SUMMARY:END -->
