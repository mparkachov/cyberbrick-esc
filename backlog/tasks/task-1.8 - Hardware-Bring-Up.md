---
id: TASK-1.8
title: Hardware Bring-Up
status: Done
assignee: []
created_date: '2026-07-04 19:32'
updated_date: '2026-07-05 06:42'
labels:
  - hardware
  - validation
  - safety
milestone: m-0
dependencies:
  - TASK-1.6
  - TASK-1.7
  - TASK-1.10
modified_files:
  - README.md
  - AGENTS.md
  - justfile
parent_task_id: TASK-1
priority: medium
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Flash and validate the MVP firmware on the connected ESP32-C3 device at /dev/tty.usbmodem1101 with motors physically safe.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 just flash flashes the connected device through Zephyr west.
- [ ] #2 just log shows firmware output through screen at 115200 baud.
- [ ] #3 Neutral input arms and 1000/1500/2000 us behavior is verified with motors unloaded or tracks removed.
- [ ] #4 Signal loss and invalid pulses stop motor outputs.
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: codex
created: 2026-07-05 06:15
---
Hardware bring-up attempt on /dev/tty.usbmodem1101 failed before writing flash. esptool detected ESP32-C3 Secure Download Mode with flash encryption enabled and refused to write the plaintext Zephyr binary because forcing it may brick the device. Treat this board as not flashable for the PoC unless a maintainer provides an approved encrypted/signed flashing flow or a different development board without flash encryption enabled.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardware bring-up is closed with a terminal PoC finding, not a successful stock CyberBrick Zephyr flash. The firmware is technically feasible and builds, but the observed stock board at /dev/tty.usbmodem1101 reports ESP32-C3 Secure Download Mode with flash encryption enabled. esptool refused to write the plaintext Zephyr binary, and forcing the write is explicitly out of scope because it may make the device unusable. The board remains functional with its stock MicroPython runtime and REPL after Ctrl-C, so it is not bricked. Continue Zephyr bring-up only on unlocked ESP32-C3/CyberBrick hardware or with an approved signed/encrypted vendor-compatible flashing flow; stock-board experimentation should be treated as a separate MicroPython PoC path.
<!-- SECTION:FINAL_SUMMARY:END -->
