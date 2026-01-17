from machine import Pin, I2C, SoftI2C, PWM
import hardware.music_player
from hardware.aw9523 import AW9523


def beep(buzzer, freq, duration):
    buzzer.freq(freq)
    buzzer.duty_u16(30000)   # volume (0â65535)
    time.sleep(duration)
    buzzer.duty_u16(0)       # stop tone
    
class Hardware:
    def __init__(self):
        ### IO Expander
        self.i2c = SoftI2C(scl=Pin(6), sda=Pin(7))
        self.aw = AW9523(self.i2c)
        self.aw_intr = Pin(10)
        ### Buzzer 
        self.buzzer = PWM(Pin(3))
        self.buzzer.duty_u16(0)

    ### IO Expander (LEDs, Buttons) ########################
    def read_buttons(self):
        return self.aw.btn_read()
    
    def write_leds(self, leds):
        self.aw.led_write(leds)
        
    ### Buzzer #############################################
    def buzzer_on(self, freq, duty=32767):
        if freq > 0:
            self.buzzer.freq(freq)
            self.buzzer.duty_u16(duty)

    def buzzer_off(self):
        self.buzzer.duty_u16(0)   
    
    def play_rtttl(self, music_rtttl):
        print("buzz mp")
        buzz_on = self.buzzer_on
        buzz_off = self.buzzer_off
        music = hardware.music_player.RTTTL(music_rtttl).notes()
        mp = hardware.music_player.MusicPlayer(buzz_on, buzz_off)
        mp.play_music(music)
    
    def get_rtttl_task(self, music_rtttl):
        print("buzz mp")
        buzz_on = self.buzzer_on
        buzz_off = self.buzzer_off
        music = hardware.music_player.RTTTL(music_rtttl).notes()
        mp = hardware.music_player.MusicPlayer(buzz_on, buzz_off)
        return mp.get_music_task(music)
    
