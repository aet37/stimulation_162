# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO


trigger_pin = 2

# Set up trigger input GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down

#