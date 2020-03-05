import Globals
from PlotWidget import SniffPlot
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout,\
QScrollBar, QLabel, QButtonGroup,\
QRadioButton, QPushButton, QDoubleSpinBox,\
QFileDialog
from PyQt5 import QtCore, QtGui
from qrangeslider import QRangeSlider
from datetime import datetime
from collections import defaultdict

from PayloadData import PayloadData, payloadHead

import os
from TraceDocks import TraceDocks

## @package PlotTab
# PlotTab plots the opened measurement while providing added information
# like the entire measurement time and detailed tooltips.
# The plot can be exported to a .png file after reviewing the measurement.

class PlotTab(TraceDocks):
	## The constructor
	# @param parent parent for this widget
	def __init__(self,parent):
		super(PlotTab, self).__init__(parent,'Plot Tab')
		self.tabName = 'PlotTab'
		self.parent = parent
		self.logger.logEvent('Creating Tab now: '+ self.tabName)
		Globals.dockDict['dockStart'].createPlotButt.clicked.connect(self.createPlot)
		# Create necessary variables
		self.snifferConfig.configFilterState = 'Local'
		self.snifferConfig.configCurrentTheme = 'Dark'
		self.snifferConfig.parseConfigFromFile()
		
		self.writePayload = PayloadData()
		self.snifferPayload = PayloadData()
		self.singleShotTime = 0
		self.end_time = 0
		self.start_time = 0
		#self.snifferConfigData = self.parent.snifferConfigData
		#self.failCnt = self.parent.failCnt
		self.purge = 0
		#self.measurementIsRunning = self.parent.measurementIsRunning
	
	## Create Layout for this Tab
	def setPlotTabLayout(self):    
		# Create Plot Tab --------------------###    
		# Create Layouts
		self.VLayout = QVBoxLayout()
		self.H1layout = QHBoxLayout()
		self.H1layout.setSpacing(15)
		self.H11layout = QHBoxLayout()
		self.H2layout = QHBoxLayout()
		self.V11layout = QVBoxLayout()
		self.V12layout = QVBoxLayout()
		
		self.V21layout = QVBoxLayout()
		self.V23layout = QVBoxLayout()
		self.V22layout = QVBoxLayout()
		#------------------------------------
		 
		# Create Widgets for H1layout         
		# Create Browser
		self.plotter = SniffPlot(self.snifferConfig)
		self.rangeslider = QRangeSlider(self)
		
		self.filterGroup = QButtonGroup()
		self.localFilterRadio = QRadioButton('Local',self)
		self.globalFilterRadio = QRadioButton('Global', self)
		self.configureFilterButt = QPushButton('Configure Filter')
		self.createPlotButt = QPushButton('Create Plot')
		self.exportPlotButt = QPushButton('Export Plot')
		
		# We need to sync the UI before connecting any slots in order to prevent accidental stateChanges.
		self.syncUiToConfig() 
		
		self.configureFilterButt.clicked.connect(self.configureFilter)
		self.createPlotButt.clicked.connect(self.createPlot)
		self.exportPlotButt.clicked.connect(self.exportPlot)
		self.localFilterRadio.clicked.connect(self.localRadioSelected)
		self.globalFilterRadio.clicked.connect(self.globalRadioSelected)
		
		self.H11layout.addWidget(self.localFilterRadio)
		self.H11layout.addWidget(self.globalFilterRadio)
		self.H11layout.addWidget(self.createPlotButt)
		self.H11layout.addWidget(self.exportPlotButt)
		self.V12layout.addLayout(self.H11layout)
		self.V12layout.addWidget(self.configureFilterButt)
		
		self.H1layout.addLayout(self.V11layout)
		self.H1layout.addStretch()
		self.H1layout.addLayout(self.V12layout)
		
		self.plotWindowStart=QDoubleSpinBox(self)
		self.plotWindowEnd=QDoubleSpinBox(self)
		
		self.plotWindowResetStart=QPushButton(self)
		self.plotWindowResetEnd=QPushButton(self)
		
		self.plotWindowResetStart.pressed.connect(self.plotter.resetStart)
		self.plotWindowResetEnd.pressed.connect(self.plotter.resetEnd)
		
		self.plotWindowResetStart.setText("R")
		self.plotWindowResetEnd.setText("R")
		
		self.plotWindowStart.setSuffix("ms")
		self.plotWindowEnd.setSuffix("ms")
		
		self.plotWindowStartLabel=QLabel(self)
		self.plotWindowDurationLabel=QLabel(self)
		self.plotWindowEndLabel=QLabel(self)
		
		self.applyRange=QPushButton(None)
		self.applyRange.setText("Apply Range")
		
		self.H2layout.addLayout(self.V21layout)
		self.H2layout.addWidget(self.plotWindowResetStart)
		self.H2layout.addStretch()
		self.H2layout.addLayout(self.V22layout)
		self.H2layout.addStretch()
		self.H2layout.addWidget(self.plotWindowResetEnd)
		self.H2layout.addLayout(self.V23layout)
		
		
		self.V21layout.addWidget(self.plotWindowStart)
		self.V21layout.addWidget(self.plotWindowStartLabel)
		
		self.V22layout.addWidget(self.applyRange)
		self.V22layout.addWidget(self.plotWindowDurationLabel)
		
		self.V23layout.addWidget(self.plotWindowEnd)
		self.V23layout.addWidget(self.plotWindowEndLabel)
		
		#------------------------------------
		
		self.VLayout.addLayout(self.H1layout)
		
		self.VLayout.addWidget(self.plotter)
		self.VLayout.addWidget(self.rangeslider)
		self.VLayout.addLayout(self.H2layout)
		
		self.applyRange.pressed.connect(self.plotter.applyRange)
		
		self.plotter.setScrollbar(self.rangeslider)
		self.plotter.setWindowSpinner(self.plotWindowStart,self.plotWindowEnd)
		self.plotter.setRangeLabels(self.plotWindowStartLabel,self.plotWindowEndLabel,self.plotWindowDurationLabel)
		self.dockContents.setLayout(self.VLayout)
	
	## Get Task name from Task-ID
	def getTaskName(self,taskid):
		return "Task-"+str(taskid)
	
	### Export plot to PNG image
	def exportPlot(self):
		# Create dummy SniffPlot with light Theme
		self.plotterExport = SniffPlot(self.snifferConfig)
		self.plotterExport.setStyleSheet("background-color: rgb(255, 255, 255);")
		self.plotterExport.setOverrideStyle("Light")
		self.plotterExport.endTime=self.plotter.endTime
		self.plotterExport.endTime_=self.plotter.endTime_
		self.plotterExport.startTime=self.plotter.startTime
		self.plotterExport.startTime_=self.plotter.startTime_
		self.plotterExport.data=self.plotter.data
		self.plotterExport.ntask=self.plotter.ntask
		self.plotterExport.plotStart=self.plotter.plotStart
		self.plotterExport.plotEnd=self.plotter.plotEnd
		self.plotterExport.taskcols=self.plotter.taskcols
		self.plotterExport.resize(1050,750)
		
		# Create image to fit Plot
		pixmap=QtGui.QPixmap(self.plotterExport.size());
		# Render Widget to QPixMap and safe file
		self.plotterExport.render(pixmap)
		filename, ok = QFileDialog.getSaveFileName(self, 'Save Plot', 'Plot.png', 'PNG files (*.png)')
		if filename and ok:
			pixmap.save(filename);
		del self.plotterExport
		del pixmap
	
	## Generate actual plot
	def displayFunction(self,timerValueInMs_extern,payloadList):
		knownTasks={} #All known tasks which will be displayed in the plot
		readyTasks={} #Saves the ready-state of a task
		dataFrame=[]
		filteredPayloads = []
		eventWidth=1 #Width of an displayed Event in ms
		overflowCounter=0 #Counts how often the tickOverflowValue is surpassed
		tickOverflow = int(Globals.dockDict['dockConfig'].snifferConfig.configMaxTickCountVal) #value of tick-overflow in normal ticks
		timerValueInMs=1/timerValueInMs_extern
		previousElementTickCount=self.getTickCount(payloadList[0].payloadHead) #Reads the start Time
		previousElement=payloadList[0]
		print('I have Payloads len:' + str(len(payloadList)))
		
		print('I have filtered len:' + str(len(filteredPayloads)))
		
		self.task_state_changes=defaultdict(list)
		self.end_time=0
		self.start_time=None
		for element in payloadList: #for each element in the payload list
			if element.payloadHead.informationID is 148:
				continue

			if element.payloadHead.informationID is 149:
				continue

			if element.payloadHead.informationID is 150:
				continue

			if hasattr(element, 'payloadHead'):# and hasattr(element,"data1"):
				if previousElementTickCount-self.getTickCount(element.payloadHead)==int(Globals.dockDict['dockConfig'].snifferConfig.configMaxTickCountVal): #Checks for overflow
					overflowCounter = overflowCounter+1
				
				previousElementTickCount=self.getTickCount(element.payloadHead)
				previousElement=element #rememver previousElement
				
				if element.payloadHead.informationID is 44:
					continue
				
				#get Data from element
				infoid=Globals.tspDict[element.payloadHead.informationID][0]
				
				timestamp=self.getTickCount(element.payloadHead)+\
				overflowCounter*tickOverflow+\
				self.getTimerValue(element.payloadHead)*timerValueInMs
				
				#skip Ticks
				if infoid=='ID_TASK_INCREMENT_TICK':
					continue

				
				#Task state from InfoID
				state2str={
				'ID_TASK_SWITCHED_OUT': "waiting",
				'ID_MOVED_TASK_TO_READY_STATE': "ready",
				'ID_TASK_SWITCHED_IN': "running"
				}
				
				#update task state and timestamp
				
				if infoid in ['ID_TASK_SWITCHED_OUT',
				'ID_MOVED_TASK_TO_READY_STATE',
				'ID_TASK_SWITCHED_IN']:
					task_id=element.data1
					self.task_state_changes[task_id].append({"time":timestamp,"state":state2str[infoid]})
				else:
					self.task_state_changes[99999].append({"time":timestamp,"state":infoid})
				
				if timestamp>self.end_time:
					self.end_time=timestamp
				
				if self.start_time is None or timestamp<self.start_time:
					self.start_time=timestamp
		#save data and send to Plotter
		self.task_state_changes=dict(self.task_state_changes)
		self.plotter.update_data(self.task_state_changes,self.end_time,self.start_time)
	
	## Handler for "Create Plot" button
	def createPlot(self):
		if(len(Globals.payloadList) == 0):
			self.displayException('The PayloadList is empty. Run a measurement?')
			return
		self.displayFunction(timerValueInMs_extern = int(Globals.dockDict['dockConfig'].snifferConfig.configTickToMsLine),payloadList = Globals.payloadList)
		
	
	## Enable all buttons
	def disableButtons(self):
		self.saveMeasButt.setEnabled(False)
		self.openMeasButt.setEnabled(False)
		print('Disable TabStart Buttons')
	
	## Disable all buttons
	def enableButtons(self):
		self.saveMeasButt.setEnabled(True)
		self.openMeasButt.setEnabled(True)
		print('Enable TabStart Buttons')
	
	## Display status message
	def displayStatusMessage(self,myMessage):
		self.statusBox.setText('Message: ' + myMessage)    
	
	## Change waitForReset state
	def waitResetCheckChanged(self):
		self.snifferConfig.configWaitResetCheck ^= 1
		self.logger.logEvent('changed Wait for Reset Checkbox to - '+ str(self.snifferConfig.configWaitResetCheck))
	
	## Select local Filter
	def localRadioSelected(self):
		self.snifferConfig.configFilterState = 'Local'
		self.logger.logEvent('changed Filter Radio to - '+ str(self.snifferConfig.configFilterState))
	
	## Select global Filter
	def globalRadioSelected(self):
		self.snifferConfig.configFilterState = 'Global'
		self.logger.logEvent('changed Filter Radio to - '+ str(self.snifferConfig.configFilterState))
	
	## Get TickCount from Header
	def getTickCount(self,payloadHeader):
		return payloadHeader.tickCountHigh << 8 | payloadHeader.tickCountLow
	
	## Get TimerValue from Hader
	def getTimerValue(self,payloadHeader):
		return payloadHeader.timerByteHigh << 8 | payloadHeader.timerByteLow
			
	# --- MANDATORY UI FUNCTIONS --- #
	# -------------------------------# 
	
	## Read out all components of snifferConfig and set the UI elements according to
	#  the saved values.   		
	def syncUiToConfig(self):
		if self.snifferConfig.configFilterState == 'Local':
			self.localFilterRadio.click()
		elif self.snifferConfig.configFilterState == 'Global':
			self.globalFilterRadio.click()
		else:
			print('Error, neither local nor global in config')
			
	## Open the correct filter based on the radioButton. If the Global-filter is checked
	#  we assign its calledby variable in order to execute the right callback after the filter is saved. 
	def configureFilter(self):
		if self.localFilterRadio.isChecked():
			self.snifferFilter.show()
		elif self.globalFilterRadio.isChecked():
			print('stump implementation for global filter')
		else:
			print('neither radios checked. Error!')
			
	## CB: // Updates the UI-contents with after filtering has taken place.
	#  This function should not be called by the tab itself, but by the filter
	#  @param filteredIDs the IDs that are to be kept in the payloadList (obsolete)
	#  @param filteredPayloads the new payloadList, which only contains the payloads filtered by the SnifferFilter  			
	def filterUpdated(self, filteredIDs, filteredPayloads):
		print('we arrive from SnifferFilter')
		if(len(Globals.payloadList) == 0):
			self.displayException('The PayloadList is empty. Run a measurement?')
			return
		self.displayFunction(timerValueInMs_extern = int(Globals.dockDict['dockConfig'].snifferConfig.configTickToMsLine),payloadList = filteredPayloads)
	