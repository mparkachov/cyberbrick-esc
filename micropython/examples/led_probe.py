from machine import Pin, bitstream
from time import sleep_ms


WS2812_TIMING = (400, 1000, 1000, 400)
STEP_MS = 450
PIN_HOLD_MS = 2200
LED_CANDIDATES = (
    (8, 1),
    (20, 4),
    (21, 4),
)
COLORS = (
    ("red", (96, 0, 0)),
    ("green", (0, 96, 0)),
    ("blue", (0, 0, 96)),
    ("off", (0, 0, 0)),
)


class PixelBus:
    def __init__(self, pin_id, count):
        self.pin = Pin(pin_id, Pin.OUT)
        self.buf = bytearray(count * 3)

    def show(self, rgb):
        red, green, blue = rgb
        for offset in range(0, len(self.buf), 3):
            self.buf[offset] = green
            self.buf[offset + 1] = red
            self.buf[offset + 2] = blue
        bitstream(self.pin, 0, WS2812_TIMING, self.buf)


def main():
    print("CyberBrick LED probe")
    print("Watching candidate WS2812 pins:", LED_CANDIDATES)
    while True:
        for pin_id, count in LED_CANDIDATES:
            bus = PixelBus(pin_id, count)
            print("Testing pin", pin_id, "count", count)
            elapsed = 0
            while elapsed < PIN_HOLD_MS:
                for name, color in COLORS:
                    print("pin", pin_id, name)
                    bus.show(color)
                    sleep_ms(STEP_MS)
                    elapsed += STEP_MS
            bus.show((0, 0, 0))


main()
