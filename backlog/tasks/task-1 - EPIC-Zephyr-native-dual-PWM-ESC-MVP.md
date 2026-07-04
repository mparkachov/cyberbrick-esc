---
id: TASK-1
title: 'EPIC: Zephyr-native dual PWM ESC MVP'
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-04 20:17'
labels:
  - epic
  - firmware
  - safety
milestone: m-0
dependencies: []
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deliver the MVP firmware profile: two center-neutral RC PWM inputs drive two bidirectional brushed motor outputs with safe boot, neutral-before-arm, failsafe stop, tests, documentation, and hardware validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two standard PWM inputs map to two bidirectional brushed motor outputs in direct dual ESC mode.
- [ ] #2 Boot, initialization failure, missing input, invalid pulse widths, and failsafe recovery all leave motor outputs safe unless neutral arming requirements are met.
- [ ] #3 Project uses Zephyr-native build, Kconfig, devicetree, GPIO, PWM, Ztest, and Twister workflows.
- [ ] #4 README and Backlog records describe the implemented workflow and intentionally unsupported features.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MVP firmware structure, safety mapping, motor output, PWM input capture, integration loop, tests, documentation, and just workflow are implemented. just install resolves Zephyr v4.4.1 and ESP-IDF v6.0.2 into gitignored local folders; ESP-IDF tools, CMake, Ninja, OpenOCD, esptool, and the ESP32-C3 RISC-V toolchain are local under .espressif/.venv. just build produces ESP32-C3 firmware artifacts under build/. Remaining open validation: Zephyr native_sim Twister execution is filtered on macOS because native_sim requires Linux, and hardware flash/log/physical motor validation has not been run.
<!-- SECTION:NOTES:END -->
