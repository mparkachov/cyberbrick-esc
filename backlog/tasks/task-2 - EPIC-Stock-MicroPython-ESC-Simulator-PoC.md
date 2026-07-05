---
id: TASK-2
title: 'EPIC: Stock MicroPython ESC Simulator PoC'
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - epic
  - micropython
  - safety
milestone: m-1
dependencies: []
modified_files:
  - README.md
  - AGENTS.md
  - justfile
  - micropython/
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prove the stock CyberBrick MicroPython runtime can host the ESC simulator path without replacing firmware: persistent blink first, then two PWM inputs mapped through the same center-neutral safety behavior into RGB LED command feedback.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Persistent onboard LED blink deploys as `main.py` and runs after board reset or power-on without a host command.
- [ ] #2 Simulator reads both input channels on GPIO1 and GPIO0 and rejects invalid pulse widths.
- [ ] #3 Safety mapping matches 1000 us -> -1000, 1500 us -> 0, 2000 us -> +1000, with neutral-before-arm and failsafe recovery.
- [ ] #4 RGB LED reflects final safe commands: blue neutral, green forward, red reverse, and blue on exact opposing ties.
- [ ] #5 Documentation explains backup, deploy, restore, wiring, signal limits, no plaintext flashing, and unsupported features.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep this as stock-runtime MicroPython work on `main`. The previous Zephyr implementation is preserved on `origin/backup/zephyr`; do not reintroduce plaintext flashing for stock locked boards. This milestone is visual-first and must not drive GPIO4-GPIO7 motor outputs.
<!-- SECTION:NOTES:END -->
