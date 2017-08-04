from time import sleep
import shift_register
import matrix_codes

CLEAR_VALUE = 0x00

REG_NO_OP=0X00
REG_DIGIT0=0X01
REG_DIGIT1=0X02
REG_DIGIT2=0X03
REG_DIGIT3=0X04
REG_DIGIT4=0X05
REG_DIGIT5=0X06
REG_DIGIT6=0X07
REG_DIGIT7=0X08
REG_DECODE_MODE=0X09
REG_INTENSITY=0X0A
REG_SCAN_LIMIT=0X0B
REG_SHUTDOWN=0X0C
REG_DISPLAY_TEST=0X0F


class MaxMatrix(shift_register.Shift_register):

    def __init__(self, 
                 dio_pin_id = 13, clk_pin_id = 14, stb_pin_id = 15, lsbfirst = False,
                 intensity = 0x01,
                 matrix_count_row = 1, matrix_count_column = 2, 
                 columns_per_matrix = 8, dots_per_column = 8):
                 
        super().__init__(dio_pin_id, clk_pin_id, stb_pin_id, lsbfirst)
        self.intensity = intensity
        self.matrix_count_row = matrix_count_row
        self.matrix_count_column = matrix_count_column
        self.matrix_count = matrix_count_row * matrix_count_column 
        self.columns_per_matrix = columns_per_matrix
        self.dots_per_column = dots_per_column
        self.buffer_length = self.matrix_count * self.columns_per_matrix
        self.buffer = [0] * self.buffer_length

        commands = [(REG_SHUTDOWN, 0x00),
                    (REG_DISPLAY_TEST, 0x00),
                    (REG_SCAN_LIMIT, 0x07), 
                    (REG_DECODE_MODE, 0x00),
                    (REG_SHUTDOWN, 0x01)]
        
        for command in commands:
            self.setCommand(*command)
            
        self.setIntensity(self.intensity) 
        self.clear()        
            
    
    def latch(self):
        self.stb.value(1)
        
        
    def setRegister(self, addr, value):
        self.shiftOut(addr, raise_stb = False)
        self.shiftOut(value, raise_stb = False)
        

    def setCommand(self, command, value):
        for i in range(self.matrix_count):
            self.setRegister(command, value)
            
        self.latch()
        

    def setIntensity(self, intensity):
        self.setCommand(REG_INTENSITY, intensity)


    def setColumnAll(self, col, value):        
        for i in range(self.matrix_count):
            self.setRegister(col + 1, value)
            self.buffer[col + i * self.columns_per_matrix] = value
            
        self.latch()    
        

    def clear(self, value = CLEAR_VALUE):
        for i in range(self.columns_per_matrix):
            self.setColumnAll(i, value)
            
        for i in range(self.buffer_length):
            self.buffer[i] = value 
            
            
    def fill(self, value = 0xFF): 
        for i in range(self.buffer_length):
            self.buffer[i] = value
            
        self.reload()
            

    def setColumn(self, col, value):        
        targeted_matrix = int(col / self.columns_per_matrix)
        column = col % self.columns_per_matrix
        
        for i in range(self.matrix_count):
            if i == targeted_matrix:
                self.setRegister(column + 1, value)
            else:
                self.setRegister(REG_NO_OP, CLEAR_VALUE) 
                
        self.latch()        
        self.buffer[col] = value 
            

    def setDot(self, col, row, on = True):
        self.buffer[col] = self.buffer[col] | (1 << row) if on else self.buffer[col] & ~(1 << row)

        targeted_matrix = int(col / self.columns_per_matrix)
        column = col % self.columns_per_matrix
        
        for i in range(self.matrix_count):
            if i == targeted_matrix:
                self.setRegister(column + 1, self.buffer[col])
            else:
                self.setRegister(REG_NO_OP, CLEAR_VALUE)
                
        self.latch()
        

    def writeSprite(self, x, y, sprite):
        w = sprite[0]
        h = sprite[1]
        
        if h == self.dots_per_column and y == 0:
            for i in range(w):
                c = x + i
                if c >= 0 and c < self.buffer_length:
                    self.setColumn(c, sprite[i+2])
        else:
            for i in range(w):
                for j in range(h):
                    c = x + i
                    r = y + j
                    if c >= 0 and c < self.buffer_length and r >= 0 and r < self.dots_per_column:
                        self.setDot(c, r, (sprite[i+2] & 1<<j) != 0)
                        

    def showChar(self, char, 
                 col_start = 0, 
                 fixed_width = -1, 
                 left_padding = 0, right_padding = 1, 
                 reload = True):
                 
        w, h = matrix_codes.get_char_dimension(char)
        
        for c, byte in enumerate(matrix_codes.get_char_bitmap_bytes(char)):
            if col_start + left_padding + c >= self.buffer_length: break
            self.buffer[col_start + left_padding + c] = byte
            
        if reload: self.reload()
        return col_start + max(w, fixed_width)  + (left_padding + right_padding)


    def showString(self, string, 
                   col_start = 0, 
                   fixed_width = -1, 
                   left_padding = 0, right_padding = 1, 
                   reload = True): 
                   
        col_to_start = col_start
        
        for char in list(string):
            if col_to_start >= self.buffer_length: break
            col_to_start = self.showChar(char, col_to_start, fixed_width, left_padding, right_padding, False)            
                
        if reload: self.reload()
        return col_to_start
                
        
    def reload(self):        
        for col in range(self.columns_per_matrix):
            buffer_index = col
            for matrix in range(self.matrix_count):
                self.setRegister(col + 1, self.buffer[buffer_index])
                buffer_index += self.columns_per_matrix
                
            self.latch()
        

    def shiftLeft(self, rotate = True, fill_value = CLEAR_VALUE):
        old = self.buffer[0]      
        
        for i in range(self.buffer_length - 1):
            self.buffer[i] = self.buffer[i + 1]
            
        self.buffer[self.buffer_length - 1] = old if rotate else fill_value   
        self.reload() 
        

    def shiftRight(self, rotate = True, fill_value = CLEAR_VALUE):  
        old = self.buffer[self.buffer_length - 1]
        
        for i in range(1, self.buffer_length)[::-1]:
            self.buffer[i] = self.buffer[i - 1]

        self.buffer[0] = old if rotate else fill_value        
        self.reload() 
        

    def shiftUp(self,  rotate = True):
        for i in range(self.buffer_length):
            b = self.buffer[i] & 1
            self.buffer[i] >>= 1
            
            if rotate:
                self.buffer[i] = self.buffer[i] | b<<(self.dots_per_column - 1)
                
        self.reload()
        

    def shiftDown(self, rotate = True):        
        for i in range(self.buffer_length):
            b = self.buffer[i] & 1<<(self.dots_per_column - 1)
            self.buffer[i] <<= 1
            if rotate:
                self.buffer[i] = self.buffer[i] | b>>(self.dots_per_column - 1)
                
        self.reload() 

