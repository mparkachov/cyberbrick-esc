---
id: TASK-1.1
title: Toolchain And Just Workflow
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
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
- [ ] #2 just install checks python3, uv, git, cmake, ninja, dtc, screen, and ESP32-C3 toolchain availability with actionable failures.
- [ ] #3 just build, just flash, and just log execute the specified Zephyr west and screen workflows.
- [ ] #4 Generated Zephyr workspace, virtualenv, build, and test outputs are ignored by git.
<!-- AC:END -->
