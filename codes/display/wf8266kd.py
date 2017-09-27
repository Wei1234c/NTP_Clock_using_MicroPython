import time
import machine
import tm1629
import wf8266kd_commands


NO_SHOW_CODE = 0
ALL_SHOW_CODE = 255
                          

class WF8266KD(tm1629.TM1629): 
    
    def __init__(self, 
                 dio_pin_id = 16,                 
                 clk_pin_id = 14,
                 stb_pin_id = 15, 
                 brightness_level = 1, 
                 button_pin_id = 0):
                 
        self.button = machine.Pin(button_pin_id, machine.Pin.IN)
        
        self.buffer = [0,] * tm1629.DISPLAY_SEGMENT_COUNT        
        self.no_show_code = NO_SHOW_CODE
        self.all_show_code = ALL_SHOW_CODE
        self.display_digit_addrs = (0xc1, 0xc3, 0xc5, 0xc7, 0xc9, 0xcb, 0xcd, 0xcf) 
        self.display_digit_count = len(self.display_digit_addrs)
        self.display_digit_min = - 10 ** (self.display_digit_count - 1) + 1
        self.display_digit_max = 10 ** (self.display_digit_count) - 1
        
        self.display_digit_code = {
            '0': 63, '1': 6, '2': 91, '3': 79, '4': 102, '5': 109, '6': 125, '7': 7, '8':    127, '9': 111,
            '.': 128, '-': 64, ':': 72,
            "A": 0x77, "B": 0x7C, "C": 0x39, "D": 0x5E, "E": 0x79, "F": 0x71, "G": 0, "H": 118, "I": 0, "J": 14, "K": 0, "L": 56, "M": 0, "N": 0, "O": 63, "P": 115, "Q": 103, "R": 80, "S": 109, "T": 120, "U": 62, "V": 0, "W": 0, "X": 0, "Y": 102, "Z": 0,
            "a": 0x77, "b": 0x7C, "c": 0x39, "d": 0x5E, "e": 0x79, "f": 0x71, "g": 111, "h": 116, "i": 4, "j": 14, "k": 0, "l": 48, "m": 0, "n": 84, "o": 92, "p": 115, "q": 103, "r": 80, "s": 109, "t": 120, "u": 28, "v": 0, "w": 0, "x": 0, "y": 102, "z": 0, 
            tm1629.NO_SHOW_DIGIT: NO_SHOW_CODE, tm1629.All_SHOW_DIGIT: ALL_SHOW_CODE} 
        
        super().__init__(dio_pin_id = dio_pin_id,
                         clk_pin_id = clk_pin_id, 
                         stb_pin_id = stb_pin_id,
                         lsbfirst = True,
                         brightness_level = brightness_level)        
        
        self.clear(tm1629.All_SHOW_DIGIT); self.show(); time.sleep(3)                 
        self.show_text("HELLO!"); time.sleep(1) 
 
 
    # convert number to digits string and show it
    def show_number(self, number):        
        if self.display_digit_min <= number <= self.display_digit_max:
            digits = str(number)
            dots = [digits.find('.') - 1]
            digits = digits.replace('.', '')            
            self._show_digits(digits, dots = dots, right_align = True)
        else:
            self._show_digits("Error")
            
            
    def show_datetime(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(month) + "{0:0>2}".format(day) + "{0:0>2}".format(hour) + "{0:0>2}".format(minute)
        self._show_digits(time_string, dots = [1, 3, 5])
        
        
    def show_time(self, year, month, day, hour, minute, second):
        super().show_time(year, month, day, hour, minute, second)
        if self.button.value() == 0:
            self.show_date(year, month, day, hour, minute, second); time.sleep(3) 
        self.exec_command(self.read_keys()[0])
        
        
    def exec_command(self, key_code):
        command = wf8266kd_commands.commands.get(key_code)
        if command: exec(command)
            
            
# import time
# import wf8266kd
# ds = wf8266kd.WF8266KD() 
# ds.show_datetime(2017, 2, 25, 13, 47, 25); time.sleep(2)
# ds.show_time(2017, 2, 25, 13, 47, 25); time.sleep(2)
# ds.show_number(12.56); time.sleep(2)

# for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    # ds.show_text(c); time.sleep(0.5)
# for c in 'abcdefghijklmnopqrstuvwxyz':
    # ds.show_text(c); time.sleep(0.5)     
# ds.show_text("HELLO!"); time.sleep(2)     
# for i in range(99999999):
    # ds.show_number(i)