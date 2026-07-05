---
id: TASK-2.8
title: Integration, Validation, and Documentation
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 18:49'
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
  - scripts/mp_prepare_repl.py
  - scripts/mp_serial_fs.py
  - micropython/boot.py
  - micropython/lib/cyberbrick_esc/config.py
  - micropython/lib/cyberbrick_esc/led.py
  - tests/test_app_skeleton.py
  - tests/test_led.py
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
- [x] #1 `just deploy` installs the reversible PoC `boot.py`, `main.py`, and `cyberbrick_esc` library files.
- [x] #2 README documents wiring, 3.3 V signal limits, blink, deploy, backup, restore, failsafe behavior, and intentionally unsupported features.
- [x] #3 `just test` passes host safety tests.
- [x] #4 Documentation states that GPIO4-GPIO7 motor outputs are not driven in this milestone.
- [x] #5 Documentation preserves the warning against force-flashing plaintext firmware to locked stock boards.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hardware validation requires a connected stock board in MicroPython REPL mode. Keep validation steps motors-disconnected and visual-first.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Integration and documentation are complete for the stock MicroPython visual ESC simulator milestone. `just deploy` was run on the stock CyberBrick board and copied the reversible PoC `boot.py`, `main.py`, and `lib/cyberbrick_esc/` modules. The deployed board initially showed safe neutral blue with no PWM input, confirming the simulator app replaced the blink example. Because the observed USB serial path cannot reliably interrupt an already-running infinite app, the PoC boot flow now includes sticky double-reset safe REPL mode using `cyberbrick_boot_pending.txt` and `cyberbrick_safe_repl.txt`; in safe mode it renames `main.py` to `main.poc.py` so MicroPython does not auto-run the app after `boot.py` returns. Hardware validation confirmed that after deploy and double reset, `just mp-tree` can inspect the board and shows `boot.py`, `boot.stock.py`, `cyberbrick_safe_repl.txt`, `lib/cyberbrick_esc/`, and `main.poc.py`. README documents wiring, 3.3 V signal limits, blink/deploy/backup/restore/recovery workflows, failsafe behavior, intentionally unsupported features, the locked-board no-plaintext-flashing warning, and that GPIO4-GPIO7 motor outputs are not driven in this milestone. Host validation passes with `just test`.
<!-- SECTION:FINAL_SUMMARY:END -->
