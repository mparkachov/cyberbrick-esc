---
id: TASK-2.9
title: Stock-Tool ESC Simulator Deployment
status: Done
assignee: []
created_date: '2026-07-06 00:00'
updated_date: '2026-07-08 00:00'
labels:
  - micropython
  - deployment
  - hardware
dependencies:
  - TASK-2.8
modified_files:
  - justfile
  - README.md
  - AGENTS.md
  - micropython/examples/esc_boot.py
  - micropython/main.py
  - micropython/lib/cyberbrick_esc/app.py
  - micropython/lib/cyberbrick_esc/config.py
  - micropython/lib/cyberbrick_esc/safety.py
  - micropython/lib/cyberbrick_esc/led.py
  - tests/test_safety.py
  - tests/test_led.py
  - tests/test_app_skeleton.py
  - micropython/lib/cyberbrick_esc/
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10900
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deploy the visual ESC simulator through the validated stock-tool MicroPython
workflow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `just deploy` uses only `uv run mpremote ... resume` filesystem commands and preserves remote `boot.py` as `boot.stock.py`.
- [x] #2 The deploy recipe installs the simulator boot override, `main.py`, and `micropython/lib/cyberbrick_esc/` modules without custom serial helpers.
- [x] #3 `just restore-stock` removes deployed simulator files and returns stock `boot.py`.
- [x] #4 Host tests and MicroPython syntax checks pass through `just test`.
- [x] #5 Simulator prints miniterm diagnostics for captured channel pulse widths, freshness, safety state, final commands, and LED RGB.
- [x] #6 Arming tolerates brief non-neutral capture glitches while keeping final commands zero until arming completes.
- [x] #7 Armed state tolerates brief stale-input glitches by outputting zero without latching disarm unless loss persists.
- [x] #8 Agent guidance states that final safe commands, not LED smoothness, are the stability target for future motor output.
- [x] #9 Hardware validation confirms the native-capture simulator starts after reset/power-cycle and LED feedback follows final safe commands.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The observed stock `boot.py` runs the vendor app directly, so simulator
deployment installs `micropython/examples/esc_boot.py` as remote `boot.py` and
keeps the real app entrypoint in remote `main.py`. At visual simulator
validation time, GPIO4-GPIO7 remained unused; the later unloaded output probe is
tracked in TASK-2.10.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardware validation is complete for the visual simulator PoC. `just deploy`
backs up the board filesystem, preserves stock `boot.py`, creates the simulator
package directory, copies `esc_boot.py`, `main.py`, and the simulator library,
then resets through stock `mpremote resume reset`. `just restore-stock` restores
`boot.stock.py`, removes deployed simulator files, and resets the board. The app
prints 500 ms diagnostics showing captured PWM widths, freshness, pre-safety raw
mapped commands, arming/failsafe reason, hard-fault detail, final commands, and
LED RGB.

Latest native-capture hardware evidence confirms the persistent simulator
starts after reset/power-cycle, waits for fresh input, arms from neutral, holds
`cmd=1000,0` for the 2000/1500 us forward step, holds `cmd=-1000,0` for the
1000/1500 us reverse step, and holds `cmd=1000,-1000` for the 2000/1000 us
opposing endpoint tie. LED feedback follows those final safe commands as green,
red, and blue respectively. When PWM stops, stale input immediately outputs
`cmd=0,0`; if input remains absent, `latch=input_loss` appears after the
configured 1500 ms latch window. The observed one-line delay where
`raw=-1000,0` while `cmd=1000,0` is the expected 80 ms command-change
confirmation behavior.

Follow-up scope testing showed stable electrical input while scheduled Python
GPIO callback timestamps moved under runtime load. Input capture now alternates
native `machine.time_pulse_us` measurements at a nominal 25 Hz per channel and
applies a three-sample median filter. Native polling still has rare preemption
outliers, so this remains a visual stock-runtime PoC rather than deterministic
motor-control evidence. The command path also applies a 50 us neutral deadband,
150 us endpoint deadband, endpoint/neutral command snapping, and 80 ms
command-change confirmation. These filters are part of the final command
stream rather than LED-only smoothing. Agent guidance makes final safe commands
the stability target for future motor output and keeps LED feedback as
downstream debug only.
<!-- SECTION:FINAL_SUMMARY:END -->
