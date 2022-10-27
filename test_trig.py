# Import Library to control RasPi GPIO
import RPi.GPIO as GPIO
import time
from threading import Thread, Event

# Define pins
input_pin = 11
trigger_pin = 13

# Stimulation Parameters (in frames)
noff = 5
nimtr = 10
ntr = 5

# Define the events
stim_now = Event()
stim_now.clear()

# Function to count the frames taken
def listen_2P_frames():
	'''
	# Set up trigger input GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
	GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down
	'''

	total_frames = 0
	started = False

	# Compute frames we need to stimulate on
	stim_frames = []
	for i in range(1, ntr + 1):
		stim_frames.append(noff + nimtr*(i-1) + 1)

	print(stim_frames)

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

				if total_frames in stim_frames:	# Check if stimulation is needed
					stim_now.set()
					#print('Stim Start')

			else:
				print('  Program Finished.')
				print('Total Frames: ', total_frames)
				#GPIO.cleanup()
				break

# Function to trigger the simulus
def stim_trig():
	while True:
		if stim_now.is_set():
			print('Stim Starting...')
			stim_now.clear():
		else:
			continue



if __name__ == "__main__":

	# Set up trigger input GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
	GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down

	# Define the 2 threads
	listen_thread = Thread(target=listen_2P_frames)
	stim_thread = Thread(target=stim_trig)

	# Start the threads
	listen_thread.start()
	stim_thread.start()

	# Join the threads to end program
	stim_thread.join()

	# Cleanup the GPIO
	GPIO.cleanup()
	print('GPIO Clean.')

