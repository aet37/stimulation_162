# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO
import time

# Define pins
input_pin = 11
trigger_pin = 13

# Set up trigger input GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down

total_frames = 0
started = False

# Loop Raspi to listen for frames
while True:

	# Watit for Acquisition to start if no frames
	if not started:
		GPIO.wait_for_edge(input_pin, GPIO.RISING)
		started = True
		total_frames += 1
		print('Camera Acquisition Started ...')

	else:
		# Count the edges
		channel = GPIO.wait_for_edge(input_pin, GPIO.RISING, timeout=5000)

		if channel is not None:
			total_frames += 1
			print('  Frame ', total_frames)
		else:
			print('  Program Finished.')
			print('Total Frames: ', total_frames)
			GPIO.cleanup()
			break