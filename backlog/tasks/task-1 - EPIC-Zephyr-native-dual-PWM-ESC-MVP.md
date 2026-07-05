---
id: TASK-1
title: 'EPIC: Zephyr-native dual PWM ESC MVP'
status: Done
assignee: []
created_date: '2026-07-04 19:31'
updated_date: '2026-07-05 06:42'
labels:
  - epic
  - firmware
  - safety
milestone: m-0
dependencies: []
modified_files:
  - README.md
  - AGENTS.md
priority: high
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deliver the MVP firmware profile: two center-neutral RC PWM inputs drive two bidirectional brushed motor outputs with safe boot, neutral-before-arm, failsafe stop, tests, documentation, and hardware validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Two standard PWM inputs map to two bidirectional brushed motor outputs in direct dual ESC mode.
- [x] #2 Boot, initialization failure, missing input, invalid pulse widths, and failsafe recovery all leave motor outputs safe unless neutral arming requirements are met.
- [x] #3 Project uses Zephyr-native build, Kconfig, devicetree, GPIO, PWM, and a macOS-buildable `just build` workflow.
- [x] #4 README and Backlog records describe the implemented workflow and intentionally unsupported features.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MVP firmware structure, safety mapping, motor output, PWM input capture, integration loop, documentation, and just workflow are implemented. just install resolves Zephyr v4.4.1 and ESP-IDF v6.0.2 into gitignored local folders; ESP-IDF tools, CMake, Ninja, OpenOCD, esptool, and the ESP32-C3 RISC-V toolchain are local under .espressif/.venv. just build produces ESP32-C3 firmware artifacts under build/. Project direction is proof-of-concept, not production deployment; Twister tests are not part of the active workflow. Remaining open validation: hardware flash/log/physical motor validation has not been run.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Epic closed as a completed proof-of-concept with a documented hardware limitation. The Zephyr-native dual PWM ESC firmware path was implemented: direct dual center-neutral PWM inputs, safety mapping, neutral-before-arm/failsafe behavior, PWM input capture, bidirectional motor output, RGB motor-state feedback, local Zephyr/ESP-IDF tooling, and macOS just build validation. The PoC is technically feasible but does not currently run on the observed stock CyberBrick board because that board reports ESP32-C3 Secure Download Mode with flash encryption enabled and esptool refuses to flash a plaintext Zephyr binary. The board remains functional with stock MicroPython REPL after Ctrl-C, so it is not bricked. Further Zephyr validation requires unlocked hardware or an approved signed/encrypted vendor-compatible flashing flow; stock-board work should be a separate MicroPython PoC path.
<!-- SECTION:FINAL_SUMMARY:END -->
