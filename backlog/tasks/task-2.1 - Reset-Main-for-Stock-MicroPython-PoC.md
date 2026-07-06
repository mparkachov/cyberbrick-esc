---
id: TASK-2.1
title: Reset Main for Stock MicroPython PoC
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
labels:
  - micropython
  - cleanup
dependencies: []
modified_files:
  - README.md
  - AGENTS.md
  - justfile
  - pyproject.toml
  - uv.lock
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
- [x] #1 Active Zephyr app/toolchain files are removed from `main`.
- [x] #2 README and AGENTS state that `backup/zephyr` preserves the old implementation.
- [x] #3 No flashing workflow is presented as valid for stock locked CyberBrick boards.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Remove the Zephyr build surface from the active branch, including CMake, Kconfig, app overlay, source/include modules, and Zephyr install scripts. Keep backlog history for the completed Zephyr PoC.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
`main` has been reset to a stock MicroPython PoC surface. The active tracked files no longer include the Zephyr app/build surface (`CMakeLists.txt`, `Kconfig`, `prj.conf`, `app.overlay`, `src/`, `include/`, or Zephyr install scripts). README and AGENTS document that the previous Zephyr implementation is preserved on `origin/backup/zephyr`, and both documents preserve the warning that stock locked CyberBrick boards must not be force-flashed with plaintext firmware. Verified with tracked-file inspection and documentation search.

The 2026-07-06 workflow reset replaced the earlier requirements-file tooling surface with a `uv`-managed stock-tool workflow. `just` is now only a thin alias layer over `uv run mpremote` and `uv run python`.
<!-- SECTION:FINAL_SUMMARY:END -->
