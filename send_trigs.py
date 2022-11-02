# Import Library to control RasPi GPIO
import sys
import RPi.GPIO as GPIO
import time
import keyboard
from threading import Thread, Event

'''
	@DATE 1 November 2022
	@AUTHORS Andrew T. (aet37 atpitt), Adiya R.
	@PURPOSE For NeuroImaging Lab, 2 Photon system in room 162
'''

###################################################################################################
## Function to count the frames taken
###################################################################################################
def listen_2P_frames(noff, ntr, nimtr, img_freq):

	# Print the sequence to user
	print('Running Stimulation...')
	print('______________________________')
	print('  noff = ', noff)
	print('  nimtr = ', nimtr)
	print('  ntr = ', ntr)
	print(' ')
	print('  Stimulus Duration: ', dur, 's')
	print('  Stimulus Rrequency: ', freq, 'Hz')
	print('  Pulse Width of Stimulus: ', pw, 'ms')
	print(' ')
	print('  Acquisition Time: ', round((noff + (nimtr*ntr)) * img_freq, 1), ' min')
	print(' ')

	# Set up counting variables
	total_frames = 0
	started = False

	# Compute frames we need to stimulate on
	stim_frames = []
	for i in range(1, ntr + 1):
		stim_frames.append(noff + nimtr*(i-1) + 1)

	print('  Stimulus delivered at frames: ', stim_frames)
	print(' ')
	print(' NOTE: IF YOU WANT TO TERMINATE PROGRAM PLEASE HOLD \'c\' AND \'z\' KEYS followed by [cntrl] + z')
	print('   using only [cntrl]+z will cause unclean exit')
	print(' ')
	print('______________________________')

	# Loop Raspi to listen for frames
	while True:

		# Watit for Acquisition to start if no frames
		if not started:
			print('  Waiting for Camera Acquisition ...')
			print(' ')
			GPIO.wait_for_edge(input_pin, GPIO.RISING)
			started = True
			total_frames += 1
			print('  Camera Acquisition Started.')

		else:
			# Count the edges
			channel = GPIO.wait_for_edge(input_pin, GPIO.RISING, timeout=3000)

			if channel is not None:
				total_frames += 1

				if total_frames in stim_frames:	# Check if stimulation is needed
					stim_now.set()

			else:
				print(' ')
				print('Done.')
				img_done.set()
				break

###################################################################################################
## Function to trigger the simulus
###################################################################################################
def stim_trig(duration, frequency, pulse_width):

	while True:

		# If imaging is done, return
		if img_done.is_set():
			return None

		# If signal to simulat is set, send stimulation pulses
		if stim_now.is_set():
			print(' Stim run ', stim_run)
			stim_run += 1 	# increment stim counter

			for i in range(duration):
				for j in range(frequency):
					GPIO.output(trigger_pin, 1)
					time.sleep(pulse_width/1000)
					GPIO.output(trigger_pin, 0)
					time.sleep((1/frequency) - (pulse_width/1000))


			stim_now.clear()
		# Take no action otherwise
		else:
			continue

###################################################################################################
## Function to monitor the keyboard for an exit signal to do clean exit
###################################################################################################
def exit_monitor():
	while True:
		# Exit program cleanly (clear GPIO) if 'c' and 'z' are pressed at same time
		if keyboard.is_pressed('c') and keyboard.is_pressed('z'):
			GPIO.cleanup()
			print(' ')
			print('TERMINATED STIM PROGRAM.')
			print (' ')
			quit()

		if img_done.is_set():
			break

	time.sleep(0.5)
	img_done.clear()

###################################################################################################
## Main function to call frame count and stimulation manager functions
###################################################################################################
def run_trig(noff, nimtr, ntr, duration, frequency, pulse_width, img_freq, inpin=11, trigpin=13):
	'''

	run_trig: Function to sychronize frame acquisitions with stimulus delivery. For use in RasPi. Written for room 162.

		INPUTS:
			noff 		- number of frames of rest at the begining
			nimtr 		- number of frames per trial
			ntr 		- number of trails for stimulus

			duration 	- duration of stimulus in SECONDS
			frequency	- frequency of stimulus in HZ
			pulse_width - pulse width of stimulus in MS

			(optional)
			input_pin	- pin to connect to camera triggers (default = 11)
			trigger_pin	- pin to connect to stimulation manager (default = 13)

		OUTPUTS:
			None

		NOTE:
			- PRESS 'c' and 'z' KEY AT SAME TIME TO EXIT PROGRAM

			- Error checking will occur for noff, nimtr, and ntr to ensure valid values
			- Error checking will occur for frequency and pulse width to ensure no negative time pause in program

	'''

	# Convert all arguments inputed to integers (inputed as strings if comes from command line)
	noff = int(noff)
	nimtr = int(nimtr)
	ntr = int(ntr)
	duration = int(duration)
	frequency = int(frequency)
	pulse_width = int(pulse_width)
	inpin = int(inpin)
	trigpin = int(trigpin)
	img_freq = int(img_freq)

	# Make input and trigger pins global variables
	global input_pin
	global trigger_pin
	input_pin = inpin
	trigger_pin = trigpin

	# Make duration, freq, pulse width global for easy printout
	global dur, freq, pw
	dur = duration
	freq = frequency
	pw = pulse_width

	# Error check to make sure that stimulus parameters are valid
	if (noff < 0) or (nimtr < 1) or (ntr < 0):
		print('')
		print('Error: INVALID VALUES FOR noff, nimtr, AND/OR ntr')
		print('')
		raise RuntimeError

	if ((1/frequency) - (pulse_width/1000) < 0):
		print('')
		print('Error: INVALID STIMULATION PARAMETER: (1/f - pulse_width < 0)')
		print('  Pulse width must be less than stimulation period')
		print('  To do DC stimulaiton (0Hz), set pulse_width equal to the sitmulation period.')
		print('')
		raise RuntimeError

	# Define stim counter
	global stim_run
	stim_run = 1

	# Define the events
	global stim_now
	stim_now = Event()
	stim_now.clear()
	global img_done
	img_done = Event()
	img_done.clear()

	# Set up trigger input GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down
	GPIO.setup(trigger_pin, GPIO.OUT) # internal pull down

	# Define the 2 threads
	listen_thread = Thread(target=listen_2P_frames, args=[noff, ntr, nimtr, img_freq])
	stim_thread = Thread(target=stim_trig, args=[duration, frequency, pulse_width])
	exit_tread = Thread(target=exit_monitor)

	# Start the threads
	listen_thread.start()
	exit_tread.start()
	stim_thread.start()

	# Join the threads to end program
	stim_thread.join()
	exit_tread.join()

	# Cleanup the GPIO
	GPIO.cleanup()

###################################################################################################
## If called from bash, parse the input arguments provided and call the run_trig funciton
###################################################################################################
if __name__ == "__main__":
	if len(sys.argv) > 8:
		globals()['run_trig'](sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
	else:
		globals()['run_trig'](sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])