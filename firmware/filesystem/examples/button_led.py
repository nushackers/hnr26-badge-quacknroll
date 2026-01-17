'''
Example - Turn LED on and off based on button pressed
'''
from hardware.main import Hardware
hw = Hardware()

while True:
    leds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    button_val_list = hw.read_buttons()
    for i in range(4):
        if button_val_list[i]: # Up button pressed
            leds[i] = 1
    hw.write_leds(leds)