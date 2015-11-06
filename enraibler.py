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


GPIO_ENC_A = 9
GPIO_ENC_B = 10
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

# Encoder debounce code adapted from Circuits@Home -
# https://www.circuitsathome.com/mcu/reading-rotary-encoder-on-arduino
old_ab = 0
def readEncoder():
	enc_states = [0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0]
	global old_ab
	old_ab = old_ab << 2			# remember prev state
	enc_port = (GPIO.input(GPIO_ENC_B) << 1) + GPIO.input(GPIO_ENC_A)
	old_ab = old_ab | ( enc_port & 0x03 )	# add current state
	old_ab = old_ab & 0x0f
	return enc_states[old_ab]

def buttonEventHandler(pin):
	global update
	update = True

def encoderEventHandler(pin):
	global delay
	direction = readEncoder()
	if direction == 1:
		delay = delay+1
	elif direction == -1 and delay > 0:
		delay = delay-1

def get_delay_ms():
	# we see 4 transitions per detent, so divide by 4.
	global delay
	return round(delay / 4) * 100
	
def main():
	# Use chip's GPIO numbering scheme
	GPIO.setmode(GPIO.BCM)

	# setup user GPIOs 
	GPIO.setup(GPIO_BUTTON_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	# Add event handlers
	GPIO.add_event_detect(GPIO_BUTTON_0, GPIO.FALLING, callback=buttonEventHandler, bouncetime=200)
	GPIO.add_event_detect(GPIO_ENC_A, GPIO.BOTH, callback=encoderEventHandler)
	GPIO.add_event_detect(GPIO_ENC_B, GPIO.BOTH, callback=encoderEventHandler)

	global update
	global lcd
	delay_prev = -1
	while True:
		delay_cur = get_delay_ms()
		if (delay_cur != delay_prev):
			update = False
			lcd.clear()
			# delay audio in 100ms increments.
			lcd.message(str(delay_cur / 1000))
			audiodelay.begin_delay_ms(delay_cur)
			delay_prev = delay_cur
		time.sleep(0.1)

main()
