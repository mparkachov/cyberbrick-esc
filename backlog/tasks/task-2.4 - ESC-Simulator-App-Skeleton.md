---
id: TASK-2.4
title: ESC Simulator App Skeleton
status: To Do
assignee: []
created_date: '2026-07-05 09:06'
updated_date: '2026-07-05 09:06'
labels:
  - micropython
  - architecture
dependencies:
  - TASK-2.1
modified_files:
  - micropython/main.py
  - micropython/lib/cyberbrick_esc/config.py
  - micropython/lib/cyberbrick_esc/app.py
parent_task_id: TASK-2
milestone: m-1
priority: medium
ordinal: 10400
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the MicroPython app entrypoint, package layout, and safe default configuration for the visual ESC simulator.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Config defines GPIO1/GPIO0 inputs and GPIO8 LED.
- [ ] #2 Config defines 900-2100 us valid range, 1000/1500/2000 us command mapping, 50 us deadband, 150 ms failsafe, 1000 ms neutral arming, and 200 Hz loop.
- [ ] #3 App entrypoint initializes LED, input capture, and safety mapping.
- [ ] #4 No motor output pins are configured or written.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Keep long-running behavior in `main.py`; do not add `boot.py` unless a later task proves it is required.
<!-- SECTION:NOTES:END -->
