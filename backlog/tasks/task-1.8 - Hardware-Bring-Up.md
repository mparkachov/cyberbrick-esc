---
id: TASK-1.8
title: Hardware Bring-Up
status: To Do
assignee: []
created_date: '2026-07-04 19:32'
labels:
  - hardware
  - validation
  - safety
milestone: m-0
dependencies:
  - TASK-1.6
  - TASK-1.7
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
