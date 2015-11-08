
import Adafruit_CharLCD as LCD
# PWM the backlight for brightness control
from RPIO import PWM
import signal
import RPi.GPIO as GPIO

# Threading is used for fading LCD backlight in background
import threading
import time
import numpy

class LcdWrapper:
        def __init__(self):
            ## Initialize LCD for enraibler
            lcd_rs = 25
            lcd_en = 24
            lcd_d4 = 23
            lcd_d5 = 17
            lcd_d6 = 27
            lcd_d7 = 22
            self.lcd_backlight = 4

            lcd_columns = 16
            lcd_rows    = 2

            self.lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                        lcd_columns, lcd_rows)
            
            self.message_on_screen = ""

            PWM.setup()
            PWM.init_channel(0)
            PWM.set_loglevel(2)
            ## PWM likes to exit everything on child signal... Prevent this.
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        def set_brightness(self, percent):
            # Make our percentage logarithmic from 0 to 100 for a more natural brightness curve
            percent = (float(percent)/10)**2
            # Divide the 20ms period into 4 pulses so we get 200Hz
            # pulse width in 10us increments.
            pulse_width = int((100-percent) * 5)

            PWM.add_channel_pulse(0, self.lcd_backlight, start=0,    width=pulse_width)
            PWM.add_channel_pulse(0, self.lcd_backlight, start=499,  width=pulse_width)
            PWM.add_channel_pulse(0, self.lcd_backlight, start=999,  width=pulse_width)
            PWM.add_channel_pulse(0, self.lcd_backlight, start=1499, width=pulse_width)

        # only update message if necessary.
        def printline(self, message, line=0):
            # Left-justify the message to pad with spaces.
            message = message.ljust(20)
            if (message != self.message_on_screen):
                self.lcd.home()
                self.lcd.message(message)
                self.message_on_screen = message
            
            
        increment_ms = 10.0
        fade_thread_running = False
        def _fade_thread(self, start, finish, duration_ms):
            ## Wait for existing fading activity to complete before beginning this one.
            while (self.fade_thread_running):
                time.sleep(self.increment_ms/1000)
            
            self.fade_thread_running = True
            ## number of desired elements = duration / increment
            for i in numpy.linspace(start, finish, duration_ms/self.increment_ms):
                self.set_brightness(i)
                time.sleep(self.increment_ms/1000)
            self.fade_thread_running = False

        def fade_backlight(self, start, finish, duration_ms):
            lcd_fade_thread = threading.Thread(target=self._fade_thread, args=[start,finish,duration_ms])
            lcd_fade_thread.start()
            
        def cleanup(self):
            self.lcd.clear()
            PWM.cleanup()

