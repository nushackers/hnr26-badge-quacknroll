"""
aw9523.py

Basic driver for Adafruit's AW9523, Modified to work with the "Quack & Roll" Badge
Written for micropython, no dependencies.
Largely inspired from https://github.com/clapeyre/micropython-aw9523/blob/main/aw9523.py
"""

### Bitwise Helper Functions #########################################################################

def is_bit_on(bytestring, byte_index, bit_index):
    if not (0 <= byte_index < len(bytestring)):
        raise IndexError("Byte index out of range for the bytestring.")
    if not (0 <= bit_index < 8):  # A byte has 8 bits (0-7)
        raise ValueError("Bit index must be between 0 and 7.")

    # Get the integer value of the specific byte
    byte_value = bytestring[byte_index]

    # Create a bitmask with a 1 at the desired bit position
    mask = 1 << bit_index

    # Perform a bitwise AND operation and check if the result is non-zero
    return (byte_value & mask) != 0

def bits_to_int(bits):
    """Convert list of bits (MSB → LSB) into integer."""
    value = 0
    for b in bits:
        value = (value << 1) | b
    return value

### AW9523 Main Class #########################################################################

_AW9523_DEFAULT_ADDR   = const(0x58)
_AW9523_REG_CHIPID     = const(0x10)  # Register for hardcode chip ID
_AW9523_REG_SOFTRESET  = const(0x7F)  # Register for soft resetting
_AW9523_REG_INTENABLE0 = const(0x06)  # Register for enabling interrupt
_AW9523_REG_GCR        = const(0x11)  # Register for general configuration
_AW9523_REG_LEDMODE    = const(0x12)  # Register for configuring const current

class AW9523:
    _pin_to_addr = ([0x24 + pin for pin in range(7)] +
                    [0x20 + pin - 8 for pin in range(8, 12)] +
                    [0x2C + pin - 12 for pin in range(12, 16)])

    def __init__(self, i2c_bus, address=_AW9523_DEFAULT_ADDR):
        self.i2c_bus = i2c_bus
        self.address = address
        if (list(self.i2c_bus.readfrom_mem(address, _AW9523_REG_CHIPID, 1)) !=
            [0x23]):
            raise AttributeError("Cannot find a AW9523")
        self.reset()

    def _write(self, addr, *vals):
        self.i2c_bus.writeto_mem(self.address, addr, bytearray(list(vals)))

    def write(self, addr, *vals):
        self._write(addr, *vals)
        
    def enable_interrupts(self):
        self._write(_AW9523_REG_INTENABLE0, 0xff, 0b00001111) # 0 to enable interrupt for buttons
        
    def disable_interrupts(self):
        self._write(_AW9523_REG_INTENABLE0, 0xff, 0xff) # 0 to enable interrupt for buttons
        
    def reset(self):
        """Perform a soft reset, check datasheets for post-reset defaults!"""
        self._write(_AW9523_REG_SOFTRESET, 0)
        self._write(_AW9523_REG_GCR, 0b00010000)  # pushpull output
        self.disable_interrupts()        
        self._write(_AW9523_REG_LEDMODE, 0b11111111, 0b11111111) # Sets all to GPIO mode
        self._write(0x4, 0b11000000, 0b11110000) # Input Output state - 1 for input, 0 for output
    
    ### Main LED/ Button Functions ######################################
    def btn_read(self):
        indices = [(1, 4), (1, 5), (1, 6), (1, 7)]
        out = []
        val = self.i2c_bus.readfrom_mem(self.address, 0x00, 2)
        for x,y in indices:
            out.append(is_bit_on(val, x, y))
        return out
        ## up, down, left, right
  
    def led_write(self, ledstate):
        ledstate = ledstate[::-1]
        val1 = ([0]*2 + ledstate[0:6])
        val2 = ([0]*4 + ledstate[6:])
        self._write(0x02, bits_to_int(val1), bits_to_int(val2))
    
    ### Connectivity Pins ################################################
    def pad_config(self, mode):
        val = 0b00000000
        if mode == 1: val = 0b01000000 # 1 for input (pad A)
        elif mode == 2: val = 0b10000000
        elif mode == 3: val = 0b11000000
        self._write(0x4, val)
        
    def pad_read_A(self):
        x, y = (0,6)
        val = self.i2c_bus.readfrom_mem(self.address, 0x00, 2)
        return (is_bit_on(val, x, y))
        
    def pad_read_B(self):
        x, y = (0,7)
        val = self.i2c_bus.readfrom_mem(self.address, 0x00, 2)
        return (is_bit_on(val, x, y))
    
    def pad_write(self, a, b):
        self.pad_state = [b, a]
        val1 = (self.pad_state+[0]*6)
        self._write(0x02, bits_to_int(val1))
        
    def pad_write_A(self, val):
        self.pad_state[1] = val
        val1 = (self.pad_state+[0]*6)
        self._write(0x02, bits_to_int(val1))
        
    def pad_write_B(self, val):
        self.pad_state[1] = val
        val1 = (self.pad_state+[0]*6)
        self._write(0x02, bits_to_int(val1))
        
        