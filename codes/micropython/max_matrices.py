import time
import max_matrix
       

class Matrices(max_matrix.MaxMatrix): 
    
    def __init__(self, 
                 dio_pin_id = 13, clk_pin_id = 14, stb_pin_id = 15, lsbfirst = False,
                 intensity = 0x01,
                 matrix_count_row = 1, matrix_count_column = 2, 
                 columns_per_matrix = 8, dots_per_column = 8,
                 width_per_digit = 4):
        
        super().__init__(dio_pin_id, clk_pin_id, stb_pin_id, lsbfirst,
                         intensity,
                         matrix_count_row, matrix_count_column, 
                         columns_per_matrix, dots_per_column) 
                 
        self.width_per_digit = width_per_digit
        self.display_digit_count = int(matrix_count_row * matrix_count_column * columns_per_matrix  / self.width_per_digit)        
        self.display_digit_min = - 10 ** (self.display_digit_count - 1) + 1
        self.display_digit_max = 10 ** (self.display_digit_count) - 1
        
        self.fill(); time.sleep(3);self.clear()                 
        self.showString("Hi!"); time.sleep(1) 
        
 
    # convert number to digits string and show it
    def show_number(self, number):        
        if self.display_digit_min <= number <= self.display_digit_max:
            digits = str(number)          
            self.showString(digits, fixed_width = 4, left_padding = 0, right_padding = 0)
        else:
            self.showString("Oop!")
            
            
    def show_datetime(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(month) + "{0:0>2}".format(day)
        self.showString(time_string, fixed_width = 4, left_padding = 0, right_padding = 0) 
        
        
    def show_time(self, year, month, day, hour, minute, second):
        time_string = "{0:0>2}".format(hour % 12 if hour != 12 else hour) + "{0:0>2}".format(minute)
        self.showString(time_string, fixed_width = 4, left_padding = 0, right_padding = 0) 
        