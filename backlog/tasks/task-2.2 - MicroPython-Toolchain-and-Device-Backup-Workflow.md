---
id: TASK-2.2
title: MicroPython Toolchain and Device Backup Workflow
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
labels:
  - tooling
  - micropython
  - safety
dependencies:
  - TASK-2.1
modified_files:
  - justfile
  - pyproject.toml
  - uv.lock
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
- [x] #1 `just install` runs `uv sync` and installs `mpremote`.
- [x] #2 `just mp-list` lists available MicroPython serial devices.
- [x] #3 `just mp-backup` saves the current board filesystem under gitignored `device-backups/`.
- [x] #4 `just mp-repl` opens the stock MicroPython REPL.
- [x] #5 `DEVICE=...` overrides the default `DEVICE=auto`.
- [x] #6 Filesystem recipes use stock `mpremote` commands and document that the board must already be REPL-reachable.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use `mpremote` only. Do not use `esptool`, `west flash`, or any firmware replacement path for stock locked boards.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The MicroPython toolchain and backup workflow has been reset to stock tools. `pyproject.toml` declares `mpremote>=1.26,<2`, `uv.lock` records the resolved environment, and `just install` is a thin alias for `uv sync`. Filesystem, REPL, backup, blink, and restore recipes call `uv run mpremote` directly with stock `resume` after manual REPL recovery. When the board is running the stock solid-green app, the documented path is manual miniterm recovery to `>>>`.
<!-- SECTION:FINAL_SUMMARY:END -->
