---
id: TASK-2.3
title: Persistent Onboard LED Blink
status: Done
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-06 00:00'
labels:
  - micropython
  - hardware
  - feedback
dependencies:
  - TASK-2.2
modified_files:
  - micropython/examples/blink_boot.py
  - micropython/examples/blink_main.py
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
- [x] #5 `just restore-stock` restores stock `boot.py`, removes deployed PoC startup files when present, and returns the board to stock startup.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The observed stock board boots `./app/rc_main.py` from `boot.py`, so `main.py` alone is not persistent. Keep the boot override reversible. Phase 1 uses the known onboard WS2812 data pin on GPIO8 only.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Persistent blink bring-up remains the Phase 1 hardware proof. `just deploy-blink` backs up the stock MicroPython filesystem, preserves the original remote `boot.py` as `boot.stock.py`, installs `micropython/examples/blink_boot.py` as remote `boot.py`, and resets the board. The active blink path uses a direct WS2812 driver on GPIO8 only. `just restore-stock` is the recovery path to restore stock boot behavior.
<!-- SECTION:FINAL_SUMMARY:END -->
