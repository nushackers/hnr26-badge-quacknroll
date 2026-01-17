import asyncio
import random
import time

async def blink_random(hw):
    leds = [1,0,0,0,0,0,0,0,0,0]
    while True:
        old = leds.index(1)   # find current 1
        new = random.randrange(len(leds))
        leds[old] = 0
        leds[new] = 1
        hw.write_leds(leds)
        await asyncio.sleep(0.1)

async def cycle(hw):
    leds = [1,0,0,0,0,0,0,0,0,0]
    while True:
        old = leds.index(1)   # find current 1
        new = (old + 1) % len(leds)
        leds[old] = 0
        leds[new] = 1
        hw.write_leds(leds)
        await asyncio.sleep(0.1)

async def cycle_down(hw):
    leds = [1,0,0,0,0,0,0,0,0,0]
    while True:
        old = leds.index(1)   # find current 1
        new = (len(leds) + old - 1) % len(leds)
        leds[old] = 0
        leds[new] = 1
        hw.write_leds(leds)
        await asyncio.sleep(0.1)
    
    
async def led_pwm_duration(hw, leds, duration, always=False):
    ticks = time.ticks_ms()
    while always or time.ticks_ms() - ticks < duration:
        time.sleep(0.00001)
        hw.write_leds([0]*10)
        await asyncio.sleep(0.02)
        hw.write_leds(leds) 

    
async def smiley_face(hw):
    leds = [1,1,1,0,0,1,0,1,1,1]
    while True:
        await led_pwm_duration(hw, leds, 0, True)
    
async def flat_face(hw):
    leds = [0,1,1,0,0,1,0,1,1,0]
    while True:
        await led_pwm_duration(hw, leds, 0, True)

async def all_on(hw):
    leds = [1,1,1,1,1,1,1,1,1,1]
    while True:
        await led_pwm_duration(hw, leds, 0, True)

async def tick(hw, duration):
    leds = [1,0,1,0,1,0,0,1,0,0]
    hw.write_leds(leds)
    await asyncio.sleep(duration/1000)
    
async def cross(hw, duration):
    leds = [1,0,0,1,1,0,0,1,1,0]
    hw.write_leds(leds)
    await asyncio.sleep(duration/1000)