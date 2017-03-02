import time
import machine 
import ws2812_clock_patterns

# >>> np[0] = (255, 0, 0) # set to red, full brightness
# >>> np[1] = (0, 128, 0) # set to green, half brightness
# >>> np[2] = (0, 0, 64)  # set to blue, quarter brightness
 


NO_SHOW_DIGIT = 0x00
NO_SHOW_CODE = 0
All_SHOW_DIGIT = 0xFF
ALL_SHOW_CODE = 255

HOURS = 12
MINUTES = 60
HOUR_COLOR = (255, 255, 255)
                          

class Face(neopixel.NeoPixel): 
    
    def __init__(self, 
                 data_pin_id = 4,                 
                 pixels_count = 60,
                 brightness_level = 1, 
                 button_pin_id = 0):
        
        self.pixels_count = pixels_count
        self.brightness_level = brightness_level        
        self.pattern = ws2812_clock_patterns.patterns['default']
        self.button = machine.Pin(button_pin_id, machine.Pin.IN)        
        # self.buffer = [(0, 0, 0),] * pixels_count
        
        super().__init__(machine.Pin(data_pin_id, machine.Pin.OUT), pixels_count)
        
        self.clear(All_SHOW_DIGIT); self.show(); time.sleep(3)
        
    
    def set_pattern(self, pattern):
        self.pattern = pattern
        
        
    def _get_minute_pixel_index(self, minute):
        return int((minute / MINUTES) * self.pixels_count)
        
        
    def _get_hour_pixel_index(self, hour):
        return int((hour / HOURS) * self.pixels_count)        

        
    def _show_hour_pixels(self, color = HOUR_COLOR):
        for i in range(HOURS):
            self[self._get_hour_pixel_index(i + 1)] = color
                
    
    def show(self):
        self.write()
        
    
    def _calculate_buffers(self):        
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
            
        
    def show_time(self, year, month, day, hour, minute, second):
        # background: background? color and brightness?
        # hours dots: show hours dots? color and brightness?
        # hour: how to display hour? color and brightness?
        # minute: how to display minute? color and brightness?
        # second: how to display second? color and brightness?
        # hour-minute: fill between hour and minute? color and brightness?
        # minute-hour: fill between minute and hour? color and brightness?
        
        pass
        
        
    def show_date(self, year, month, day, hour, minute, second):
        pass

        
# import time
# import ws2812_clock_face
# ds = ws2812_clock_face.Face()  
# ds.show_time(2017, 2, 25, 13, 47, 25); time.sleep(2) 
 