import asyncio
import random
import time
from hardware.ble_comms import *

async def led_pwm_duration(hw, leds, duration, always=False):
    ticks = time.ticks_ms()
    while always or time.ticks_ms() - ticks < duration:
        time.sleep(0.00001)
        hw.write_leds([0]*10)
        await asyncio.sleep(0.02)
        hw.write_leds(leds) 



async def cycle_down(hw, val):
    leds = [1,0,0,0,0,0,0,0,0,0]
    for i in range(val):
        hw.write_leds(leds)
        old = leds.index(1)   # find current 1
        new = (len(leds) + old - 1) % len(leds)
        leds[old] = 0
        leds[new] = 1
        hw.buzzer_on(440)
        await asyncio.sleep(0.05)
        hw.buzzer_off()
        await asyncio.sleep(0.05)
        

async def cycle_up(hw, val):
    leds = [1,0,0,0,0,0,0,0,0,0]
    for i in range(val):
        hw.write_leds(leds)
        old = leds.index(1)   # find current 1
        new = (len(leds) + old + 1) % len(leds)
        leds[old] = 0
        leds[new] = 1
        hw.buzzer_on(440)
        await asyncio.sleep(0.05)
        hw.buzzer_off()
        await asyncio.sleep(0.05)
        
async def dice_roll(hw, val, start):
    print("Pattern to Play:", val)
    all_on = [1,1,1,1,1,1,1,1,1,1]
    hw.write_leds(all_on)
    
    mode = val[0]
    curr = int(val[1:])
    
    win = (
        (start and int(val[1:].strip()) % 2 == 0) or
        (not start and int(val[1:].strip()) % 2 == 1)
    )
    
    if mode == "A":
        while curr > 10:
            print(curr)
            await cycle_down(hw, 10)
            curr -= 10
        await cycle_down(hw, curr)
    elif mode == "B":
        while curr > 10:
            print(curr)
            await cycle_up(hw, 10)
            curr -= 10
        await cycle_up(hw, curr)
    elif mode == "C":
        curr = val[1:]
        leds = [1,0,0,0,0,0,0,0,0,0]
        for c in curr:
            hw.write_leds(leds)
            pos = int(c)
            old = leds.index(1)   # find current 1
            new = pos
            leds[old] = 0
            leds[new] = 1
            hw.buzzer_on(440)
            await asyncio.sleep(0.05)
            hw.buzzer_off()
            await asyncio.sleep(0.05)
    
    if (not win):
        hw.write_leds([0]*10)
    
    await asyncio.sleep(5)
    
    
def random_generate_pattern(mode_int=None):    
    modes = "ABC"
    if mode_int is None: mode_int = random.randint(0,len(modes)-1)
    pattern = modes[mode_int]

    if pattern == "C":
        for i in range(random.randint(25,75)):
            pattern += str(random.randint(0,9))
    else:
        pattern += str(random.randint(25,75))
    
    return pattern


async def unlock(hw):
    while True:
        leds = [0,0,0,0,1,1,1,1,1,1]
        
        while True:
            time.sleep(0.00001)
            hw.write_leds([0]*10)
            button_val_list = hw.read_buttons()
            button_down_pressed = button_val_list[1] # Down bitton
            if (button_val_list[1]): # Bluetooth mode
                break
            elif (button_val_list[2] & button_val_list[3]):
                TEXT = random_generate_pattern(2)
                print(f"dice: {TEXT}")
                await dice_roll(hw, TEXT, 1)
            elif (button_val_list[2]):
                TEXT = random_generate_pattern(0)
                print(f"dice: {TEXT}")
                await dice_roll(hw, TEXT, 1)
            elif (button_val_list[3]):
                TEXT = random_generate_pattern(1)
                print(f"dice: {TEXT}")
                await dice_roll(hw, TEXT, 1)
                
            await asyncio.sleep(0.02)
            hw.write_leds(leds)
            
        leds = [0,0,0,0,1,1,1,1,1,1]
        hw.write_leds(leds)
        time.sleep(random.random())
        
        client = BLETextClient(target_name="dice", scan_time_ms=1000)
        value = await client.run()
        print(value)
        
        if value is not None:
            hw.buzzer_on(329)
            await dice_roll(hw, value.decode(), 0)
            continue
        
        TEXT = random_generate_pattern()
        print(f"dice: {TEXT}")
        server = BLETextServer(name="dice",text=TEXT)
        await server.run()
        
        # after downloading
        await dice_roll(hw, TEXT, 1)

if __name__ == "__main__":
    from hardware.main import Hardware
    hw = Hardware()
    asyncio.run(unlock(hw))





