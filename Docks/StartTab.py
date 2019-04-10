import Globals

#PyQt Imports
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QProgressBar, QLineEdit, QLabel, QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont

import serial
import time
from SnifferThreads import SnifferInterpretThread,SnifferQueueThread
from PayloadData import PayloadData

from TraceDocks import TraceDocks

## @package StartTab
# StartTab handles the start / stop of a measurement and is the base
# view presented to the user.

## The actual implementation of the StartTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on
class StartTab(TraceDocks):
    
    ## The constructor
    #  initialize the super-class, assign a name and first configItems
    def __init__(self,parent):
        super(StartTab, self).__init__(parent,'StartTab')
        self.tabName = 'StartTab'
        self.parent = parent
        self.logger.logEvent('Creating Tab now: '+ self.tabName)
        
        # Set a couple of default-values, in case the configParser does not work
        self.snifferConfig.configWaitResetCheck = 0
        self.snifferConfig.configCurrentTheme = 'Dark'
        
        # By parsing the config now, we assure that we re-load everything
        # the way we left it
        self.snifferConfig.parseConfigFromFile()
        
        self.singleShotTime = 0
        self.failCnt = self.parent.failCnt
        self.purge = 0
        self.measurementIsRunning = False
        
        
    ## Create the visible UI              
    def setStartTabLayout(self):
        
        # Create Start Tab --------------------###   
        # Create Layouts     
        self.Vlayout = QVBoxLayout()
        
        self.H1layout = QHBoxLayout()
        self.H1layout.setSpacing(15)
        self.H1layout.addSpacing(60)
        
        self.H2layout = QHBoxLayout()
        self.H2SubV1Layout = QVBoxLayout()
        self.H2SubH1Layout = QHBoxLayout()
        self.H2SubV2Layout = QVBoxLayout()
        self.H2layout.setSpacing(15)
        
        self.H3layout = QHBoxLayout()
        self.H3layout.setSpacing(15)
        #------------------------------------
        
        # Create Widgets for H1layout
        # First buttons
        self.startStopAnalyzingButt = QPushButton('START')
        self.startStopAnalyzingButt.clicked.connect(self.toggleAnalyzing)
        self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: forestgreen; border-radius:100px}'
                                                  'QPushButton:pressed {border: 2px solid; border-color: green; background-color: forestgreen; border-radius:100px}'
                                                  'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                                  'QPushButton:focus {border: 2px solid; border-color: green; border-radius:100px}'
                                                  )
        self.startStopFont = QFont()
        self.startStopFont.setPointSize(20)
        self.startStopAnalyzingButt.setFont(self.startStopFont)
        
        self.startStopAnalyzingButt.setFixedSize(200,200)
        # Add Widgets to H1layout
        self.H1layout.addWidget(self.startStopAnalyzingButt)
        
        # Spacing for H1layout
        self.H1layout.addSpacing(5)
        #------------------------------------
        
        # Create Widgets for H2layout
        self.statusLabel = QLabel('Status')
        self.statusBox = QLineEdit()
        self.statusBox.setText('Booted and Ready')
        self.statusBox.setReadOnly(True)
        self.saveMeasButt = QPushButton('Save Measurefile')
        self.saveMeasButt.clicked.connect(self.saveMeasurement)
        self.openMeasButt = QPushButton('Open Measurefile')
        self.openMeasButt.clicked.connect(self.openMeasurement)
        self.createPlotButt = QPushButton('Create Plot')
        #self.createPlotButt.clicked.connect(Globals.dockDict['dockPlot'].createPlot)
        #self.waitResetCheck = QCheckBox('Wait for uC Reset')
        #self.hardwareFilterButt = QPushButton('Filter Ticks')
        #self.hardwareFilterButt.clicked.connect(self.hardwareFilter)
        
        # We need to sync the UI before connecting any slots in order to prevent accidental stateChanges.
        self.syncUiToConfig() 
        
        #self.waitResetCheck.stateChanged.connect(self.waitResetCheckChanged)  

        # Add Widgets to H2layout        
        self.H2layout.addWidget(self.statusLabel)
        self.H2layout.addWidget(self.statusBox)
        self.H2layout.addSpacing(40)
        #self.H2layout.addWidget(self.waitResetCheck)
        #self.H2layout.addWidget(self.hardwareFilterButt)
        self.H2layout.addWidget(self.openMeasButt)
        self.H2layout.addWidget(self.saveMeasButt)
        self.H2layout.addWidget(self.createPlotButt)
        
        # Endspacing for H2layout
        self.H2layout.addSpacing(5)
        #------------------------------------
        
        # Create Widgets for H3layout
        self.progressShotBar = QProgressBar()
        
        # Add Widgets to H3layout
        self.H3layout.addWidget(self.progressShotBar)
        #------------------------------------       
        self.Vlayout.addSpacing(130)
        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addStretch()
        self.Vlayout.addLayout(self.H2layout)
        self.Vlayout.addLayout(self.H3layout)
        
        self.dockContents.setLayout(self.Vlayout)
    
    # --- CALLBACKS --- #
    ## CB: startStopAnalyzingButt // Starts or Stops the measurement, depending on the state     
    def toggleAnalyzing(self):
        print('Deciding wether to Start/Stop Analyzing')
        # If measurement is going on, clean up the UI and try to stop it
        if self.measurementIsRunning == True:
            self.enableButtons()
            self.displayStatusMessage('Measurement is stopping...')
            self.measurementIsRunning = False
            self.setStartStopButtonStyle()
            self.logger.logEvent('stop Analyzing clicked')     
            self.progressShotBar.setMaximum(100)
            self.progressShotBar.setMinimum(0)
            self.progressShotBar.setValue(0)
            self.parent.serialTimer.stop()
            try:
                self.interpretThread.killme = True
                self.queueThread.killme = True
                while(self.interpretThread.isReading == True and self.queueThread.isReading == True):
                    #print('Waiting for the Thread to be stopped.')
                    pass
                self.displayStatusMessage('Measurement stopped.')    
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                self.displayException('Probably a missing Handler')
        
        # If measurement is stopped, we set up the UI and try to start it                   
        elif self.measurementIsRunning == False:
            self.disableButtons()
            self.measurementIsRunning = True
            self.setStartStopButtonStyle()
            self.logger.logEvent('start Analyzing clicked - ' + Globals.dockDict['dockConfig'].snifferConfig.configMode)
            self.setLayout(self.Vlayout)
            if(Globals.dockDict['dockConfig'].snifferConfig.configMode == 'Continuous'):
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.singleShotTime = 0xFFFFFFFF #Should be enough.
                self.triggerOn = False
                self.displayStatusMessage('Measuring with Continuousmode')
                            
            if(Globals.dockDict['dockConfig'].snifferConfig.configMode == 'Singleshot'):
                try:
                    self.singleShotTime = int(Globals.dockDict['dockConfig'].snifferConfig.configSingleDurLine)
                except ValueError:
                    QMessageBox.about(self,'ERROR','No integer entered, defaulting to 50')
                    self.singleShotTime = 50
                #self.progressShotBar.setMaximum(self.'dockConfig'.singleShotTime)
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.progressValue = 0
                self.triggerOn = False
                self.displayStatusMessage('Measuring with Singleshotmode, wait for '+str(self.singleShotTime)+'ms.')
                    
            if(Globals.dockDict['dockConfig'].snifferConfig.configMode == 'Trigger'):
                try:
                    self.singleShotTime = int(Globals.dockDict['dockConfig'].inputSingleDurBox.text())
                except ValueError:
                    QMessageBox.about(self,'ERROR','No integer entered, defaulting to 50')
                    self.singleShotTime = 50
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.triggerOn = True
                self.displayStatusMessage('Measuring with Triggermode')
            # Create a serialHandle with the parameters from ConfigDock and try to open it
            try:
                self.serialHandle = serial.Serial()
                self.serialHandle.port =  Globals.dockDict['dockConfig'].snifferConfig.configCom
                self.serialHandle.baudrate = int(Globals.dockDict['dockConfig'].snifferConfig.configBaud)
                self.serialHandle.timeout=3
                self.serialHandle.setDTR(False)
                self.serialHandle.open()
                time.sleep(0.1) # Wait for the open process to complete, then flush the buffer
                self.serialHandle.reset_input_buffer()
                self.serialHandle.reset_output_buffer()
                print(self.serialHandle.in_waiting)
                while self.serialHandle.in_waiting > 0:
                    self.serialHandle.reset_input_buffer()
                time.sleep(0.1) # A second sleep, just for safety
            
            # If anything goes wrong, clean up the UI    
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                self.displayException('Exception when opening SerialPort. Check Port?')
                self.enableButtons()
                self.displayStatusMessage('Stopping due to Exception!')
                self.measurementIsRunning = False
                self.setStartStopButtonStyle()   
                self.progressShotBar.setMaximum(100)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.parent.serialTimer.stop()
                return
            try:
                self.interpretThread = SnifferInterpretThread(singleshotTime = self.singleShotTime,
                                                               timeByteCount = Globals.dockDict['dockConfig'].snifferConfig.configTimeBytes,
                                                               triggerOn = self.triggerOn,
                                                               selectedTrigger = Globals.dockDict['dockConfig'].snifferConfig.configTrigger,
                                                               saveIncTime = Globals.dockDict['dockConfig'].snifferConfig.configIncTimeCheck)
                
                self.queueThread = SnifferQueueThread(serialHandle = self.serialHandle,
                                                        singleshotTime = self.singleShotTime,
                                                        timeByteCount = Globals.dockDict['dockConfig'].snifferConfig.configTimeBytes,
                                                        triggerOn = self.triggerOn,
                                                        selectedTrigger = Globals.dockDict['dockConfig'].snifferConfig.configTrigger,
                                                        saveIncTime = Globals.dockDict['dockConfig'].snifferConfig.configIncTimeCheck)
                
                self.interpretThread.startInterpretationSignal.connect(self.startInterpreter)
                # Threads are actually started here
                self.interpretThread.start()
                self.queueThread.start()
                
                self.failCnt = 0
                self.parent.serialTimer.start(5)
                
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                self.displayException('Exception when creating Thread.') 
                self.interpretThread.kill()
                self.queueThread.kill()  
                
    ## CB: startInterpretationSignal // gets called whenever a measurement is finished
    #  @details This function is user-defined. It currently fills the Table of TableDock and updates the filter.
    #  Updating the filter is mandatory!
    def startInterpreter(self):
        print('I completed my measurement, starting interpreter now...')
        self.queueThread.killme = True
        if(len(Globals.payloadList) > 0):
            Globals.dockDict['dockTable'].fillTable(Globals.payloadList)   
        if(Globals.objectDict):
            for docksNames, actualDocks in Globals.dockDict.items(): 
                actualDocks.snifferFilter.updateObjectFilter()
            Globals.globalFilter.updateObjectFilter()
        self.measurementIsRunning = False
        # Reset the UI
        self.setStartStopButtonStyle() 
        self.enableButtons()
        
    ## CB: saveMasurementButt // Saves the current measurement buffered in RAM to a .sniff file   
    def saveMeasurement(self):
        print('Trying to save Measurement')
        if(len(Globals.payloadList)== 0):
            self.displayException('payload List empty. Did you run a measurement?')
        else:
            self.displayStatusMessage('Measurements found, trying to save...')
            self.saveMeasDirectory, self.purge = QFileDialog.getSaveFileName(self, 'Save File', '', 'Sniff files (*.sniff)')
            print(self.saveMeasDirectory)
            try:
                self.snifferParser.saveToFile(self.saveMeasDirectory)
                self.displayStatusMessage('Done saving measurements, check your file/directory')
            except Exception as ex:
                self.displayStatusMessage('Something went wrong when selecting a file. Did you select a .sniff?')
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message) 
                
    ## CB: openMeasurementButt // Opens a .sniff measurement file and fills/replaces the measurement buffered in RAM
    #  with the filecontents. 
    def openMeasurement(self):
        print('Trying to open Measurement')
        self.displayStatusMessage('Measurements found, trying to save...')
        self.openMeasDirectory, self.purge = QFileDialog.getOpenFileName(self, 'Save File', '', 'Sniff files (*.sniff)')
        print(self.openMeasDirectory)
        Globals.payloadList.clear()
        # TODO: replace fillTable with startInterpreter!
        try:
            self.snifferParser.getFromFile(self.openMeasDirectory)
            Globals.dockDict['dockTable'].fillTable(Globals.payloadList)
            self.displayStatusMessage('Done opening measurements, check your table')
        except Exception as ex:
            self.displayException('Something went wrong when selecting a file. Did you select a .sniff?/File might be corrupt')
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
        
    # --- HELPER FUNCTIONS --- #
    
    ## Checks whether a measurement is running and changes the Start/Stop button style accordingly       
    def setStartStopButtonStyle(self):#change the StartStopButton Stylesheets. We either need it to be start or stop, theme is provided by configCurrentTheme var
        if self.measurementIsRunning == False:#We are in Stop mode, so we change button to Start
            if self.snifferConfig.configCurrentTheme == 'Dark': #TODO: Improve the theming, this is just a hotfix so the Button looks 'ok' in both themes.
                self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: limegreen; border-radius:100px}'
                                  'QPushButton:pressed {border: 2px solid; border-color: green; background-color: forestgreen; border-radius:100px}'
                                  'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                  'QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: #31363b; border-radius:100px}'
                                  )
            else:
                self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: limegreen; border-radius:100px}'
                                  'QPushButton:pressed {border: 2px solid; border-color: green; background-color: forestgreen; border-radius:100px}'
                                  'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                  'QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: white; border-radius:100px}'
                                  )
            self.startStopAnalyzingButt.setText('START')
        elif self.measurementIsRunning == True:# We are in Start mode, so we change button to Stop
            if self.snifferConfig.configCurrentTheme == 'Dark':
                self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: tomato; border-radius:100px}'
                                              'QPushButton:pressed {border: 2px solid; border-color: red; background-color: maroon; border-radius:100px}'
                                              'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                              'QPushButton:focus {border: 2px solid; border-color: red; background-color: #31363b; border-radius:100px}'
                                              )
            else:
                self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: tomato; border-radius:100px}'
                                  'QPushButton:pressed {border: 2px solid; border-color: red; background-color: maroon; border-radius:100px}'
                                  'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                  'QPushButton:focus {border: 2px solid; border-color: red; background-color: white; border-radius:100px}'
                                  )    
            self.startStopAnalyzingButt.setText('STOP')    
        
    ## Display a message in the statusBox of the tab
    #  @param myMessage the message that is to be displayed in the statusBox      
    def displayStatusMessage(self,myMessage):
        self.statusBox.setText('Message: ' + myMessage)    
        
    ## Obsolete, replaced by the HardwareFilter-tab
    def hardwareFilter(self):
        try:
            self.serialHandle = serial.Serial(Globals.dockDict['dockConfig'].snifferConfig.configCom,int(Globals.dockDict['dockConfig'].snifferConfig.configBaud),timeout=3,parity=serial.PARITY_NONE,rtscts=False,dsrdtr=False)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            self.displayException('Exception when opening SerialPort. Check Port?')
            self.enableButtons()
            self.displayStatusMessage('Stopping due to Exception!')
            return
        self.serialHandle.write(b'\x98')
        for _ in range(0,5):
            self.serialHandle.write(b'\xff')
            
        self.serialHandle.write(b'\b11101111')
        for _ in range(0,7):
            self.serialHandle.write(b'\xff')
        self.displayStatusMessage('Tracer should be filtered!')
        self.serialHandle.close()
        
    # --- DOCK-SPECIFIC UI FUNCTIONS --- #
    # -----------------------------------#              
    def waitResetCheckChanged(self):
        self.snifferConfig.configWaitResetCheck ^= 1
        self.logger.logEvent('changed Wait for Reset Checkbox to - '+ str(self.snifferConfig.configWaitResetCheck))
        
    ## Disable all UI-buttons belonging to the tab. This is implementation specific           
    def disableButtons(self):
        self.saveMeasButt.setEnabled(False)
        self.openMeasButt.setEnabled(False)
        print('Disable TabStart Buttons')
        
    ## Enable all UI-buttons belonging to the tab. This is implementation specific         
    def enableButtons(self):
        self.saveMeasButt.setEnabled(True)
        self.openMeasButt.setEnabled(True)
        print('Enable TabStart Buttons')
        
    
    # --- MANDATORY UI FUNCTIONS --- #
    # -------------------------------# 
             
    ## Read out all components of snifferConfig and set the UI elements according to
    #  the saved values.        
    def syncUiToConfig(self):
        #self.waitResetCheck.setChecked(self.snifferConfig.configWaitResetCheck)
        pass