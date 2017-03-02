# coding: utf-8


import time
import worker
import led
import display_oled
import ntp_clock
import u_python 


class Worker(worker.Worker):
        
    # Object control
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        self.now = time.ticks_ms
        self.display = display_oled.oled
        self.clock = ntp_clock.Clock()
        
        
    # code book_______________________
    def set_default_code_book(self):
        code_book = {'read GPIOs': self.read_GPIOs,
                     'write GPIOs': self.write_GPIOs,
                     'show text': self.show_text,
                     'blink led': self.blink_led}      
        self.set_code_book(code_book)        
        
        
    def rename(self, name):
        self.name = name
        
        
    def read_GPIOs(self, pins):
        return u_python.read_GPIOs_pins(pins)
        

    def write_GPIOs(self, pins_and_values): 
        return u_python.write_GPIOs_pins(pins_and_values)
        
    
    def blink_led(self, times = 1, forever = False, on_seconds = 0.5, off_seconds = 0.5):
        led.blink_on_board_led(times = times, 
                               forever = forever,
                               on_seconds = on_seconds,
                               off_seconds = off_seconds)

                               
    def show_text(self, text = '', x = 0, y = 0, clear_first = True, show_now = True, hold_seconds = 10):  
        if clear_first: self.display.fill(0)
        self.display.text(text, x, y)
        if show_now: 
            self.display.show()
            time.sleep(hold_seconds)
            
            
    def process_messages(self):
        super().process_messages()
        self.clock.show_current_time()