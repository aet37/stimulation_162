from PyQt5.QtCore import QObject, QThread, pyqtSignal
from threading import Event
import time
import os

'''
	@File: stimFunctions.py
	@Date: 26 Nov 2022
	@Author: NeuroImaging Lab, Andrew Toader

	@Purpose: support functions for the ImagingSystem GIU to control stimulation, and synchronize with imaging system

'''

# Define the Trigger pin
global TRIGGER_IN_PIN
TRIGGER_IN_PIN = 32

'''
Class to control and run the stimulation (QThread object)
'''
class stimControlNoWait(QObject):

	finished = pyqtSignal()
	force_stopped = pyqtSignal()
	stim_on = pyqtSignal()
	stim_off = pyqtSignal()
	exp_started = pyqtSignal()
	trial_number = pyqtSignal(int)

	def __init__(self, noff, nimtr, ntr, dur, freq, pw, stimToMaster8, waitForTrig, cntrl, frame_aq):
		QObject.__init__(self)
		self.ctrl = cntrl
		self.frame = frame_aq
		self.toff = noff
		self.ttr = nimtr
		self.ntr = ntr
		self.dur = dur
		self.pw = pw
		self.freq = freq
		self.toM8 = stimToMaster8
		self.do_wait = waitForTrig

	def run(self):
		# Clear output from any previous trials
		os.system('clear')

		# Check for wait
		if self.do_wait:
			'''
			****** Insert Wait Logic here ******
			'''
			# Placeholder test functionality
			while True:

				if self.frame.is_set():
					time.sleep(0.2)
					self.exp_started.emit()
					break

				if self.ctrl.is_set():
					self.force_stopped.emit()
					return
		else:
			self.exp_started.emit()

		# Wait toff time
		for i in range(self.toff):
			time.sleep(1)
			if self.ctrl.is_set():
				self.force_stopped.emit()
				return

		# Start trial runs
		for i in range(self.ntr):
			# Advance trial number for UI
			self.trial_number.emit(i + 1)

			'''
			******* Stimulation Logic here ********
			'''
			if self.toM8:

				# Send UI stimulation signal
				self.stim_on.emit()

				print('  Stimulation to M8')

				# Sleep for the remainder of the trial time (while checking for done signal)
				for a in range(self.ttr):
					# Sleep
					time.sleep(1)

					# Send UI stimulation off signal at proper time
					if a + 1 == self.dur:
						self.stim_off.emit()

					# Check if stop button has been pressed in UI
					if self.ctrl.is_set():
						self.force_stopped.emit()
						return

			else:
				print('  Stimulation to Laser...')

				# Send UI stimulation signal
				self.stim_on.emit()

				if 1/self.freq == self.pw/1000:
					print('    Now')

					# Sleep for the remainder of the stimulation time (while checking for done signal)
					for a in range(self.dur):
						time.sleep(1)
						if self.ctrl.is_set():
							self.force_stopped.emit()
							return

					# Send UI stimulation off signal
					self.stim_off.emit()

				else:
					for j in range(self.dur):
						for k in range(self.freq):
							print('    High')
							time.sleep(self.pw/1000)
							print('    Low')
							time.sleep((1/self.freq) - (self.pw/1000))

							# Check if trial was stopped
							if self.ctrl.is_set():
								self.force_stopped.emit()
								return

					# Send UI stimulation offsignal
					self.stim_off.emit()

				# Sleep for the remainder of the trial time (while checking for done signal)
				for a in range(self.ttr - self.dur):
					time.sleep(1)
					if self.ctrl.is_set():
							self.force_stopped.emit()
							return


		# Emit done signal
		self.finished.emit()

'''
Class to count the frames and synchronize stimulation (QThread object)
'''
class stimControl(QObject):

	stim_on = pyqtSignal()
	stim_off = pyqtSignal()
	trial_number = pyqtSignal(int)

	# Keep track of trial number
	tr_num = 0

	def __init__(self, stim_dur, stim_freq, stim_pw, stimToMaster8, exp_stopped):
		QObject.__init__(self)
		self.dur = stim_dur
		self.pw = stim_pw
		self.freq = stim_freq
		self.toM8 = stimToMaster8
		self.exp_stopped = exp_stopped

		os.system('clear')

	def run(self):

		self.tr_num += 1
		self.trial_number.emit(self.tr_num)

		if self.toM8:

				# Send UI stimulation signal
				self.stim_on.emit()

				print('  Stimulation to M8')

				# Sleep for the remainder of the trial time (while checking for done signal)
				for i in range(self.dur):

					# Sleep
					time.sleep(1)

					# Check if stop button has been pressed in UI
					if self.exp_stopped.is_set():
						return

				# Send UI stimulation off signal
				self.stim_off.emit()

		else:
			print('  Stimulation to Laser...')

			# Send UI stimulation signal
			self.stim_on.emit()

			# DC Case 1
			if self.freq == 0:
				print('    Now')

				# Sleep for the remainder of the stimulation time (while checking for done signal)
				for a in range(self.dur):
					time.sleep(1)
					if self.exp_stopped.is_set():
						return

				# Send UI stimulation off signal
				self.stim_off.emit()

			# DC Case 2
			elif 1/self.freq == self.pw/1000:
				print('    Now')

				# Sleep for the remainder of the stimulation time (while checking for done signal)
				for a in range(self.dur):
					time.sleep(1)
					if self.exp_stopped.is_set():
						return

				# Send UI stimulation off signal
				self.stim_off.emit()

			else:
				for j in range(self.dur):
					for k in range(self.freq):
						print('    High')
						time.sleep(self.pw/1000)
						print('    Low')
						time.sleep((1/self.freq) - (self.pw/1000))

						# Check if trial was stopped
						if self.exp_stopped.is_set():
							return

				# Send UI stimulation offsignal
				self.stim_off.emit()

'''
Class to count the frames and synchronize stimulation (QThread object)
'''
class frameCount(QObject):

	# Critical signals
	finished = pyqtSignal()
	stim_now = pyqtSignal()

	# UI update signals
	force_stopped = pyqtSignal()
	exp_started = pyqtSignal()
	frame_number = pyqtSignal(int)

	# Keep track of total frames
	curent_frame = 0
	started = False

	def __init__(self, noff, nimtr, ntr, exp_stopped, frame_sim):
		QObject.__init__(self)
		self.noff = noff
		self.nimtr = nimtr
		self.ntr = ntr
		self.frame = frame_sim
		self.exp_stopped = exp_stopped

		# Compute frames we need to stimulate on
		self.stim_frames = []
		for i in range(1, self.ntr + 1):
			self.stim_frames.append(self.noff + self.nimtr * (i - 1) + 1)

	def run(self):

		while True:

			# Decision point if experiment started or not
			if not self.started:

				# Continually check for start signal (simulated frame)
				while True:
					if self.frame.is_set():
						time.sleep(0.2)
						self.exp_started.emit()
						self.curent_frame += 1
						self.started = True
						self.frame_number.emit(self.curent_frame)
						break

					if self.exp_stopped.is_set():
						self.force_stopped.emit()
						return

			else:
				# Continually check for start signal (simulated frame)
				while True:
					if self.frame.is_set():
						self.curent_frame += 1
						self.frame_number.emit(self.curent_frame)

						# Check if stimulation is needed
						if self.curent_frame in self.stim_frames:
							self.stim_now.emit()

						time.sleep(0.2)

					if self.exp_stopped.is_set():
						self.force_stopped.emit()
						return

					if self.curent_frame == self.noff + (self.nimtr * self.ntr):
						self.finished.emit()
						return

'''
Class to control the LED firing
'''
class LEDControl(QObject):

	led_pins = ['Blue', 'Green', 'Red', 'Flourescense']

	current_led = 0

	def __init__(self, num_led, use_led_arr, led_period_arr, exp_stopped):
		QObject.__init__(self)
		self.exp_stopped = exp_stopped
		self.num_led = num_led

		self.led_arr = []
		self.led_period_arr = []
		for i in range(len(use_led_arr)):
			if use_led_arr[i]:
				self.led_arr.append(i)
				self.led_period_arr.append(led_period_arr[i])



	def run(self, frame_num):
		# Turn on the next LED in line
		if frame_num == 1:
			print(self.led_pins[self.current_led], ' at 0')

		else:
			print(self.led_pins[self.current_led], ' at ', self.led_period_arr[self.current_led])
			time.sleep(self.led_period_arr[self.current_led]/1000000)

		# Update the next LED
		self.current_led += 1
		if self.current_led == self.num_led:
			self.current_led = 0


