---
id: TASK-1
title: 'EPIC: Zephyr-native dual PWM ESC MVP'
status: To Do
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-04 19:52'
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
Initial MVP implementation added: just/uv Zephyr workflow, app skeleton, safety mapping, motor output, PWM input capture, integration loop, tests, and README updates. Validation currently blocks at missing ESP32-C3 Zephyr SDK/RISC-V toolchain; native_sim Twister discovery works but execution is filtered on macOS because Zephyr native_sim is Linux-only.
<!-- SECTION:NOTES:END -->
