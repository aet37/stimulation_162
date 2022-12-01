import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import RPi.GPIO as GPIO
import sys
from threading import Event
from stimFunctions import *

# Define Events to be used throughout UI
global exp_stopped
exp_stopped = Event()
exp_stopped.clear()

# For simulation
global frame_sim
frame_sim = Event()
frame_sim.clear()

class ImagingSystem(QtWidgets.QMainWindow):

	# UI Class initializer / LOAD THE UI
	def __init__(self):
		super(ImagingSystem, self).__init__()
		uic.loadUi('StimControl.ui', self)
		self.move(0, 0)


		self.setWindowTitle("Stimulation Control")

		###########################################################################################
		## Buttons / Screen Items
		###########################################################################################

		# Line Edits
		self.noffBox = self.findChild(QtWidgets.QLineEdit, 'noffBox')
		self.nimtrBox = self.findChild(QtWidgets.QLineEdit, 'nimtrBox')
		self.ntrBox = self.findChild(QtWidgets.QLineEdit, 'ntrBox')
		self.fpsBox = self.findChild(QtWidgets.QLineEdit, 'fpsBox')
		self.toffbox = self.findChild(QtWidgets.QLineEdit, 'toffbox')
		self.ntbox = self.findChild(QtWidgets.QLineEdit, 'ntbox')
		self.ntrBoxT = self.findChild(QtWidgets.QLineEdit, 'ntrbox_t')
		self.durationBox = self.findChild(QtWidgets.QLineEdit, 'durationBox')
		self.freqBox = self.findChild(QtWidgets.QLineEdit, 'freqBox')
		self.pwBox = self.findChild(QtWidgets.QLineEdit, 'pwBox')
		self.LED1OTVal = self.findChild(QtWidgets.QLineEdit, 'LED1OTVal')
		self.LED2OTVal = self.findChild(QtWidgets.QLineEdit, 'LED2OTVal')
		self.LED3OTVal = self.findChild(QtWidgets.QLineEdit, 'LED3OTVal')
		self.LEDFOTVal = self.findChild(QtWidgets.QLineEdit, 'LEDFOTVal')

		# Check Boxes
		self.UseImgCheck = self.findChild(QtWidgets.QCheckBox, 'UseImg')
		self.UseImgCheck.clicked.connect(self.img_selection_toggle)
		self.useLEDCheck = self.findChild(QtWidgets.QCheckBox, 'useLED')
		self.useLEDCheck.clicked.connect(self.led_selection_toggle)
		self.blinkOnShowLive = self.findChild(QtWidgets.QCheckBox, 'blinkOnShowLive')
		self.blinkOnShowLive.clicked.connect(self.blink_live_toggle)
		self.waitTrig = self.findChild(QtWidgets.QCheckBox, 'waitTrig')

		self.LED1Check = self.findChild(QtWidgets.QCheckBox, 'LED1Check')
		self.LED1Check.clicked.connect(self.set_ontime_1)
		self.LED2Check = self.findChild(QtWidgets.QCheckBox, 'LED2Check')
		self.LED2Check.clicked.connect(self.set_ontime_2)
		self.LED3Check = self.findChild(QtWidgets.QCheckBox, 'LED3Check')
		self.LED3Check.clicked.connect(self.set_ontime_3)
		self.flourCheck = self.findChild(QtWidgets.QCheckBox, 'flourCheck')
		self.flourCheck.clicked.connect(self.set_ontime_f)

		# Radio Buttons
		self.master8RadioButton = self.findChild(QtWidgets.QRadioButton, 'master8RadioButton')
		self.laserRadioButton = self.findChild(QtWidgets.QRadioButton, 'laserRadioButton')
		self.master8RadioButton = self.findChild(QtWidgets.QRadioButton, 'NormChRadioB')

		# Labels
		self.nimsReport = self.findChild(QtWidgets.QLabel, 'nimsReport')
		self.recTimeReport = self.findChild(QtWidgets.QLabel, 'recTimeReport')
		self.stimTrNumMonitor = self.findChild(QtWidgets.QLabel, 'stimTrNumMonitor')
		self.StimONMonitor = self.findChild(QtWidgets.QLabel, 'StimONMonitor')
		self.ImgStatus = self.findChild(QtWidgets.QLabel, 'ImgStatus')
		self.inputErrorLabel = self.findChild(QtWidgets.QLabel, 'inputErrorLabel')
		self.LED1OTlabel = self.findChild(QtWidgets.QLabel, 'LED1OTlabel')
		self.LED2OTlabel = self.findChild(QtWidgets.QLabel, 'LED2OTlabel')
		self.LED3OTlabel = self.findChild(QtWidgets.QLabel, 'LED3OTlabel')
		self.LEDFOTlabel = self.findChild(QtWidgets.QLabel, 'LEDFOTlabel')
		self.LED1Monitor = self.findChild(QtWidgets.QLabel, 'LED1Monitor')
		self.LED2Monitor = self.findChild(QtWidgets.QLabel, 'LED2Monitor')
		self.LED3Monitor = self.findChild(QtWidgets.QLabel, 'LED3Monitor')
		self.FlourMonitor = self.findChild(QtWidgets.QLabel, 'FlourMonitor')
		self.LEDUseReport = self.findChild(QtWidgets.QLabel, 'LEDUseReport')

		# Push Buttons
		self.startButton = self.findChild(QtWidgets.QPushButton, 'startButton')
		self.startButton.clicked.connect(self.start_experiment)
		self.stopButton = self.findChild(QtWidgets.QPushButton, 'stopButton')
		self.stopButton.clicked.connect(self.stop_experiment)
		self.frameSimulate = self.findChild(QtWidgets.QPushButton, 'frameSimulate')

		# Progress Bar
		self.expProgress = self.findChild(QtWidgets.QProgressBar, 'expProgress')

		# Group Boxes
		self.ExpInputGroup = self.findChild(QtWidgets.QGroupBox, 'ExpInputGroup')
		self.ExpInfoGroup = self.findChild(QtWidgets.QGroupBox, 'ExpInfoGroup')
		self.ChSel = self.findChild(QtWidgets.QGroupBox, 'ChSel')
		self.ImgParam = self.findChild(QtWidgets.QGroupBox, 'ImgParam')
		self.LEDGroup = self.findChild(QtWidgets.QGroupBox, 'LEDGroup')
		self.LenGroup = self.findChild(QtWidgets.QGroupBox, 'LenParam')

		###########################################################################################
		## Class Variables
		###########################################################################################

		# Experiment Setup Variables
		self.doImg = True
		self.doLED = False
		self.actShowLive = False
		self.waitForTrig = False

		self.stimToINV = False
		self.stimToMaster8 = False

		self.noff = 0
		self.nimtr = 0
		self.ntr = 0
		self.fps = 0
		self.stim_dur = 0
		self.stim_freq = 0
		self.stim_pw = 0

		self.num_led = 0
		self.use_led1 = False
		self.use_led2 = False
		self.use_led3 = False
		self.use_ledf = False
		self.led1_period = 0
		self.led2_period = 0
		self.led3_period = 0
		self.ledf_period = 0

		self.curr_stim_tr = 0

		self.show()

	###############################################################################################
	## Helper Functions to update UI during runtime
	###############################################################################################

	# Show 'StimON' update in experiment monitor in UI
	def update_stim_on(self):
		self.StimONMonitor.setText('Stim ON')
		self.StimONMonitor.setStyleSheet('Color: red;Font-Size: 20pt;')

	# Clear 'StimON' update in experiment monitor in UI
	def update_stim_off(self):
		self.StimONMonitor.setText('')

	# Show trial counter updat ein experiment monitor in UI
	def update_tr_num(self, tr_num):
		self.curr_stim_tr = tr_num
		self.stimTrNumMonitor.setText(str(self.curr_stim_tr) + ' / ' + str(self.ntr))

		# If not an imaging trial, update the progress bar as well (since we cannot count frames)
		if not self.doImg:
			if self.curr_stim_tr == 1:
				self.expProgress.setValue(int(((self.curr_stim_tr - 0.5) / self.ntr) * 100))
			else:
				self.expProgress.setValue(int(((self.curr_stim_tr - 1) / self.ntr) * 100))

	# Show progress bar update if doing imaging
	def update_prog_bar(self, frame_num):
		total_frames = self.noff + (self.nimtr * self.ntr)
		self.expProgress.setValue(int((frame_num / total_frames) * 100))

	def update_started(self):
		# Edit UI start
		self.ImgStatus.setText('Experiment Started.')
		self.ImgStatus.setStyleSheet('Color: green;Font-Size:20pt;')

	###############################################################################################
	## Helper Functions to start stimulus
	###############################################################################################

	'''
	Function to start the stimulus and create the 2 threads when not waiting for camera triggers
	'''
	def start_stim_notrig(self):

		# Define Thread Objects
		self.stim_thread = QThread()

		# Define worker classes
		self.stim_worker = stimControlNoWait(self.noff, self.nimtr, self.ntr, self.stim_dur, self.stim_freq, self.stim_pw, self.stimToMaster8, self.stimToINV, self.waitForTrig, exp_stopped, frame_sim)

		# Move tasks to their threads
		self.stim_worker.moveToThread(self.stim_thread)

		# Connect signals
		self.stim_thread.started.connect(self.stim_worker.run)

		self.stim_worker.stim_on.connect(self.update_stim_on)
		self.stim_worker.stim_off.connect(self.update_stim_off)
		self.stim_worker.trial_number.connect(self.update_tr_num)
		self.stim_worker.exp_started.connect(self.update_started)

		self.stim_worker.finished.connect(self.stim_thread.quit)
		self.stim_worker.finished.connect(self.exp_finished)
		self.stim_worker.force_stopped.connect(self.stim_thread.quit)

		self.stim_worker.finished.connect(self.stim_worker.deleteLater)
		self.stim_thread.finished.connect(self.stim_thread.deleteLater)

		# Start the Threads
		self.stim_thread.start()

	'''
	Function to start the stimulus and create the 2 threads when waiting for camera triggers
	'''
	def start_stim(self):
		# Define Thread Objects
		self.stim_thread = QThread()
		self.img_thread = QThread()
		if self.doLED:
			self.led_thread = QThread()

		# Define worker classes
		self.stim_worker = stimControl(self.stim_dur, self.stim_freq, self.stim_pw, self.stimToMaster8, self.stimToINV, exp_stopped)
		self.img_worker = frameCount(self.noff, self.nimtr, self.ntr, exp_stopped, frame_sim)
		if self.doLED:
			self.led_worker = LEDControl(self.num_led, [self.use_led1, self.use_led2, self.use_led3, self.use_ledf], [self.led1_period, self.led2_period, self.led3_period, self.ledf_period], exp_stopped)

		# Move tasks to their threads
		self.stim_worker.moveToThread(self.stim_thread)
		self.img_worker.moveToThread(self.img_thread)
		if self.doLED:
			self.led_worker.moveToThread(self.led_thread)

		# Connect signals
		self.img_thread.started.connect(self.img_worker.run)

		# Functionality signals
		self.img_worker.stim_now.connect(self.stim_worker.run)
		if self.doLED:
			self.img_worker.frame_number.connect(self.led_worker.run)

		#UI Update signals
		self.img_worker.exp_started.connect(self.update_started)
		self.stim_worker.stim_on.connect(self.update_stim_on)
		self.stim_worker.stim_off.connect(self.update_stim_off)
		self.stim_worker.trial_number.connect(self.update_tr_num)
		self.img_worker.frame_number.connect(self.update_prog_bar)

		# Quitting Signals
		self.img_worker.finished.connect(self.stim_thread.quit)
		self.img_worker.force_stopped.connect(self.stim_thread.quit)
		self.img_worker.finished.connect(self.stim_worker.deleteLater)
		self.img_worker.finished.connect(self.stim_thread.deleteLater)

		self.img_worker.finished.connect(self.img_thread.quit)
		self.img_worker.finished.connect(self.exp_finished)
		self.img_worker.force_stopped.connect(self.img_thread.quit)
		self.img_worker.finished.connect(self.img_worker.deleteLater)
		self.img_worker.finished.connect(self.img_thread.deleteLater)

		if self.doLED:
			self.img_worker.finished.connect(self.led_thread.quit)
			self.img_worker.force_stopped.connect(self.led_thread.quit)
			self.img_worker.finished.connect(self.led_worker.deleteLater)
			self.img_worker.finished.connect(self.led_thread.deleteLater)

		# Start the Threads
		self.stim_thread.start()
		self.img_thread.start()
		if self.doLED:
			self.led_thread.start()

	###############################################################################################
	## Button Click Functions
	###############################################################################################

	# For Do Stimulation Checkbox
	def img_selection_toggle(self):
		if self.UseImgCheck.isChecked():
			self.doImg = True
			self.ImgParam.setEnabled(True)
			self.LenGroup.setEnabled(False)
		else:
			self.doImg = False
			self.ImgParam.setEnabled(False)
			self.LenGroup.setEnabled(True)

	# For Use LED Checkbox
	def led_selection_toggle(self):
		if self.useLEDCheck.isChecked():
			self.doLED = True
			self.LEDGroup.setEnabled(True)
			self.blinkOnShowLive.setEnabled(True)

			self.LED1OTlabel.setEnabled(False)
			self.LED1OTVal.setEnabled(False)
			self.LED2OTlabel.setEnabled(False)
			self.LED2OTVal.setEnabled(False)
			self.LED3OTlabel.setEnabled(False)
			self.LED3OTVal.setEnabled(False)
			self.LEDFOTlabel.setEnabled(False)
			self.LEDFOTVal.setEnabled(False)

		else:
			self.doLED = False
			self.LEDGroup.setEnabled(False)
			self.blinkOnShowLive.setEnabled(False)
			self.LED1Check.setChecked(False)
			self.LED2Check.setChecked(False)
			self.LED3Check.setChecked(False)
			self.flourCheck.setChecked(False)
			self.blinkOnShowLive.setChecked(False)

	# For Blink LED on Show Live Button
	def blink_live_toggle(self):
		if self.blinkOnShowLive.isChecked():
			self.actShowLive = True
		else:
			self.actShowLive = False

	# For LED 1 ON TIME settings
	def set_ontime_1(self):
		if self.LED1Check.isChecked():
			self.LED1OTlabel.setEnabled(True)
			self.LED1OTVal.setEnabled(True)
		else:
			self.LED1OTlabel.setEnabled(False)
			self.LED1OTVal.setEnabled(False)

	# For LED 2 ON TIME settings
	def set_ontime_2(self):
		if self.LED2Check.isChecked():
			self.LED2OTlabel.setEnabled(True)
			self.LED2OTVal.setEnabled(True)
		else:
			self.LED2OTlabel.setEnabled(False)
			self.LED2OTVal.setEnabled(False)

	# For LED 3 ON TIME settings
	def set_ontime_3(self):
		if self.LED3Check.isChecked():
			self.LED3OTlabel.setEnabled(True)
			self.LED3OTVal.setEnabled(True)
		else:
			self.LED3OTlabel.setEnabled(False)
			self.LED3OTVal.setEnabled(False)

	# For LED F ON TIME settings
	def set_ontime_f(self):
		if self.flourCheck.isChecked():
			self.LEDFOTlabel.setEnabled(True)
			self.LEDFOTVal.setEnabled(True)
		else:
			self.LEDFOTlabel.setEnabled(False)
			self.LEDFOTVal.setEnabled(False)

	# For Start Experiment Button
	def start_experiment(self):

		# Clear errors
		self.inputErrorLabel.setText('')

		# Set progress bar to 0
		self.expProgress.setValue(0)

		# Unset the stopped flag
		exp_stopped.clear()

		# Determine whether to wait for trigger
		if self.UseImgCheck.isChecked():
			self.waitForTrig = True
		else:
			if self.waitTrig.isChecked():
				self.waitForTrig = True
			else:
				self.waitForTrig = False

		if self.doImg:
			# Check if no input
			if not bool(self.noffBox.text().strip()) or not bool(self.nimtrBox.text().strip()) or not bool(self.ntrBox.text().strip()) or not bool(self.fpsBox.text().strip()):
				self.inputErrorLabel.setText('Error: input all img params.')
				return

			# Check to make sure that imaging paramters are integers
			if self.noffBox.text().isnumeric():
				self.noff = int(self.noffBox.text())
			else:
				self.inputErrorLabel.setText('Error: noff must be int.')
				return

			if self.nimtrBox.text().isnumeric():
				self.nimtr = int(self.nimtrBox.text())
			else:
				self.inputErrorLabel.setText('Error: nimtr must be int.')
				return

			if self.ntrBox.text().isnumeric():
				self.ntr = int(self.ntrBox.text())
			else:
				self.inputErrorLabel.setText('Error: ntr must be int.')
				return

			if self.fpsBox.text().isnumeric():
				self.fps = int(self.fpsBox.text())
			else:
				self.inputErrorLabel.setText('Error: fps must be int.')
				return
		else:
			if self.toffbox.text().isnumeric():
				self.noff = int(self.toffbox.text())
			else:
				self.inputErrorLabel.setText('Error: Time Off must be int.')
				return

			if self.ntbox.text().isnumeric():
				self.nimtr = int(self.ntbox.text())
			else:
				self.inputErrorLabel.setText('Error: Trial Time must be int.')
				return

			if self.ntrBoxT.text().isnumeric():
				self.ntr = int(self.ntrBoxT.text())
			else:
				self.inputErrorLabel.setText('Error: Num Trials must be int.')
				return

		# Check to make sure Stimulation paramters are integers
		if self.durationBox.text().isnumeric():
			self.stim_dur = int(self.durationBox.text())
		else:
			self.inputErrorLabel.setText('Error: duration must be int.')
			return

		if self.freqBox.text().isnumeric():
			self.stim_freq = int(self.freqBox.text())
		else:
			self.inputErrorLabel.setText('Error: frequency must be int.')
			return

		if self.pwBox.text().isnumeric():
			self.stim_pw = int(self.pwBox.text())
		else:
			self.inputErrorLabel.setText('Error: pulse width must be int.')
			return

		self.stimToINV = self.laserRadioButton.isChecked()
		self.stimToMaster8 = self.master8RadioButton.isChecked()

		# Check to make sure LED inputs are correct
		if self.doLED:

			# Get the number of LEDs on
			self.num_led = 0

			if self.LED1Check.isChecked():
				self.num_led += 1
				self.use_led1 = True
			if self.LED2Check.isChecked():
				self.num_led += 1
				self.use_led2 = True
			if self.LED3Check.isChecked():
				self.num_led += 1
				self.use_led3 = True
			if self.flourCheck.isChecked():
				self.num_led += 1
				self.use_ledf = True

			# If no LEDs are checked, dont start
			if self.num_led < 1:
				self.inputErrorLabel.setText('Error: No LEDs selected.')
				return

			# Check the LED OnTime
			if self.LED1Check.isChecked():
				if self.LED1OTVal.text().isnumeric():
					self.led1_period = int(self.LED1OTVal.text())
				else:
					self.inputErrorLabel.setText('Error: LED1 on time must be int.')
					return
			if self.LED2Check.isChecked():
				if self.LED2OTVal.text().isnumeric():
					self.led2_period = int(self.LED2OTVal.text())
				else:
					self.inputErrorLabel.setText('Error: LED2 on time must be int.')
					return
			if self.LED3Check.isChecked():
				if self.LED3OTVal.text().isnumeric():
					self.led3_period = int(self.LED3OTVal.text())
				else:
					self.inputErrorLabel.setText('Error: LED3 on time must be int.')
					return
			if self.flourCheck.isChecked():
				if self.LEDFOTVal.text().isnumeric():
					self.ledf_period = int(self.LEDFOTVal.text())
				else:
					self.inputErrorLabel.setText('Error: Flour. on time must be int.')
					return

		# Disable Further changes to editing
		self.ExpInputGroup.setEnabled(False)

		# Enable information window
		self.ExpInfoGroup.setEnabled(True)

		# Update features about window
		if self.doImg:
			self.nimsReport.setText(str(self.noff + (self.nimtr * self.ntr)))
			self.LEDUseReport.setText(str(self.num_led))
		else:
			self.nimsReport.setText('--')
			self.LEDUseReport.setText('None')

		if self.doImg:
			self.recTimeReport.setText(str(round(((self.noff + (self.nimtr * self.ntr)) * (1/self.fps)) / 60, 2)))
		else:
			self.recTimeReport.setText(str(round((self.noff + (self.nimtr * self.ntr)) / 60, 2)))

		self.stimTrNumMonitor.setText(str(self.curr_stim_tr) + ' / ' + str(self.ntr))

		# Set proper LEDs to correct status
		self.LED1Monitor.setEnabled(self.use_led1)
		if self.use_led1:
			self.LED1Monitor.setStyleSheet('Color: blue;')
		else:
			self.LED1Monitor.setStyleSheet('Color: black;')
		self.LED2Monitor.setEnabled(self.use_led2)
		if self.use_led2:
			self.LED2Monitor.setStyleSheet('Color: green;')
		else:
			self.LED2Monitor.setStyleSheet('Color: black;')
		self.LED3Monitor.setEnabled(self.use_led3)
		if self.use_led3:
			self.LED3Monitor.setStyleSheet('Color: red;')
		else:
			self.LED3Monitor.setStyleSheet('Color: black;')
		self.FlourMonitor.setEnabled(self.use_ledf)
		if self.use_ledf:
			self.FlourMonitor.setStyleSheet('Color: yellow;')
		else:
			self.FlourMonitor.setStyleSheet('Color: black;')

		# Disable Start Button
		self.startButton.setEnabled(False)

		# Enable Stop Button
		self.stopButton.setEnabled(True)

		if self.waitForTrig:
			self.ImgStatus.setText('Waiting For Trigger ...')
			self.ImgStatus.setStyleSheet('Color: yellow;Font-Size:20pt;')

		else:
			self.ImgStatus.setText('Experiment Started.')
			self.ImgStatus.setStyleSheet('Color: green;Font-Size:20pt;')

		if self.doImg:
			# Call funciton to start trigger experiments
			self.start_stim()
		else:
			# Call function to start non-trig experiments
			self.start_stim_notrig()

	# For Stop Experiment Button
	def stop_experiment(self):

		# Set the stop flag
		exp_stopped.set()

		# Set Pins to all off
		initialize_gpio()

		# Reset Experimental Variables
		self.noff = 0
		self.nimtr = 0
		self.ntr = 0
		self.fps = 0
		self.stim_dur = 0
		self.stim_freq = 0
		self.stim_pw = 0

		self.num_led = 0
		self.use_led1 = False
		self.use_led2 = False
		self.use_led3 = False
		self.use_ledf = False
		self.led1_period = 0
		self.led2_period = 0
		self.led3_period = 0
		self.ledf_period = 0

		self.curr_stim_tr = 0

		# Update experiment info that trial was stopped
		self.ImgStatus.setText('Experiment Stopped')
		self.ImgStatus.setStyleSheet('Color: red;Font-Size:20pt;')
		self.StimONMonitor.setText('')

		self.LED1Monitor.setEnabled(False)
		self.LED2Monitor.setEnabled(False)
		self.LED3Monitor.setEnabled(False)
		self.FlourMonitor.setEnabled(False)

		# Allow Editing
		self.ExpInputGroup.setEnabled(True)
		self.startButton.setEnabled(True)

		# Disable information window
		self.ExpInfoGroup.setEnabled(False)
		self.stopButton.setEnabled(False)

	def exp_finished(self):

		# Set the stop flag
		exp_stopped.set()

		# Set progress bar to 100
		self.expProgress.setValue(100)

		# Set Pins to all off
		initialize_gpio()

		# Reset Experimental Variables
		self.noff = 0
		self.nimtr = 0
		self.ntr = 0
		self.fps = 0
		self.stim_dur = 0
		self.stim_freq = 0
		self.stim_pw = 0

		self.num_led = 0
		self.use_led1 = False
		self.use_led2 = False
		self.use_led3 = False
		self.use_ledf = False
		self.led1_period = 0
		self.led2_period = 0
		self.led3_period = 0
		self.ledf_period = 0

		self.curr_stim_tr = 0

		# Update experiment info that trial was stopped
		self.ImgStatus.setText('Experiment Finished.')
		self.ImgStatus.setStyleSheet('Color: black;Font-Size:20pt;')
		self.StimONMonitor.setText('')

		self.LED1Monitor.setEnabled(False)
		self.LED2Monitor.setEnabled(False)
		self.LED3Monitor.setEnabled(False)
		self.FlourMonitor.setEnabled(False)

		# Allow Editing
		self.ExpInputGroup.setEnabled(True)
		self.startButton.setEnabled(True)

		# Disable information window
		self.ExpInfoGroup.setEnabled(False)
		self.stopButton.setEnabled(False)

# Set up GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Set up trigger input GPIO
GPIO.setup(TRIGGER_IN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # internal pull down

# Set up output Stimulation pins
GPIO.setup(TRIGGER_INV_PIN, GPIO.OUT)
GPIO.setup(TRIGGER_NORM_PIN, GPIO.OUT)
GPIO.setup(TRIGGER_M8_PIN, GPIO.OUT)

# Set up output LED pins
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)
GPIO.setup(LED3_PIN, GPIO.OUT)
GPIO.setup(FLOUR_PIN, GPIO.OUT)

# Initialize Pins to all off
initialize_gpio()

# UI Setup
app = QtWidgets.QApplication(sys.argv)

# Start UI
window = ImagingSystem()
os.system('clear')
app.exec_()

# To do before system Exit
os.system('clear')
