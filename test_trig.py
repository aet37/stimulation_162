# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO
import time
from threading import Thread

# Define pins
input_pin = 11
trigger_pin = 13


# Function to check for stimulus
def check_stim(curr_frame, noff, nimtr, ntr):
	return None

# Stimulation Parameters (in frames)
noff = 5
nimtr = 10
ntr = 5


def listen_2P_frames():
	'''
	# Set up trigger input GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
	GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down
	'''

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
			print('  Frame ', total_frames)

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


if __name__ == "__main__":

	# Set up trigger input GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
	GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down

	listen_2P_frames()

