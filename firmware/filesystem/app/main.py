from hardware.main import Hardware
from hardware.ble_comms import BLETextClient, BLETextServer
import app.led_blinks as led_blinks
import os
import machine

app_unlocks = []
def load_unlocks():
    try:
        global app_unlocks
        app_unlocks.clear()
        for i in range(100):
            exec(f"import app.unlock{i} as unlock")
            app_unlocks.append(unlock)
    except Exception as e:
        print("Limited Unlocks:", e)
load_unlocks()


import random
import asyncio
import time
import machine

rtttl_songs = [
    'rap:d=8,o=6,b=180:2d4,f4,a4,4d5,d,d,c,a5,d,d,c,d,c,d,c,a5,d,d,a5,d,c,d,c,a5,d,2d4,f4,a4,4d5,f5,d5,a4,f4,2d#4,d,d,c,d,c,d,c,a5,d,d,c,d,c,d,c,a5,d',
    'BackInBlack:d=4,o=6,b=180:e,p,p,d,d,p,p,a5,a5,p,p,p,p,8g,8e,8d,8b5,8a5,8a5,8g5,e,p,p,d,d,p,p,a5,a5,p,8b5,g5,8b5,a5,8b5,a#5,8b5,g5',
    'CuttingCrewDiedInYourArms:d=8,o=6,b=125:f#,f#,f#,f#,f#,f#,f#,f#,a,a,a,g,g,g,f#,f#,e,e,e,e,e,e,e,e,f#,f#,f#,c#,c#,c#,d,d,2f#.,e,f#,4g.,g,4f#.,d,1e,f#,e,f#,e,f#,e,d,d,2b5',
    'Quack1:d=16,o=6,b=63:8b,f,e,p,p,32e,32e,32e,32f,32e,p,p,32e,32e,32f,32e,32f,32e,p,32g5,32g5,32g5,32f#5,32e5,e5,32e5,32g5,32g5,32g5,32g5,32f#5,32e5,p,b,16b,b,8b',
    'EuropeTheFinalCountdown:d=4,o=5,b=200:p,p,8c#6.,16b,2c#6,2f#,p,p,p,8d6.,16c#6,4d6,4c#6,2b,p,p,p,8d6.,16c#6,2d6,2f#,p,p,p,8b.,16a,4b,4a,4g#,4b,2a',
    'QueenDontStopMeNow:d=8,o=6,b=125:g,g,a#5,a#5,a#5,4c,4d,p,e,e,e,4f,4g,p,4a5,4f5,f5,a5,c,f,2e,p,c,a5,4g5,4f5,4p,a5,g5,f5,4g5,g5,g5,a5,4a#5,1c', 
    'LastChristmas:d=8,o=6,b=112:4e,e,4e,4d,a5,e,e,f#,2d,a5,e,e,4f#,4d.,d,c#,d,c#,2b5,4p,4f#,f#,4e,4p,b5,f#,g,f#,4e,4p,d,c#,c#,c#,4c#,4d,4c#,4a5,2a5,4p',
    'jlohasbeeps:d=4,o=6,b=200:8f#,8f#,8f#,4e,4e,4a5,4a,e,8a5,8a5,8f#,8f#,8f#,8a5,f#,8e,8e',
    ('QZKago:d=4,o=5,b=125:8c,8d,8d#,8g4,8f#4,16g4,8g#4,8d#,16d#,8d,8d#,' +
          '8f,8d#,8d,16d#,8d,8c,16b4,8c,8d,'+
          '8d#,8g#4,16g4,8g#4,8g4,16d#,16d,16d#,8d,8c,8b4,8a4,8b4,c'+
          '8c,8d,8d#,8g4,8f#4,16g4,8g#4,8d#,16d#,8d,8d#,' +
          '8f,8d#,8d,16d#,8d,16c,16c,4g,'+
          '8d#,8g#4,16g4,8g#4,8g4,16g4,16f#4,16g4,16.,16g,16f#,16g,16.,'+
          '16f,16d#,16d,16c,16d,16d#,16f,16b4,4c'),
    'mirrortune:d=16,o=5,b=160:32c6,32p,c6,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,32f5,32p,f5,g5,p,f5,p,d5,p,c5,p,a#4,p,c5,p,g4,f4,8p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,f5,f#5,g5,p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,32g6,32p,g6,f6,p,g6,4p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,32f5,32p,f5,g5,p,f5,p,d5,p,c5,p,a#4,p,c5,p,g4,f4,8p,a#5,c6,p,a#5,p,c#6,p,c6,a#5,p,c6,p,a#5,p,f5,f#5,g5,p,f5,f#5,g5,p,f5,f#5,4g5,8p'
]

class MusicException(Exception):
    pass

# Programs
class ModeManager:
    def __init__(self, hw):
        self.hw = hw
        
        self.mode = 0;
        self.num_modes = 6 + len(app_unlocks) + 1
        self.current_task = None
        
        # Program State
        self.input_states = [0,0,0,0,0,0]
        
        #self.hw.aw.pad_config(1) # a as an input
        #self.hw.aw.pad_write(1, 1)
        
    ### Helper Tasks ##############################
    async def state_inc(self):
        self.mode = (self.mode + 1) % self.num_modes
        await self.mode_reload()
    
    async def mode_reload(self):
        if self.current_task is not None:
            self.current_task.cancel()
            self.current_task = None
            
        if self.mode == 0:
            self.current_task = asyncio.create_task(led_blinks.blink_random(self.hw))
        elif self.mode == 1:
            self.current_task = asyncio.create_task(led_blinks.cycle(self.hw))
        elif self.mode == 2:
            self.current_task = asyncio.create_task(led_blinks.cycle_down(self.hw))
        elif self.mode == 3:
            self.current_task = asyncio.create_task(self.led_button_select())
        elif self.mode == 4:
            self.current_task = asyncio.create_task(led_blinks.smiley_face(self.hw))
        elif self.mode == 5:
            self.current_task = asyncio.create_task(led_blinks.flat_face(self.hw))
        elif self.mode == self.num_modes - 1:
            self.current_task = asyncio.create_task(led_blinks.all_on(self.hw))
            try:
                await self.bluetooth_mode()
            except Exception as e:
                print("bluetooth fail")
                await led_blinks.cross(self.hw, 2000)
                machine.reset()
        elif self.mode >= 6:
            try:
                self.current_task = asyncio.create_task(app_unlocks[self.mode-6].unlock(self.hw))
            except AttributeError as e:
                print("remove invalid module")
                os.remove(f"/app/unlock{self.mode-6}.py")
                #await led_blinks.cross(self.hw, 2000)
                await self.state_inc()
        time.sleep(0.5)
            
    async def read_inputs(self):
        while True:
            self.input_states = hw.read_buttons()
            self.input_states += [hw.aw.pad_read_A()]
            await asyncio.sleep(0.1) # Polling Rate
        
    async def bluetooth_mode(self):
        if self.current_task is not None:
            self.current_task.cancel()
            self.current_task = None
        
        hw.write_leds([1]*10)
        
        while True:
            button_val_list = hw.read_buttons()
            button_down_pressed = button_val_list[1] # Down bitton
            if (button_down_pressed):
                break
            await asyncio.sleep(0.02)
        
        hw.write_leds([0]*10)
        
        client = BLETextClient()
        value = await client.run()
        print(value)
        
        if value is None or value == "":
            await led_blinks.cross(self.hw, 2000)
            machine.reset()
            return
        
        filename = f"/app/unlock{len(app_unlocks)}.py"
        with open(filename, "w") as f:
            print("Writing to file:", filename)
            f.write(value)
        await led_blinks.tick(self.hw, 2000)
        machine.reset()
        
    ### Async Programs/ Functions #####################
    async def led_button_select(self):
        leds = [1,0,0,0,0,0,0,0,0,0]
        
        hw.write_leds(leds)
        while True:
            btns = self.input_states
            if btns[3]:
                leds = leds[1:] + [leds[0]]
                hw.write_leds(leds)
            elif btns[2]:
                leds = [leds[-1]] + leds[:-1]
                hw.write_leds(leds)
            ### Music Playing
            elif btns[1]:
                state = leds.index(1)
                task = hw.get_rtttl_task(rtttl_songs[state%len(rtttl_songs)])
                asyncio.run(task())
                raise MusicException() # Trick to avoid crashing
            await asyncio.sleep(0.2)

    ### Main ##########################################
    async def main(self):
        asyncio.create_task(self.mode_reload())
        asyncio.create_task(self.read_inputs())
        
        while True:
            #asyncio.run(self.read_inputs())
            if self.input_states[0]: # Up Button
                asyncio.create_task(self.state_inc())
            await asyncio.sleep(0.2)
        
        
hw = Hardware()
mm = ModeManager(hw)

try:
    # Start the event loop and run the main coroutine
    while True:
        try:
            asyncio.run(mm.main())
        except MusicException:
            pass
except KeyboardInterrupt:
    pass # Handle manual interruption
finally:
    # Clear retained state in the event loop for subsequent runs
    asyncio.new_event_loop()


