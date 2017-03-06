import time
import machine
import tm1629


NO_SHOW_CODE = [0, 0, 0]
ALL_SHOW_CODE = [255, 255, 255]
DISPLAY_INTEGER_DIGIT_COUNT = 5
DISPLAY_DECIMAL_DIGIT_COUNT = 2

DISPLAY_DIGIT_MAP = {0: {0: [{'addr': 192, 'start_bit': 0, 'end_bit': 7, 'shift': 0, 'mask': 255}], 
                         1: [{'addr': 194, 'start_bit': 0, 'end_bit': 7, 'shift': 0, 'mask': 255}], 
                         2: [{'addr': 196, 'start_bit': 0, 'end_bit': 0, 'shift': 0, 'mask': 1}]},
                     1: {0: [{'addr': 196, 'start_bit': 1, 'end_bit': 7, 'shift': 1, 'mask': 254}, 
                             {'addr': 198, 'start_bit': 0, 'end_bit': 0, 'shift': -7, 'mask': 1}], 
                         1: [{'addr': 198, 'start_bit': 1, 'end_bit': 7, 'shift': 1, 'mask': 254}, 
                             {'addr': 200, 'start_bit': 0, 'end_bit': 0, 'shift': -7, 'mask': 1}], 
                         2: [{'addr': 200, 'start_bit': 1, 'end_bit': 1, 'shift': 1, 'mask': 2}]},
                     2: {0: [{'addr': 200, 'start_bit': 2, 'end_bit': 7, 'shift': 2, 'mask': 252}, 
                             {'addr': 202, 'start_bit': 0, 'end_bit': 1, 'shift': -6, 'mask': 3}], 
                         1: [{'addr': 202, 'start_bit': 2, 'end_bit': 7, 'shift': 2, 'mask': 252}, 
                             {'addr': 204, 'start_bit': 0, 'end_bit': 1, 'shift': -6, 'mask': 3}], 
                         2: [{'addr': 204, 'start_bit': 2, 'end_bit': 2, 'shift': 2, 'mask': 4}]},
                     3: {0: [{'addr': 204, 'start_bit': 3, 'end_bit': 7, 'shift': 3, 'mask': 248}, 
                             {'addr': 206, 'start_bit': 0, 'end_bit': 2, 'shift': -5, 'mask': 7}], 
                         1: [{'addr': 206, 'start_bit': 3, 'end_bit': 7, 'shift': 3, 'mask': 248}, 
                             {'addr': 193, 'start_bit': 0, 'end_bit': 2, 'shift': -5, 'mask': 7}], 
                         2: [{'addr': 193, 'start_bit': 3, 'end_bit': 3, 'shift': 3, 'mask': 8}]},
                     4: {0: [{'addr': 193, 'start_bit': 4, 'end_bit': 7, 'shift': 4, 'mask': 240}, 
                             {'addr': 195, 'start_bit': 0, 'end_bit': 3, 'shift': -4, 'mask': 15}], 
                         1: [{'addr': 195, 'start_bit': 4, 'end_bit': 7, 'shift': 4, 'mask': 240}, 
                             {'addr': 197, 'start_bit': 0, 'end_bit': 3, 'shift': -4, 'mask': 15}], 
                         2: [{'addr': 197, 'start_bit': 4, 'end_bit': 4, 'shift': 4, 'mask': 16}]},
                     5: {0: [{'addr': 197, 'start_bit': 5, 'end_bit': 7, 'shift': 5, 'mask': 224}, 
                             {'addr': 199, 'start_bit': 0, 'end_bit': 4, 'shift': -3, 'mask': 31}], 
                         1: [{'addr': 199, 'start_bit': 5, 'end_bit': 7, 'shift': 5, 'mask': 224}, 
                             {'addr': 201, 'start_bit': 0, 'end_bit': 4, 'shift': -3, 'mask': 31}], 
                         2: [{'addr': 201, 'start_bit': 5, 'end_bit': 7, 'shift': 5, 'mask': 224},
                             {'addr': 203, 'start_bit': 0, 'end_bit': 1, 'shift': -3, 'mask': 3}]},
                     6: {0: [{'addr': 203, 'start_bit': 2, 'end_bit': 7, 'shift': 2, 'mask': 252}, 
                             {'addr': 205, 'start_bit': 0, 'end_bit': 1, 'shift': -6, 'mask': 3}], 
                         1: [{'addr': 205, 'start_bit': 2, 'end_bit': 7, 'shift': 2, 'mask': 252}, 
                             {'addr': 207, 'start_bit': 0, 'end_bit': 1, 'shift': -6, 'mask': 3}], 
                         2: [{'addr': 207, 'start_bit': 2, 'end_bit': 6, 'shift': 2, 'mask': 124}]},
                   }  
                   
                   
class WF8266T(tm1629.TM1629):
         
    def __init__(self,                  
                 dio_pin_id = 16,                 
                 clk_pin_id = 14,
                 stb_pin_id = 15, 
                 brightness_level = 3, 
                 button_pin_id = 0):
                 
        self.button = machine.Pin(button_pin_id, machine.Pin.IN)
        
        self.buffer = {'digits': {}, 'bytes': {}} 
        self.no_show_code = NO_SHOW_CODE
        self.all_show_code = ALL_SHOW_CODE
        self.display_digit_count = 7
        self.display_digit_min = - 10 ** (self.display_digit_count - 1) + 1
        self.display_digit_max = 10 ** (self.display_digit_count) - 1
                
        self.display_digit_code = {
            '0': [255, 254, 1], '1': [0, 252, 1], '2': [249, 63, 1], '3': [201, 255, 1],     '4': [15, 253, 1], '5': [207, 231, 1], '6': [255, 231, 1], '7': [129, 252, 1], '8': [255, 255, 1],
             '9': [207, 255, 1],
             '.': [0, 2, 0], '-': [8, 33, 0], ':': [0, 3, 0], '!': [0, 124, 1],
             "A": [254, 249, 1], "B": [255, 219, 0], "C": [255, 142, 1], "D": [255, 250, 0], "E": [255, 39, 1], "F": [255, 37, 0], "G": [255, 230, 1], "H": [127, 253, 1], "I": [0, 252, 1], "J": [192, 254, 1], "K": [127, 221, 1], "L": [127, 2, 1], "M": [124, 241, 1], "N": [255, 252, 1], "O": [255, 254, 1], "P": [255, 61, 0], "Q": [143, 253, 1], "R": [255, 221, 1], "S": [239, 239, 1], "T": [255, 4, 0], "U": [127, 254, 1], "V": [63, 254, 0], "W": [31, 125, 0], "X": [119, 221, 1], "Y": [15, 255, 1], "Z": [243, 159, 1],
             "a": [254, 249, 1], "b": [126, 227, 1], "c": [120, 35, 1], "d": [120, 251, 1], "e": [255, 39, 1], "f": [255, 37, 0], "g": [255, 230, 1], "h": [126, 225, 1], "i": [0, 232, 1], "j": [0, 234, 1], "k": [126, 217, 1], "l": [126, 0, 0], "m": [124, 241, 1], "n": [120, 225, 1], "o": [120, 227, 1], "p": [255, 61, 0], "q": [143, 253, 1], "r": [120, 33, 0], "s": [239, 239, 1], "t": [124, 35, 1], "u": [120, 226, 1], "v": [56, 226, 0], "w": [30, 121, 0], "x": [62, 249, 0], "y": [14, 251, 1], "z":  [243, 159, 1], 
             tm1629.NO_SHOW_DIGIT: NO_SHOW_CODE, tm1629.All_SHOW_DIGIT: ALL_SHOW_CODE}

        self.display_digit_code_last_two_digits = {
            '0': [124, 34, 31], '1': [0, 62, 0], '2': [116, 42, 23], 
            '3': [84, 42, 31], '4': [28, 8, 31], '5': [92, 42, 29], '6': [124, 42, 29], '7': [4, 2, 31], '8': [124, 42, 31], '9': [92, 42, 31],
            '.': [0, 32, 0], '-': [16, 8, 4], ':': [0, 20, 0], '!': [0, 47, 0], 
            tm1629.NO_SHOW_DIGIT: NO_SHOW_CODE, tm1629.All_SHOW_DIGIT: ALL_SHOW_CODE}
                        
        super().__init__(dio_pin_id = dio_pin_id,
                         clk_pin_id = clk_pin_id, 
                         stb_pin_id = stb_pin_id,
                         lsbfirst = True,
                         brightness_level = brightness_level)     
        
        self.clear(tm1629.All_SHOW_DIGIT); self.show(); time.sleep(3)
        self.show_text("HELLO!"); time.sleep(1) 

      
    def set_digit_by_index(self, index, value):
        data = {'value': value, 'code': self.no_show_code}
        if index in range(5):
            data['code'] = self.display_digit_code.get(value, self.no_show_code)
        if index in [5, 6]: 
            data['code'] = self.display_digit_code_last_two_digits.get(value, self.no_show_code)
            
        self.buffer['digits'][index] = data           
    
    
    def calculate_buffers(self):        
        buffer_bytes = {}
        
        for digit, attr in self.buffer['digits'].items():
            for byte_index in range(len(attr['code'])):
                value = attr['code'][byte_index]
                for portion in DISPLAY_DIGIT_MAP[digit][byte_index]:
                
                    addr = portion['addr']
                    shift = portion['shift']
                    mask = portion['mask']                    
                    addr_value = value << abs(shift) if shift > 0 else value >> abs(shift)
                    addr_value = addr_value & mask                    
                    attrs = buffer_bytes.setdefault(addr, {'parts': [], 'calculated_value': None})
                    attrs['parts'].append(addr_value) 
                    
        self.buffer['bytes'] = buffer_bytes
        
        for addr, attrs in self.buffer['bytes'].items():
            calculated_value = 0
            for value_part in attrs['parts']:
                calculated_value = calculated_value | value_part              
            attrs['calculated_value'] = calculated_value 
        
         
    def show(self, dots = []): 
        self.calculate_buffers()
        
        self._led_begin()        
        for addr, attrs in self.buffer['bytes'].items(): 
            self._send_one_digit(addr, attrs['calculated_value'])            
        self.set_brightness(self.brightness_level)  
        

    def show_time(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(hour) + ":" + "{0:0>2}".format(minute) + "{0:0>2}".format(second)  
        self._show_digits(time_string)
        
        if self.button.value() == 0:
            self.show_date(year, month, day, hour, minute, second); time.sleep(3) 
 
        
    def show_date(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(month) + "-" + "{0:0>2}".format(day) 
        self._show_digits(time_string)
        
        
# import time
# import display_tm1629_wf8266t
# ds = display_tm1629_wf8266t.Display()
# ds.show_text("AAAAAAAAAA")
# ds.show_one_byte_data(193, 0x01)        