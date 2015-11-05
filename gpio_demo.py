#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

GPIO_ENC_0 = 9
GPIO_ENC_1 = 10
GPIO_BUTTON_0 = 11

direction = "no"
update = False

def buttonEventHandler(pin):
	print pin

def encoderEventHandler(pin):
	global direction
	global update
	if (GPIO.input(9) == GPIO.input(10)):
		direction = "cw"
	else:
		direction = "ccw"
	update = True

def main():
	# Use chip's GPIO numbering scheme
	GPIO.setmode(GPIO.BCM)

	# setup user GPIOs (SPI MISO, MOSI, SCLK) (GPIO9,10,11)
	GPIO.setup(GPIO_BUTTON_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(GPIO_ENC_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	# Add event handlers
	GPIO.add_event_detect(GPIO_BUTTON_0, GPIO.FALLING, callback=buttonEventHandler, bouncetime=200)
	GPIO.add_event_detect(GPIO_ENC_0, GPIO.BOTH, callback=encoderEventHandler, bouncetime=75)

	global update
	while True:
		if (update):
			print direction
			update = False
		time.sleep(0.01)

	GPIO.cleanup()

main()
