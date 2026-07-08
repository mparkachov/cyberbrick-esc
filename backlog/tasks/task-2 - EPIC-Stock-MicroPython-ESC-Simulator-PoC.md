---
id: TASK-2
title: 'EPIC: Stock MicroPython ESC Simulator PoC'
status: In Progress
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-08 21:00'
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
- [x] #4 Phase 2 simulator deployment reflects final safe commands after stock-tool blink/restore is validated: blue neutral, green forward, red reverse, and blue on exact opposing ties.
- [x] #5 Documentation explains backup, deploy, restore, wiring, signal limits, no plaintext flashing, and unsupported features.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep this as stock-runtime MicroPython work on `main`. The previous Zephyr implementation is preserved on `origin/backup/zephyr`; do not reintroduce plaintext flashing for stock locked boards. GPIO4-GPIO7 may be driven only through TASK-2.10 and only from final safe commands. Attached-motor checks require the Mini Tank to be restrained with tracks lifted.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The stock-firmware MicroPython ESC simulator PoC is validated. The repo has a
confirmed `uv`-managed workflow using stock `mpremote`, manual miniterm recovery
from the stock solid-green app, RAM blink, persistent boot blink, and
restore-to-stock. Phase 2 deployment is implemented through `just deploy`, which
installs the ESC simulator using the same stock-tool workflow. Timing comparison
established that the original scheduled Python GPIO callbacks distorted pulse
timing even with stable input. The active implementation now alternates native
`machine.time_pulse_us` capture and keeps the median and safety filters
explicit in the final command path. Hardware timing evidence showed native
polling is normally accurate to about 1 us but still has rare
runtime-preemption outliers. Integrated native-capture hardware validation
confirms the deployed app starts after reset/power-cycle,
arms from neutral, follows forward/reverse/opposing-tie PWM commands in the
final safe command stream, and enters the documented stale-input and
`input_loss` states when PWM stops. The next active step is TASK-2.10: unloaded
GPIO4-GPIO7 H-bridge input PWM generated from those final safe commands and
validated through diagnostics and unloaded motor-output voltage measurement.
Diagnostic validation confirms `out=` follows final safe commands. Physical
testing identified the Mini Tank's mirrored motor polarity; the output
translation now follows the published Motor 1 positive/Motor 2 negative mapping.
Restrained forward/reverse/pivot validation remains open.
<!-- SECTION:FINAL_SUMMARY:END -->
