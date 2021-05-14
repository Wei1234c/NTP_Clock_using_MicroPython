try:
    from neo_pixel.neo_pixel import NeoPixel, Element
except:
    from neo_pixel import NeoPixel, Element

import time


HOURS = 12
MINUTES = 60
SECONDS = 60

HOUR_MARKS = (0, 3, 6, 9)
# HOUR_MARKS = range(HOURS)
COLOR_HOUR_MARK = (1, 1, 0)
COLOR_HOUR_ZERO = (1, 1, 1)
COLOR_HOUR = (5, 0, 0)
COLOR_MINUTE = (0, 5, 0)
COLOR_SECOND = (0, 0, 5)



class Clock(NeoPixel):

    def __init__(self,
                 data_pin,
                 pixels_count = 60,
                 start_idx = 0,
                 brightness_level = 1):

        super().__init__(pin = data_pin, n = pixels_count, start_idx = start_idx)

        self.pixels_count = pixels_count
        self.brightness_level = brightness_level
        self.init()


    def init(self):
        self.fill((1, 1, 1))
        self.show()
        time.sleep(3)

        self.clear()

        self._set_hour_pixels()
        self[0] = COLOR_HOUR_ZERO

        self.ele_hour = Element(colors = [COLOR_HOUR])
        self.ele_minute = Element(colors = [COLOR_MINUTE])
        self.ele_second = Element(colors = [COLOR_SECOND])

        self.place_element(self.ele_hour, 1)
        self.place_element(self.ele_minute, 2)
        self.place_element(self.ele_second, 3)


    def _get_index(self, numerator, denominator = 60):
        return int((numerator / denominator) * self.n)


    def _set_hour_pixels(self, color = COLOR_HOUR_MARK):
        for i in HOUR_MARKS:
            self[self._get_index(i, HOURS)] = color


    def show(self):
        self.write()


    def show_time(self, year, month, day, hour, minute, second):
        # background: background? color and brightness?
        # hours dots: show hours dots? color and brightness?
        # hour: how to display hour? color and brightness?
        # minute: how to display minute? color and brightness?
        # second: how to display second? color and brightness?
        # hour-minute: fill between hour and minute? color and brightness?
        # minute-hour: fill between minute and hour? color and brightness?

        self.remove_element(self.ele_second)
        self.remove_element(self.ele_minute)
        self.remove_element(self.ele_hour)

        self.place_element(self.ele_hour, self._get_index(hour + minute / MINUTES, HOURS))
        self.place_element(self.ele_minute, self._get_index(minute))
        self.place_element(self.ele_second, self._get_index(second))
        self.show()


    def show_date(self, year, month, day, hour, minute, second):
        pass
