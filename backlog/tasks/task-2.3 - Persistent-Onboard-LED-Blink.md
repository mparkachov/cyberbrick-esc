---
id: TASK-2.3
title: Persistent Onboard LED Blink
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 12:05'
labels:
  - micropython
  - hardware
  - feedback
dependencies:
  - TASK-2.2
modified_files:
  - micropython/examples/blink_boot.py
  - micropython/examples/blink_main.py
  - micropython/examples/led_probe.py
  - micropython/lib/cyberbrick_esc/pixels.py
  - justfile
  - README.md
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the first board-visible proof that deploy and startup work by installing a persistent onboard RGB LED blink through a reversible `boot.py` override.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `just deploy-blink` backs up the board filesystem before overwriting `boot.py` or `main.py`.
- [x] #2 `just deploy-blink` preserves stock `boot.py` as remote `boot.stock.py` before replacing `boot.py`.
- [x] #3 `just deploy-blink` copies blink files and resets the board.
- [x] #4 The onboard LED blinks three colors after board reset or power-on without a host command.
- [x] #5 `just mp-stop` restores stock `boot.py`, removes deployed `main.py`, and recovers stock startup/REPL access.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The observed stock board boots `./app/rc_main.py` from `boot.py`, so `main.py` alone is not persistent. Keep the boot override reversible. Probe safe candidate WS2812 data pins directly because the visible green LED has not responded to the stock `bbl.leds` abstraction.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Persistent blink bring-up is complete. `just deploy-blink` backs up the stock MicroPython filesystem, preserves the original remote `boot.py` as `boot.stock.py`, installs a reversible blink `boot.py`, and resets the board. The stock board was observed blinking three different colors after unplug/replug with no additional host command. The visible LED did not respond through the stock `bbl.leds` abstraction, so the blink path now uses a direct safe WS2812 candidate-pin driver and includes `run-led-probe` plus `poc_boot_seen.txt` diagnostics for future pin confirmation. `just mp-stop` remains the recovery path to restore stock boot behavior.
<!-- SECTION:FINAL_SUMMARY:END -->
