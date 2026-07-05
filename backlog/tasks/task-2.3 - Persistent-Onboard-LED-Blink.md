---
id: TASK-2.3
title: Persistent Onboard LED Blink
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - micropython
  - hardware
  - feedback
dependencies:
  - TASK-2.2
modified_files:
  - micropython/examples/blink_main.py
  - justfile
  - README.md
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 10300
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the first board-visible proof that deploy and startup work by installing a persistent onboard RGB LED blink as `main.py`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `just deploy-blink` backs up the board filesystem before overwriting `main.py`.
- [ ] #2 `just deploy-blink` copies the blink example as remote `main.py` and resets the board.
- [ ] #3 The onboard RGB LED on GPIO8 blinks after board reset or power-on without a host command.
- [ ] #4 `just mp-stop` removes deployed `main.py` and recovers REPL access.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Use a one-pixel WS2812/NeoPixel on GPIO8. A color cycle is acceptable because it also helps validate color order during bring-up.
<!-- SECTION:NOTES:END -->
