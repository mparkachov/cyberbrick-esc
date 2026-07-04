---
id: TASK-1.2
title: Zephyr App Skeleton
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
labels:
  - firmware
  - zephyr
milestone: m-0
dependencies:
  - TASK-1.1
parent_task_id: TASK-1
priority: high
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the minimal Zephyr application structure, configuration, devicetree overlay, module headers, and safe startup path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CMakeLists.txt, Kconfig, prj.conf, app.overlay, src, include/cyberbrick_esc, and tests scaffolding exist.
- [ ] #2 Motor outputs are initialized safe before input capture is started.
- [ ] #3 No board pin numbers are hard-coded in business logic.
- [ ] #4 just build succeeds for esp32c3_devkitm once tooling is installed.
<!-- AC:END -->
