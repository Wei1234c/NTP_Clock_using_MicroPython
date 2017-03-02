import time
import ntp_client
import led
import gc


class Clock():
    
    def __init__(self, display, led_pin = None, led_high_is_on = False):        
        self.display = display
        self.led_pin = led_pin if led_pin else led.on_board_led
        self.led_high_is_on = led_high_is_on
        ntp_client.calibrate_time_upython() 
        
        
    def show_current_time(self):
        current_time = time.localtime()
        print(current_time)
        
        year, month, day, hour, minute, second, _, _ = current_time        
        self.display.show_time(year, month, day, hour, minute, second)
        
        self._on_hour(hour, minute, second)
        
        
    def _on_hour(self, hour, minute, second): 
        
        if minute == second == 0: 
            print("\n[Clock: now is {} o'clock]\n".format(hour))

            times_to_signal = hour % 12
            if times_to_signal == 0: times_to_signal = 12

            led.blink(self.led_pin, 
                      times = times_to_signal - 1, on_seconds = 0.1, off_seconds = 0.9, 
                      high_is_on = self.led_high_is_on)
            led.blink(self.led_pin, 
                      times = 1, on_seconds = 0.5, off_seconds = 0.5, 
                      high_is_on = self.led_high_is_on)   
            
            ntp_client.calibrate_time_upython()
            

    def run(self):        
        while True:         
            self.show_current_time()
            gc.collect()
            print('[Memory - free: {}   allocated: {}]'.format(gc.mem_free(), gc.mem_alloc()))            
            time.sleep(1)