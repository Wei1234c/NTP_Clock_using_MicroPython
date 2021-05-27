import gc
import time

import led

import ntp_client



class Clock:

    def __init__(self, display, buzzer = None, led_high_is_on = False):
        self.adjusted_time_delta = 0
        self.display = display
        self.buzzer = buzzer if buzzer else led.on_board_led
        self.led_high_is_on = led_high_is_on
        ntp_client.calibrate_time_upython()

        # # (year, month, day, weekday, hours, minutes, seconds, subseconds)
        # import machine
        # machine.RTC().datetime((2021, 5, 14, 4, 8, 59, 55, 0))


    def show_current_time(self):
        current_time = time.localtime()
        print(current_time)

        year, month, day, hour, minute, second, _, _ = current_time
        self.display.show_time(year, month, day, hour, minute, second)

        self._on_hour(hour, minute, second, silent_night = False, day_hours_range = (7, 22))

        if minute == 59 and second == 0:
            ntp_client.calibrate_time_upython()


    def _on_hour(self, hour, minute, second, silent_night = False, day_hours_range = (7, 22)):
        day_hour_min, day_hour_max = day_hours_range

        if minute == second == 0:
            print("\n[Clock: now is {} o'clock]\n".format(hour))

            if (silent_night is False) or (day_hour_min <= hour <= day_hour_max):

                times_to_signal = hour % 12
                if times_to_signal == 0:
                    times_to_signal = 12

                led.blink(self.buzzer,
                          times = times_to_signal - 1, on_seconds = 0.1, off_seconds = 0.9,
                          high_is_on = self.led_high_is_on)
                led.blink(self.buzzer,
                          times = 1, on_seconds = 0.5, off_seconds = 0.5,
                          high_is_on = self.led_high_is_on)


    def adjust_time_delta(self, start_time, end_time, targeted_difference = 1000):
        time_delta = end_time - start_time - targeted_difference
        time_delta = time_delta if 0 < abs(time_delta) < targeted_difference else 0
        self.adjusted_time_delta += time_delta / 3


    def run(self):
        adjusted_time_delta = 0

        while True:
            start_time = time.ticks_ms()

            self.show_current_time()
            gc.collect()
            print('[Memory - free: {}   allocated: {}]'.format(gc.mem_free(), gc.mem_alloc()))
            time.sleep(1 - (self.adjusted_time_delta / 1000))

            end_time = time.ticks_ms()
            self.adjust_time_delta(start_time, end_time)
            print('cycle time (ms):', end_time - start_time)
