---
id: m-1
title: "Stock MicroPython ESC simulator PoC"
---

## Description

Prove that the stock CyberBrick MicroPython runtime can host a narrow ESC simulator PoC without replacing the encrypted stock firmware. The active phase is a stock-tool workflow reset: manual REPL recovery when needed, `uv run mpremote`, RAM blink, persistent boot blink, and restore-to-stock. After that workflow is stable, resume two-channel PWM input capture, center-neutral safety mapping, failsafe behavior, and RGB LED feedback for final safe ESC commands. Real H-bridge motor output is intentionally excluded.
