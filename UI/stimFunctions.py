from PyQt5.QtCore import QObject, QThread, pyqtSignal
from threading import Event
import time
import os
import RPi.GPIO as GPIO

'''
	@File: stimFunctions.py
	@Date: 26 Nov 2022
	@Author: NeuroImaging Lab, Andrew Toader

	@Purpose: support functions for the ImagingSystem GIU to control stimulation, and synchronize with imaging system

'''

# Define the Trigger pin
global TRIGGER_IN_PIN
TRIGGER_IN_PIN = 11

# Define the output pins
global TRIGGER_INV_PIN, TRIGGER_NORM_PIN, TRIGGER_M8_PIN
TRIGGER_INV_PIN = 13	# For Laser
TRIGGER_NORM_PIN = 15	# For Normal
TRIGGER_M8_PIN = 19	# For Normal

# Define the LED pins
global LED1_PIN, LED2_PIN, LED3_PIN, FLOUR_PIN
LED1_PIN = 21
LED2_PIN = 23
LED3_PIN = 29
FLOUR_PIN = 31

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

		# Check for wait
		if self.do_wait:
			while True:

				GPIO.wait_for_edge(TRIGGER_IN_PIN, GPIO.RISING, timeout=25)

				if self.ctrl.is_set():
					self.force_stopped.emit()
					return

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

			if self.toM8:

				# Send UI stimulation signal
				self.stim_on.emit()

				# Send Master 8 the stimulus
				GPIO.output(TRIGGER_M8_PIN, 1)
				time.sleep(0.2)
				GPIO.output(TRIGGER_M8_PIN, 0)
				time.sleep(0.8)

				# Check if stop button has been pressed in UI
				if self.ctrl.is_set():
					self.force_stopped.emit()
					return

				# Sleep for the remainder of the trial time (while checking for done signal)
				for a in range(self.ttr):

					# Send UI stimulation off signal at proper time
					if a + 1 == self.dur:
						self.stim_off.emit()

					# Sleep
					time.sleep(1)

					# Check if stop button has been pressed in UI
					if self.ctrl.is_set():
						self.force_stopped.emit()
						return

			else:
				# Send UI stimulation signal
				self.stim_on.emit()

				# DC Case 1
				if self.freq == 0:
					GPIO.output(TRIGGER_INV_PIN, 1)

					# Sleep for the remainder of the stimulation time (while checking for done signal)
					for a in range(self.dur):
						time.sleep(1)
						if self.ctrl.is_set():
							self.force_stopped.emit()
							return

					GPIO.output(TRIGGER_INV_PIN, 0)

					# Send UI stimulation off signal
					self.stim_off.emit()

				# DC Case 2
				elif 1/self.freq == self.pw/1000:
					GPIO.output(TRIGGER_INV_PIN, 1)

					# Sleep for the remainder of the stimulation time (while checking for done signal)
					for a in range(self.dur):
						time.sleep(1)
						if self.ctrl.is_set():
							self.force_stopped.emit()
							return

					GPIO.output(TRIGGER_INV_PIN, 0)

					# Send UI stimulation off signal
					self.stim_off.emit()

				else:
					for j in range(self.dur):
						for k in range(self.freq):
							GPIO.output(TRIGGER_INV_PIN, 1)
							time.sleep(pulse_width/1000)
							GPIO.output(TRIGGER_INV_PIN, 0)
							time.sleep((1/frequency) - (pulse_width/1000))

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

	def run(self):

		self.tr_num += 1
		self.trial_number.emit(self.tr_num)

		if self.toM8:

			# Send UI stimulation signal
			self.stim_on.emit()

			# Send Master 8 the stimulus
			GPIO.output(TRIGGER_M8_PIN, 1)
			time.sleep(0.25)
			GPIO.output(TRIGGER_M8_PIN, 0)
			time.sleep(0.75)

			if self.exp_stopped.is_set():
				return

			for i in range(self.dur - 1):
				time.sleep(1)
				if self.exp_stopped.is_set():
					return

			self.stim_off.emit()

		else:
			# Send UI stimulation signal
			self.stim_on.emit()

			# DC Case 1
			if self.freq == 0:
				GPIO.output(TRIGGER_INV_PIN, 1)

				# Sleep for the remainder of the stimulation time (while checking for done signal)
				for i in range(self.dur):
					time.sleep(1)
					if self.ctrl.is_set():
						self.force_stopped.emit()
						return

				GPIO.output(TRIGGER_INV_PIN, 0)

				# Send UI stimulation off signal
				self.stim_off.emit()

			# DC Case 2
			elif 1/self.freq == self.pw/1000:
				GPIO.output(TRIGGER_INV_PIN, 1)

				# Sleep for the remainder of the stimulation time (while checking for done signal)
				for i in range(self.dur):
					time.sleep(1)
					if self.ctrl.is_set():
						self.force_stopped.emit()
						return

				GPIO.output(TRIGGER_INV_PIN, 0)

				# Send UI stimulation off signal
				self.stim_off.emit()

			else:
				for j in range(self.dur):
					for k in range(self.freq):
						GPIO.output(TRIGGER_INV_PIN, 1)
						time.sleep(pulse_width/1000)
						GPIO.output(TRIGGER_INV_PIN, 0)
						time.sleep((1/frequency) - (pulse_width/1000))

						# Check if trial was stopped
						if self.ctrl.is_set():
							self.force_stopped.emit()
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

					edge = GPIO.wait_for_edge(TRIGGER_IN_PIN, GPIO.RISING, timeout=25)

					if edge is not None:
						self.exp_started.emit()
						self.curent_frame += 1
						self.started = True
						self.frame_number.emit(self.curent_frame)
						break

					# Check if stop experiment button has been pressed
					if self.exp_stopped.is_set():
						self.force_stopped.emit()
						return

			else:
				# Continually check for start signal (simulated frame)
				while True:

					# Wait for next frame
					edge = GPIO.wait_for_edge(TRIGGER_IN_PIN, GPIO.RISING, timeout=25)

					if edge is not None:

						# If frame, increment the frame count
						self.curent_frame += 1
						self.frame_number.emit(self.curent_frame)

						# Check if stimulation is needed
						if self.curent_frame in self.stim_frames:
							self.stim_now.emit()

					# Check if stop experiment button has been pressed
					if self.exp_stopped.is_set():
						self.force_stopped.emit()
						return

					# Check if this is the last frame
					if self.curent_frame == self.noff + (self.nimtr * self.ntr):
						self.finished.emit()
						return

'''
Class to control the LED firing
'''
class LEDControl(QObject):

	led_pins = [LED1_PIN, LED2_PIN, LED3_PIN, FLOUR_PIN]

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
		if frame_num != 1:

			# Turn on correct LED for period specified
			GPIO.output(self.led_pins[self.led_arr[self.current_led]], 1)
			time.sleep(self.led_period_arr[self.current_led]/1000000)
			GPIO.output(self.led_pins[self.led_arr[self.current_led]], 0)

		# Update the next LED
		self.current_led += 1
		if self.current_led == self.num_led:
			self.current_led = 0
