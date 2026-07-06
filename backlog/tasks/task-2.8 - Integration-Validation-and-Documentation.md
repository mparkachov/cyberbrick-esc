---
id: TASK-2.8
title: Integration, Validation, and Documentation
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
labels:
  - documentation
  - validation
  - micropython
dependencies:
  - TASK-2.2
  - TASK-2.3
  - TASK-2.5
  - TASK-2.6
  - TASK-2.7
modified_files:
  - README.md
  - AGENTS.md
  - justfile
  - pyproject.toml
  - uv.lock
  - micropython/examples/blink_boot.py
  - micropython/examples/blink_main.py
parent_task_id: TASK-2
milestone: m-1
priority: medium
ordinal: 10800
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the MicroPython simulator milestone usable, recoverable, and documented.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `uv sync`, `uv run mpremote connect list`, and thin `just` aliases are the only active tooling path.
- [x] #2 README documents manual miniterm REPL recovery, RAM blink, persistent blink, restore stock, wiring, 3.3 V signal limits, and intentionally unsupported features.
- [x] #3 `just test` passes through `uv run python`.
- [x] #4 Documentation states that GPIO4-GPIO7 motor outputs are not driven in this milestone.
- [x] #5 Documentation preserves the warning against force-flashing plaintext firmware to locked stock boards.
- [x] #6 Phase 1 hardware validation passes: RAM blink, persistent boot blink after power-cycle, and restore stock to solid green.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hardware validation requires a connected stock board in MicroPython REPL mode. Keep validation steps motors-disconnected and visual-first.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Integration is complete for the stock-tool Phase 1 reset. The active path is now `uv` plus stock `mpremote`, with `just` only as thin aliases. Manual miniterm recovery is documented as the bridge from the stock solid-green app to REPL. `uv run python -m unittest discover -s tests`, `just test`, `just --list`, and `uv run mpremote connect list` pass. Hardware validation is confirmed: RAM blink works, persistent boot blink works after reset or power-cycle, and restore stock returns the board to solid green. Simulator deploy and hardware PWM validation are deferred to Phase 2, while the simulator library and host tests remain in the repo.
<!-- SECTION:FINAL_SUMMARY:END -->
