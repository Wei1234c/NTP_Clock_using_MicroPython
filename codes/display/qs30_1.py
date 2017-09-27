from time import sleep
from machine import Pin, PWM
import shift_register 


LED_COLORS = {'': 0b111, 
              'white': 0b000, 
              'pupple': 0b001, 
              'light blue': 0b010,
              'yellow': 0b100,
              'blue': 0b011,
              'green': 0b110,
              'red': 0b101}

COLORS_COUNT = len(LED_COLORS)
              
COLONS = {'': 0b00,
          '.': 0b01, 
          '`': 0b10,
          ':': 0b11}
          
DIGITS = {'': 0x000, 
          '0': 0x001, 
          '9': 0x002, 
          '8': 0x004,
          '7': 0x008,
          '6': 0x010,
          '5': 0x020,
          '4': 0x040,
          '3': 0x080,
          '2': 0x100,
          '1': 0x200}

OUTPUT_FREQ = 500
OUTPUT_SCALE = 1024 // 10
CLEAR_VALUE = 0xE000
BYTES_PER_NIXIE = 2


class QS30_1(shift_register.Shift_register):

    def __init__(self, 
                 dio_pin_id = 13, clk_pin_id = 14, stb_pin_id = 15, lsbfirst = False,
                 oe_pin_id = 4, 
                 intensity = 0,
                 rows = 1, columns = 1):
                 
        super().__init__(dio_pin_id, clk_pin_id, stb_pin_id, lsbfirst)
        self.oe = PWM(Pin(oe_pin_id), freq = OUTPUT_FREQ)
        self.set_intensity(intensity)
        self.rows = rows
        self.columns = columns
        self.nixie_count = rows * columns
        self.buffer = [CLEAR_VALUE] * self.nixie_count
        
        self.clear()        
        

    def set_intensity(self, intensity = 0):
        self.intensity = intensity
        self.oe.duty(OUTPUT_SCALE * intensity)
        
        
    def _gen_command_from_values(self, digit_value, colon_value, led_color_value):        
        digit_value = digit_value << 3
        colon_value = colon_value << 1 
        led_color_value = led_color_value << 13
        return digit_value | colon_value | led_color_value
       
    def _gen_command(self, digit = '8', colon = '', led_color = 'green'):
        return self._gen_command_from_values(DIGITS[digit], COLONS[colon], LED_COLORS[led_color])       

    def _send_command(self, command):
        high_byte, low_byte = (command >> 8) & 0xFF, command & 0xFF
        self.shiftOut(high_byte, raise_stb = False)
        self.shiftOut(low_byte, raise_stb = False)        
        
    def _get_attrs_from_command(self, command):        
        digit_value = (command >> 3) & 0x3FF
        colon_value = (command >> 1) & 0b11
        led_color_value = (command >> 13) & 0b111
        return digit_value, colon_value, led_color_value
    

    # need to know each attribute
    def set_nixie(self, index = 0, 
                  digit = '8', colon = '', led_color = 'green',
                  display = False):                  
        self.buffer[index] = self._gen_command(digit = digit, colon = colon, led_color = led_color)
        if display: self.display()
        
    # change only desired attributes
    def _set_attr(self, index = 0, digit_value = None, colon_value = None, led_color_value = None):
        command = self.buffer[index] 
        digit_attr, colon_attr, led_color_attr = self._get_attrs_from_command(command)
        self.buffer[index] = self._gen_command_from_values(digit_value = digit_value if digit_value is not None else digit_attr,
                                                           colon_value = colon_value if colon_value is not None else colon_attr, 
                                                           led_color_value = led_color_value if led_color_value is not None else led_color_attr)        
        
     
    # change digit only
    def set_digit(self, index = 0, digit = '8'): 
        self._set_attr(index = index, digit_value = DIGITS[digit])
                
    def set_digit_all(self, digit = '8'): 
        for i in range(self.nixie_count):
            self.set_digit(i, digit) 
            
                                                           
    # change colon only
    def set_colon(self, index = 0, colon = ''):  
        self._set_attr(index = index, colon_value = COLONS[colon])
                                                           
    def set_colon_all(self, colon = ''): 
        for i in range(self.nixie_count):
            self.set_colon(i, colon) 
            
            
    # change led_color only
    def set_led_color(self, index = 0, led_color = 'green'):  
        self._set_attr(index = index, led_color_value = LED_COLORS[led_color])
        
    def set_led_color_all(self, led_color = 'green'): 
        for i in range(self.nixie_count):
            self.set_led_color(i, led_color) 


    # display
    def display(self):
        for command in self.buffer:
            self._send_command(command)            
        self.stb.value(1)

    def clear(self, command = CLEAR_VALUE):
        self.buffer = [command] * self.nixie_count
        self.display()
        
        
    # transit and transform
    def _transit_to(self, digit_to, index = 0, display = False, duration = 0.10):
        command = self.buffer[index]
        digit_attr, _, _ = self._get_attrs_from_command(command)
        self._set_attr(index = index, digit_value = digit_attr | DIGITS[digit_to])
        if display: 
            self.display()
            sleep(duration)
                   
    def transform(self, digits_to = None, duration = 0.10):
        # default digits array
        if digits_to is None:
            digits_to = [''] * self.nixie_count
        
        # show transition effect
        for i in range(self.nixie_count):
            self._transit_to(digit_to = digits_to[i], index = i)         
        self.display()
        sleep(duration)
        
        # final digits
        for i in range(self.nixie_count):
            self.set_digit(index = i, digit = digits_to[i])
        self.display()
        
    
    # blink
    def _blink_colon(self, index = 0,  colon = ':', duration = 0.1):
        self.set_colon(index = index, colon = colon)
        self.display()
        sleep(duration)
        self.set_colon(index = index, colon = '')
        self.display()
                
        
    # show time
    def show_time(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(hour % 12 if hour != 12 else hour) + "{0:0>2}".format(minute) + "{0:0>2}".format(second)
        time_string = list(time_string)
        digits_to_list = [list(time_string[i:i+self.nixie_count]) for i in range(0, len(time_string), self.nixie_count)]
        
        led_color = list(LED_COLORS.items())[minute % COLORS_COUNT][0]
        self.set_led_color_all(led_color)        
        self.set_colon_all()
        
        for digits_to in digits_to_list:
            self.transform(digits_to = digits_to)
            self._blink_colon()
            sleep(0.3)
        
        self.set_digit_all(digit = '')
        self.display()
        sleep(1.5)
        
        
    def test(self): 
        while True:
            for i in range(100):
                h = i // 10
                d = i % 10
                
                self.set_led_color_all(list(LED_COLORS.items())[h % COLORS_COUNT][0])
                
                if self.columns == 2:
                    self.transform(digits_to = [str(h), str(d)]) 
                if self.columns == 1:
                    self.transform(digits_to = [str(d)])
                    
                sleep(0.5)
            

if __name__ == '__main__':
    q = QS30_1(columns = 2)
    q.test() 
    
# import qs30_1 as qs
# q = qs.QS30_1(columns = 2)
# q.test()    