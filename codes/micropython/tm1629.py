import shift_register 


DISPLAY_COMMAND = 0x44
NO_SHOW_DIGIT = 0x00
All_SHOW_DIGIT = 0xFF
DISPLAY_DIGIT_BASE_ADDR = 0xC0
DISPLAY_SEGMENT_COUNT = 16
DISPLAY_BRIGHTNESS = (0x80,) + tuple(0x88 + i for i in range(9))   
    
KEYPAD_COMMAND = 0x42
KEYPAD_DATA_BYTES = 4
   

class TM1629(shift_register.Shift_register): 
    
    def __init__(self, 
                 dio_pin_id = 16,
                 clk_pin_id = 14,
                 stb_pin_id = 15,
                 lsbfirst = True,
                 brightness_level = 1):  
                 
        self.brightness_level = brightness_level
        
        shift_register.Shift_register.__init__(self, 
                                               dio_pin_id = dio_pin_id,
                                               clk_pin_id = clk_pin_id, 
                                               stb_pin_id = stb_pin_id,
                                               lsbfirst = lsbfirst) 
                                               
                                               
    def _led_begin(self): 
        self.shiftOut(DISPLAY_COMMAND)
  

    def set_brightness(self, brightness_level = 1):
        self.shiftOut(DISPLAY_BRIGHTNESS[brightness_level]) 

        
    def set_digit_by_index(self, index, value):
        self.buffer[index] = value  

        
    def _send_one_digit(self, addr, data):
        self.shiftOut(value = addr, raise_stb = False)
        self.shiftOut(value = data)
        
        
    def show_one_byte_data(self, addr, data): 
        self._led_begin()
        self._send_one_digit(addr, data)           
        self.set_brightness(self.brightness_level)   
        
    
    # show whatever in buffer
    def show(self, dots = []): 
        
        self._led_begin()
        
        for i in range(self.display_digit_count):  
            digit = self.buffer[i]
            digit_code = self.display_digit_code.get(digit, self.no_show_code)
            if (digit_code != self.no_show_code) and (i in dots): 
                digit_code = digit_code + self.display_digit_code['.']                
            self._send_one_digit(self.display_digit_addrs[i], digit_code)
            
        self.set_brightness(self.brightness_level) 
 
 
    # show digits string 
    def _show_digits(self, string, dots = [], right_align = False): 
        self.clear()
        
        digits = string
        width = len(digits)
        
        shift_digits = self.display_digit_count - width       
        if not right_align or shift_digits <= 0:
            shift_digits = 0
            
        for i in range(self.display_digit_count):
            if i < width: self.set_digit_by_index(i + shift_digits, digits[i])
        dots = [i + shift_digits for i in dots if i > -1]
            
        self.show(dots)

    
    def show_text(self, string, dots = [], right_align = False): 
        self._show_digits(string = string, dots = dots, right_align = right_align)
        
 
    # convert number to digits string and show it
    def show_number(self, number): 
        if self.display_digit_min <= number <= self.display_digit_max:
            digits = str(number)       
            self._show_digits(digits, dots = [], right_align = True) 
        else:
            self._show_digits("Error")
            
            
    def show_datetime(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(month) + "{0:0>2}".format(day) + "{0:0>2}".format(hour) + "{0:0>2}".format(minute)
        self._show_digits(time_string, dots = [1, 3, 5])


    def show_time(self, year, month, day, hour, minute, second):        
        time_string = "{0:0>2}".format(hour) + ":" + "{0:0>2}".format(minute) + ":" + "{0:0>2}".format(second)  
        self._show_digits(time_string)

        
    def show_date(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(year) + "{0:0>2}".format(month) + "{0:0>2}".format(day)
        self._show_digits(time_string, dots = [3, 5])  
        
                
    def clear(self, value = NO_SHOW_DIGIT):
        for i in range(self.display_digit_count):
            self.set_digit_by_index(i, value)       
        
        
    def off(self):
        self.set_brightness(0)
        
        
    def on(self):
        self.set_brightness(self.brightness_level)
        
        
    def read_keys(self):
        data = []
        self.shiftOut(value = KEYPAD_COMMAND, raise_stb = False)
        for i in range(KEYPAD_DATA_BYTES - 1):
            data.append(self.shiftIn(raise_stb = False))
        data.append(self.shiftIn())  
        
        return data
 