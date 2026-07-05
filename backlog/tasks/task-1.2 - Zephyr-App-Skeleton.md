---
id: TASK-1.2
title: Zephyr App Skeleton
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 04:29'
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
- [x] #1 CMakeLists.txt, Kconfig, prj.conf, app.overlay, src, include/cyberbrick_esc, and tests scaffolding exist.
- [x] #2 Motor outputs are initialized safe before input capture is started.
- [x] #3 No board pin numbers are hard-coded in business logic.
- [x] #4 just build succeeds for esp32c3_devkitm once tooling is installed.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Zephyr app skeleton is in place with CMake/Kconfig/prj.conf/app.overlay, src and include modules, plus tests scaffolding. Startup initializes safety and motor outputs, drives outputs safe, and only then starts PWM input capture; init failures leave outputs stopped. Board pins are confined to devicetree overlay aliases. just build completed successfully for esp32c3_devkitm and produced build/zephyr/zephyr.elf and zephyr.bin.
<!-- SECTION:FINAL_SUMMARY:END -->
