
import Adafruit_CharLCD as LCD
# We want stuff to happen on screen as soon as possible!
lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 27
lcd_d7 = 22
lcd_columns = 16
lcd_rows    = 2
lcd_backlight = 4
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                        lcd_columns, lcd_rows, lcd_backlight)

# Make LCD stuff happen as soon as possible.
lcd.message("Init LCD...")

# PWM the backlight for brightness control
from RPIO import PWM
import signal
        
# Threading is used for fading LCD backlight in background
import threading
import time
import numpy

BL_FLASHING = 0
BL_SOLID = 1
BL_FADING = 2


class LcdWrapper:
        def __init__(self):
            self.message_on_screen = "Init PWM..."
            lcd.message(self.message_on_screen)
            
            PWM.setup()
            PWM.init_channel(0)
            PWM.set_loglevel(2)
            ## PWM likes to exit everything on child signal... Prevent this.
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
            
            self.refresh_ms = 10.0
            self.backlight_state = BL_FADING
            self.fade_array = numpy.array([100])
            self.fade_index = 0
            self.fade_incr = 1
            self.run_thread = True
            bl_thread = threading.Thread(target=self._bl_brightness_task)
            bl_thread.start()

        def _set_brightness(self, percent):
            # Make our percentage logarithmic from 0 to 100 for a more natural brightness curve
            percent = (float(percent)/10)**2
            # Divide the 20ms period into 4 pulses so we get 200Hz
            # pulse width in 10us increments.
            pulse_width = int((100-percent) * 5)

            PWM.add_channel_pulse(0, lcd_backlight, start=0,    width=pulse_width)
            PWM.add_channel_pulse(0, lcd_backlight, start=499,  width=pulse_width)
            PWM.add_channel_pulse(0, lcd_backlight, start=999,  width=pulse_width)
            PWM.add_channel_pulse(0, lcd_backlight, start=1499, width=pulse_width)

        # only update message if necessary.
        def printline(self, message, line=0):
            # Left-justify the message to pad with spaces.
            message = message.ljust(20)
            if (message != self.message_on_screen):
                lcd.home()
                lcd.message(message)
                self.message_on_screen = message
            
        def _bl_brightness_task(self):
            ## Loop until killed and handle changes in LCD backlight brightness.
            while(self.run_thread):
                if (self.backlight_state == BL_FLASHING):
                    self._set_brightness(self.fade_array[self.fade_index])
                    self.fade_index = self.fade_index + self.fade_incr
                    if (self.fade_index == self.fade_array.size):
                        self.fade_incr = -1
                        self.fade_index = self.fade_index - 1
                    elif (self.fade_index == 0):
                        self.fade_incr = 1

                elif (self.backlight_state == BL_FADING):
                    self._set_brightness(self.fade_array[self.fade_index])
                    self.fade_index = self.fade_index + self.fade_incr
                    if (self.fade_index == self.fade_array.size):
                        self.fade_incr = 0
                        self.fade_index = self.fade_index - 1

                time.sleep(self.refresh_ms/1000)

        def set_backlight_flashing(self, minimum, maximum, period_ms):
            self.fade_index = 0
            self.fade_incr = 1
            self.fade_array = numpy.linspace(minimum, maximum, (period_ms/2)/self.refresh_ms)
            self.backlight_state = BL_FLASHING

        def set_backlight_solid(self, percent, duration_ms=10):
            start = self.fade_array[self.fade_index]
            self.fade_index = 0
            self.fade_incr = 1
            self.fade_array = numpy.linspace(start, percent, duration_ms/self.refresh_ms)
            self.backlight_state = BL_FADING

        def set_backlight_fading(self, start, end, duration_ms):
            self.fade_index = 0
            self.fade_incr = 1
            self.fade_array = numpy.linspace(start, end, duration_ms/self.refresh_ms)
            self.backlight_state = BL_FADING
            
        def cleanup(self):
            lcd.clear()
            self.run_thread = False
            PWM.cleanup()

