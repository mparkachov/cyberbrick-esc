---
id: TASK-1.1
title: Toolchain And Just Workflow
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-04 20:17'
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
- [ ] #1 just install resolves the latest non-RC stable Zephyr tag, initializes or updates .zephyr, and installs Python tooling through uv.
- [ ] #2 just build, just flash, and just log execute the specified Zephyr west and screen workflows.
- [ ] #3 Generated Zephyr workspace, virtualenv, build, and test outputs are ignored by git.
- [ ] #4 just install checks python3, uv, git, dtc, and screen, installs local ESP-IDF CMake/Ninja/tools under .espressif, and reports actionable failures.
<!-- AC:END -->



## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented just install/build/flash/log. just install uses uv, local .venv, .zephyr, .esp-idf, and .espressif; ESP-IDF update is tag-specific and non-recursive to avoid unrelated submodule churn. just build passed for esp32c3_devkitm with local ESP32-C3 toolchain. dtc remains a host prerequisite for Zephyr devicetree compilation.
<!-- SECTION:NOTES:END -->
