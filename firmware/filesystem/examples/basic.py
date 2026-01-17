from hardware.main import Hardware
hw = Hardware()

# Turn On LEDs - 0 for off, 1 for on
leds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # All off at first
hw.write_leds(leds)
leds[0] = 1 # Turn on 1st LED
hw.write_leds(leds)

# Read Button Values -> Get a list (Up, Down, Left, Right)
button_val_list = hw.read_buttons()
button_up_pressed = button_val_list[0]
print("List of Button Values:", button_val_list)
print("Is Up Button Pressed:", button_up_pressed)

# Play Buzzer
import time

hw.buzzer_on(440) # Number is the frequency
time.sleep(1)
hw.buzzer_off()

song = 'mirrortune:d=16,o=5,b=160:32c6,32p,c6,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,32f5,32p,f5,g5,p,f5,p,d5,p,c5,p,a#4,p,c5,p,g4,f4,8p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,f5,f#5,g5,p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,g6,f6,p,g6,4p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,32f5,32p,f5,g5,p,f5,p,d5,p,c5,p,a#4,p,c5,p,g4,f4,8p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,f5,f#5,g5,p,f5,f#5,g5,p,f5,f#5,4g5,8p'
hw.play_rtttl(song)

