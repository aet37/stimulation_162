# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO
import time

input_pin = 2
trigger_pin = 4

# Set up trigger input GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down

total_frames = 0

# Loop Raspi to listen for frames
while True:

	# Watit for Acquisition to start if no frames
	if total_frames == 0:
		GPIO.wait_for_edge(input_pin, GPIO.RISING)
		print('Camera Acquisition Started ...')
	else:
		# Check if program done
		if GPIO.input(input_pin) == 0:
			time.sleep(0.02)
			print('  Program Finished.')
			print('Total Frames: ', total_frames)
		# Count the edges
		GPIO.wait_for_edge(input_pin, GPIO.FALLING)
		total_frames += 1
		print('  Frame')
