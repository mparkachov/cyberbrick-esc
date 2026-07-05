try:
    from machine import Pin, bitstream
except ImportError:
    Pin = None
    bitstream = None


WS2812_TIMING = (400, 1000, 1000, 400)


class PixelBus:
    def __init__(self, pin_id, count):
        if Pin is None or bitstream is None:
            raise RuntimeError("machine.Pin and machine.bitstream are required")

        self.pin = Pin(pin_id, Pin.OUT)
        self.count = count
        self.buf = bytearray(count * 3)

    def fill(self, rgb):
        red, green, blue = rgb
        for idx in range(self.count):
            offset = idx * 3
            self.buf[offset] = green
            self.buf[offset + 1] = red
            self.buf[offset + 2] = blue

    def write(self):
        bitstream(self.pin, 0, WS2812_TIMING, self.buf)

    def show(self, rgb):
        self.fill(rgb)
        self.write()
