
import Adafruit_CharLCD as LCD
# PWM the backlight for brightness control
from RPIO import PWM

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
                                        lcd_columns, lcd_rows, self.lcd_backlight)
            
            self.message_on_screen = ""


        def set_brightness(self, percent):
            # Make our percentage logarithmic from 0 to 100 for a more natural brightness curve
            percent = (float(percent)/10)**2
            # Divide the 20ms period into 4 pulses so we get 200Hz
            # pulse width in 10us increments.
            pulse_width = int((100-percent) * 5)
            if (not PWM.is_setup()):
                PWM.setup()
                PWM.init_channel(0)

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
            
            

