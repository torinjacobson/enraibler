#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

GPIO_ENC_0 = 9
GPIO_ENC_1 = 10
GPIO_BUTTON_0 = 11

direction = "no"
update = False
delay = 0

lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 27
lcd_d7 = 22
lcd_backlight = 4

lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, 
					lcd_columns, lcd_rows, lcd_backlight)

def buttonEventHandler(pin):
	print pin

def encoderEventHandler(pin):
	global direction
	global update
	global delay

	if (GPIO.input(9) == GPIO.input(10)):
		direction = "cw"
		delay = delay + 1
	else:
		direction = "ccw"
		if (delay > 0):
			delay = delay - 1
	update = True

def main():
	

	# Use chip's GPIO numbering scheme
	GPIO.setmode(GPIO.BCM)

	# setup user GPIOs 
	GPIO.setup(GPIO_BUTTON_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	# Add event handlers
	GPIO.add_event_detect(GPIO_BUTTON_0, GPIO.FALLING, callback=buttonEventHandler, bouncetime=200)
	GPIO.add_event_detect(GPIO_ENC_0, GPIO.BOTH, callback=encoderEventHandler, bouncetime=75)

	global update
	global delay
	global lcd
	while True:
		if (update):
			print direction
			update = False
			# let's print the delay on the LCD for now.
			lcd.clear()
			lcd.message("delay = " + str(delay))
		time.sleep(0.01)

	GPIO.cleanup()

main()
