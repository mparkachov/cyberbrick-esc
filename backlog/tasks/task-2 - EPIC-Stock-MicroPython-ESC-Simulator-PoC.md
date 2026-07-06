---
id: TASK-2
title: 'EPIC: Stock MicroPython ESC Simulator PoC'
status: In Progress
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
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
- pyproject.toml
- uv.lock
- micropython/
- tests/
priority: high
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prove the stock CyberBrick MicroPython runtime can host the ESC simulator path without replacing firmware: persistent blink first, then two PWM inputs mapped through the same center-neutral safety behavior into RGB LED command feedback.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Phase 1 stock-tool workflow is reliable: manual REPL recovery, RAM blink, persistent boot blink, and restore stock all use `uv run mpremote` or documented miniterm.
- [x] #2 Simulator reads both input channels on GPIO1 and GPIO0 and rejects invalid pulse widths.
- [x] #3 Safety mapping matches 1000 us -> -1000, 1500 us -> 0, 2000 us -> +1000, with neutral-before-arm and failsafe recovery.
- [ ] #4 Phase 2 simulator deployment reflects final safe commands after stock-tool blink/restore is validated: blue neutral, green forward, red reverse, and blue on exact opposing ties.
- [x] #5 Documentation explains backup, deploy, restore, wiring, signal limits, no plaintext flashing, and unsupported features.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep this as stock-runtime MicroPython work on `main`. The previous Zephyr implementation is preserved on `origin/backup/zephyr`; do not reintroduce plaintext flashing for stock locked boards. This milestone is visual-first and must not drive GPIO4-GPIO7 motor outputs.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
This epic remains open for Phase 2 simulator deployment, but the stock-tool Phase 1 is now validated. Earlier live simulator probes showed that the dormant simulator library can capture 1000/1500/2000 us pulses and compute the expected blue/green/red LED states, but persistent simulator deploy is paused. The repo now has a confirmed `uv`-managed workflow using stock `mpremote`, manual miniterm recovery from the stock solid-green app, RAM blink, persistent boot blink, and restore-to-stock. Probe workflows and simulator deploy recipes are removed from the active workflow. Phase 2 may resume simulator deployment on this stock-tool base.
<!-- SECTION:FINAL_SUMMARY:END -->
