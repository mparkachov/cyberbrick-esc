---
id: TASK-1.9
title: Documentation Completion
status: Done
assignee: []
created_date: '2026-07-04 19:32'
updated_date: '2026-07-05 06:42'
labels:
  - docs
  - safety
milestone: m-0
dependencies:
  - TASK-1.7
  - TASK-1.8
modified_files:
  - README.md
  - AGENTS.md
parent_task_id: TASK-1
priority: medium
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update README for the actual MVP workflow, implemented behavior, validation commands, wiring, and unsupported feature boundaries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README documents required wiring, 3.3 V signal limits, GPIO pin map, center-neutral behavior, and failsafe behavior.
- [x] #2 README documents hardware validation precautions for /dev/tty.usbmodem1101.
- [x] #3 README clearly lists intentionally unsupported protocols and rover/autonomy features.
- [x] #4 README documents just install, just build, just clean, just flash, just log, and the PoC macOS build-validation workflow.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Documentation updated for the implemented PoC and final milestone result. README documents the just workflow, macOS build validation, wiring and pin map, 3.3 V signal limits, center-neutral behavior, failsafe behavior, unsupported protocols/features, hardware validation precautions, RGB visual feedback, and the observed stock CyberBrick limitation. The PoC is technically feasible and buildable, but the observed stock CyberBrick board cannot run the Zephyr image via plaintext flashing because it reports ESP32-C3 Secure Download Mode with flash encryption enabled. The board remains functional with stock MicroPython REPL; follow-up requires unlocked hardware, an approved vendor-compatible signed/encrypted flow, or a separate MicroPython PoC path.
<!-- SECTION:FINAL_SUMMARY:END -->
