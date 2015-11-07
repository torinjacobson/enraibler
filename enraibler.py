#!/usr/bin/env python

import os
if (os.geteuid() != 0):
    exit("Must run as root!")
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD

import JackdInit
import AudioDelay
import LcdWrapper
lcd = LcdWrapper.LcdWrapper()

# Code for gracefully killing script
import signal
import sys
def signal_handler(signal, frame):
    print("Handling SIGINT...")
    global audiodelay
    audiodelay.kill()
    GPIO.cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


GPIO_ENC_A = 9
GPIO_ENC_B = 10
GPIO_BUTTON_0 = 11

delay = 0


# Encoder debounce code adapted from Circuits@Home -
# https://www.circuitsathome.com/mcu/reading-rotary-encoder-on-arduino
old_ab = 0
def readEncoder():
    enc_states = [0,-1,1,0,1,0,0,-1,-1,0,0,1,0,1,-1,0]
    global old_ab
    old_ab = old_ab << 2            # remember prev state
    enc_port = (GPIO.input(GPIO_ENC_B) << 1) + GPIO.input(GPIO_ENC_A)
    old_ab = old_ab | ( enc_port & 0x03 )    # add current state
    old_ab = old_ab & 0x0f
    return enc_states[old_ab]

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
    JackdInit.JackdInit()
    global audiodelay
    audiodelay = AudioDelay.AudioDelay()
    audio_no_delay = AudioDelay.AudioDelay()
    audio_no_delay.begin_delay_ms(0)

    # Use chip's GPIO numbering scheme
    GPIO.setmode(GPIO.BCM)

    # setup user GPIOs 
    GPIO.setup(GPIO_BUTTON_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_ENC_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(GPIO_ENC_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event handlers
    GPIO.add_event_detect(GPIO_ENC_A, GPIO.BOTH, callback=encoderEventHandler)
    GPIO.add_event_detect(GPIO_ENC_B, GPIO.BOTH, callback=encoderEventHandler)

    global lcd
    lcd.set_brightness(50)
    delay_prev = -1
    while True:
        if (GPIO.input(GPIO_BUTTON_0)):
            # Button is released. Go into enraible mode.
            audio_no_delay.setvolume(0)
            audiodelay.setvolume(1)

            delay_cur = get_delay_ms()
            if (delay_cur != delay_prev):
                # delay audio in 100ms increments.
                audiodelay.begin_delay_ms(delay_cur)
                delay_prev = delay_cur
            lcd.printline("Delay: " + str(delay_cur / 1000) + "s")
        else:
            # Button is being pressed. Go into bypass mode.
            lcd.printline("BYPASS")
            audiodelay.setvolume(0)
            audio_no_delay.setvolume(1)

        time.sleep(0.05)
main()
