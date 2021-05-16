try:
    from neo_pixel.neo_pixel import NeoPixel, Element
except:
    from neo_pixel import NeoPixel, Element

import time


HOURS = 12
MINUTES = 60
SECONDS = 60
BRIGHTNESS = 1
HOUR_MARKS = (0,)
# HOUR_MARKS = (0, 3, 6, 9)
# HOUR_MARKS = range(HOURS)
COLOR_HOUR_MARK = (1 * BRIGHTNESS, 1 * BRIGHTNESS, 0 * BRIGHTNESS)
COLOR_HOUR_ZERO = (1 * BRIGHTNESS, 1 * BRIGHTNESS, 1 * BRIGHTNESS)
COLOR_HOUR = (1 * BRIGHTNESS, 0, 0)
COLOR_MINUTE = (0, 1 * BRIGHTNESS, 0)
COLOR_SECOND = (0, 0, 16 * BRIGHTNESS)



class Clock(NeoPixel):

    def __init__(self,
                 data_pin,
                 pixels_count = 60,
                 start_idx = 0,
                 bar_mode = True):

        super().__init__(pin = data_pin, n = pixels_count, start_idx = start_idx)

        self._bar_mode = bar_mode
        self._time_is_set = False
        self.init()


    def init(self):
        self.fill((1, 1, 1))
        self[0] = (255, 255, 255)
        self[30] = (255, 255, 255)
        self.show()
        time.sleep(3)

        self.clear()

        self._set_hour_pixels()
        self[0] = COLOR_HOUR_ZERO

        self.ele_hour = Element(colors = [COLOR_HOUR])
        self.ele_minute = Element(colors = [COLOR_MINUTE])
        self.ele_second = Element(colors = [COLOR_SECOND], transparent = False)
        self.place_element(self.ele_hour, 1)
        self.place_element(self.ele_minute, 2)
        self.place_element(self.ele_second, 3)


    def _get_index(self, numerator, denominator = 60):
        return int((numerator / denominator) * self.n)


    def _set_hour_pixels(self, color = COLOR_HOUR_MARK):
        for i in HOUR_MARKS:
            self[self._get_index(i % HOURS, HOURS)] = color


    def show(self):
        self.write()


    def show_time(self, year, month, day, hour, minute, second):

        self.remove_element(self.ele_second)

        # hour & minute
        if not self._time_is_set or second == 0:

            # remove
            self.remove_element(self.ele_minute)  # minute has to be removed before hour,for non-transparent.
            self.remove_element(self.ele_hour)

            # place
            if self._bar_mode:
                n = self._get_index(hour % HOURS + minute / MINUTES, HOURS)
                self.ele_hour = Element(n = n, colors = [COLOR_HOUR] * n, transparent = True)

                n = self._get_index(minute, MINUTES)
                self.ele_minute = Element(n = n, colors = [COLOR_MINUTE] * n, transparent = True)

                self.place_element(self.ele_hour, 1)
                self.place_element(self.ele_minute, 1)

            else:  # dot mode
                self.place_element(self.ele_hour, self._get_index(hour % HOURS + minute / MINUTES, HOURS))
                self.place_element(self.ele_minute, self._get_index(minute, MINUTES))

        self.place_element(self.ele_second, self._get_index(second, SECONDS))
        self._time_is_set = True
        self.show()


    def show_date(self, year, month, day, hour, minute, second):
        pass
