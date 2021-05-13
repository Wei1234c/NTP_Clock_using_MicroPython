# NeoPixel driver for MicroPython on ESP8266
# MIT license; Copyright (c) 2016 Damien P. George
# https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/neopixel.py

import time

import neopixel


COLOR_BLANK = (0, 0, 0)
COLOR_DEFAULT_CURSOR = (0, 0, 1)



class Element(neopixel.NeoPixel):

    def __init__(self, n = 1, colors = (COLOR_DEFAULT_CURSOR,), bpp = 3):
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self._at_index = None
        self._previous_colors = None

        for i in range(self.n):
            self[i] = colors[i]


    def write(self):
        raise NotImplementedError


    def dimm(self, factor = 2):
        for i in range(self.n):
            self[i] = tuple(max(0, min(int(self[i][j] / factor), 255)) for j in range(self.bpp))



class NeoPixel(neopixel.NeoPixel):
    RESET_us = 300
    DEFAULT_WAIT_ms = 13
    LEVEL_LOW = 0


    def __init__(self, pin, n, bpp = 3, timing = 1, start_idx = 0):
        super().__init__(pin, n, bpp, timing)
        self._start_idx = start_idx


    def _real_index(self, index):
        return (self._start_idx + index) % self.n


    def __setitem__(self, index, val):
        super().__setitem__(self._real_index(index), val)


    def __getitem__(self, index):
        return super().__getitem__(self._real_index(index))


    def write(self):
        super().write()
        self.reset()


    def reset(self):
        self.pin.value(self.LEVEL_LOW)
        time.sleep_us(self.RESET_us)


    def clear(self):
        self.fill(COLOR_BLANK)
        self.write()


    def place_element(self, element, at_idx = 0):
        element._at_index = at_idx
        element._previous_colors = []

        for i in range(element.n):
            element._previous_colors.append(self[at_idx + i])
            self[at_idx + i] = element[i]


    def remove_element(self, element):
        for i in range(element.n):
            self[element._at_index + i] = element._previous_colors[i]

        element._at_index = None
        element._previous_colors = None


    def move_element(self, element, to_idx = 0):
        self.remove_element(element)
        self.place_element(element, to_idx)


    def cycle(self, element = Element(), wait_ms = DEFAULT_WAIT_ms, transparent = True):

        for i in range(self.n):
            self.place_element(element, i)
            self.write()
            time.sleep_ms(wait_ms)

            if transparent:
                self.remove_element(element)

        self.write()
