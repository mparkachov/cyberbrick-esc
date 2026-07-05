---
id: TASK-1.1
title: Toolchain And Just Workflow
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 04:26'
labels:
  - tooling
  - zephyr
milestone: m-0
dependencies: []
parent_task_id: TASK-1
priority: high
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the required just recipes for installing Zephyr tooling, building, flashing, and serial logging while keeping the Zephyr workspace gitignored.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 just install resolves the latest non-RC stable Zephyr tag, initializes or updates .zephyr, and installs Python tooling through uv.
- [x] #2 Generated Zephyr workspace, virtualenv, build, and test outputs are ignored by git.
- [x] #3 just install checks python3, uv, git, dtc, and screen, installs local ESP-IDF CMake/Ninja/tools under .espressif, and reports actionable failures.
- [x] #4 just build, just clean, just flash, and just log execute the specified Zephyr build cleanup, west, and screen workflows.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented just install/build/flash/log. just install uses uv, local .venv, .zephyr, .esp-idf, and .espressif; ESP-IDF update is tag-specific and non-recursive to avoid unrelated submodule churn. just build passed for esp32c3_devkitm with local ESP32-C3 toolchain. dtc remains a host prerequisite for Zephyr devicetree compilation.

Added just clean to remove build/ and build-only ccache data without removing installed .venv, .zephyr, .esp-idf, or .espressif toolchain/workspace folders.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Toolchain workflow is implemented and verified. just install resolves stable Zephyr and ESP-IDF tags, uses uv for Python packages, installs local ESP-IDF CMake/Ninja/OpenOCD/esptool/RISC-V tools, and keeps generated workspaces ignored. just build passed for esp32c3_devkitm. just clean was executed and removed build/ plus build ccache while preserving installed toolchain/workspace folders. just flash/log command surfaces were verified by dry-run to use Zephyr west and screen with /dev/tty.usbmodem1101.
<!-- SECTION:FINAL_SUMMARY:END -->
