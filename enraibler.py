#!/usr/bin/env python

import os
if (os.geteuid() != 0):
	exit("Must run as root!")
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

import AudioDelay
audiodelay = AudioDelay.AudioDelay()

import JackdInit
JackdInit.JackdInit()

# Code for gracefully killing script
import signal
import sys
def signal_handler(signal, frame):
	print("Ctrl+C")
	audiodelay.kill()
	GPIO.cleanup()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


GPIO_ENC_0 = 9
GPIO_ENC_1 = 10
GPIO_BUTTON_0 = 11

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
	global update
	update = True

def encoderEventHandler(pin):
	global update
	global delay

	if (GPIO.input(9) == GPIO.input(10)):
		delay = delay + 1
	else:
		if (delay > 0):
			delay = delay - 1

def main():
	# Use chip's GPIO numbering scheme
	GPIO.setmode(GPIO.BCM)

	# setup user GPIOs 
	GPIO.setup(GPIO_BUTTON_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	# Add event handlers
	GPIO.add_event_detect(GPIO_BUTTON_0, GPIO.FALLING, callback=buttonEventHandler, bouncetime=200)
	GPIO.add_event_detect(GPIO_ENC_0, GPIO.BOTH, callback=encoderEventHandler, bouncetime=25)

	global update
	global delay
	global lcd
	delay_prev = -1
	while True:
		if (delay != delay_prev):
			update = False
			lcd.clear()
			# delay audio in 100ms increments.
			lcd.message(str(float(delay)/10))
			audiodelay.begin_delay_ms(delay * 100)
			delay_prev = delay
		time.sleep(0.05)


main()