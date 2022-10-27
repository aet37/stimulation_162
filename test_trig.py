# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO
import time

input_pin = 11
trigger_pin = 13

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
		total_frames += 1
		print('Camera Acquisition Started ...')

	else:
		# Count the edges
		channel = GPIO.wait_for_edge(input_pin, GPIO.FALLING, timeout=5000)

		if channel is not None:
			print('  Frame')
			total_frames += 1
		else:
			print('  Program Finished.')
			print('Total Frames: ', total_frames)
			GPIO.cleanup()
			break


'''
	else:
		# Check if program done
		if GPIO.input(input_pin) == 0:
		else
			# Count the edges
			channel = GPIO.wait_for_edge(input_pin, GPIO.FALLING, timeout=5000)
			total_frames += 1
			print('  Frame')
'''