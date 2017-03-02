# https://learn.adafruit.com/micropython-hardware-ssd1306-oled-display/software

import machine 
import ssd1306
import display


class Display(display.Display):
    
    def __init__(self, width = 128, height = 64, scl_pin_id = 5, sda_pin_id = 4, freq = 400000):
        self.i2c = machine.I2C(scl = machine.Pin(scl_pin_id),
                               sda = machine.Pin(sda_pin_id), 
                               freq = freq)                               
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)
        self.show = self.display.show
        super().__init__()
        

    def clear(self):
        self.display.fill(0)
        self.display.show()
        
        
    def show_text(self, text = '', x = 0, y = 0, clear_first = True, show_now = True, hold_seconds = 0):  
        if clear_first: self.display.fill(0)
        self.display.text(text, x, y)
        if show_now: 
            self.display.show()
            if hold_seconds > 0: time.sleep(hold_seconds) 
                
                
    def show_datetime(self, year, month, day, hour, minute, second):   
        datetime = [year, month, day, hour, minute, second]
        datetime_str = ["{0:0>2}".format(d) for d in datetime]        
        
        self.show_text(text = '-'.join(datetime_str[:3]),
                        x = 0, y = 0, clear_first = True, show_now = False)
        self.show_text(text = ':'.join(datetime_str[3:6]),
                        x = 0, y = 10, clear_first = False, show_now = True)

                        
    def show_time(self, year, month, day, hour, minute, second):   
        self.show_datetime(year, month, day, hour, minute, second)
                            