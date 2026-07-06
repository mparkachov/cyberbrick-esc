import gc
from machine import Pin, bitstream
from time import sleep_ms


STEP_MS = 300
LED_PIN = 8
PIXEL_COUNT = 1
WS2812_TIMING = (400, 1000, 1000, 400)


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
    with open("poc_boot_seen.txt", "w") as marker:
        marker.write("blink_boot.py started\n")

    bus = PixelBus(LED_PIN, PIXEL_COUNT)
    colors = ((64, 0, 0), (0, 64, 0), (0, 0, 64), (0, 0, 0))

    while True:
        for color in colors:
            bus.show(color)
            gc.collect()
            sleep_ms(STEP_MS)


main()
