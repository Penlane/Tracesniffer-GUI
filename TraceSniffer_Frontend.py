import sys
import glob
import serial
import queue
import re
import configparser
import qdarkstyle
import csv
import os
import plotly
import ganttForTraceSniffer as gfs
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QProgressBar, QTabWidget, QComboBox, QLineEdit, QLabel, QScrollArea, QFileDialog
from PyQt5.QtWidgets import QSizePolicy, QHeaderView, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.Qt import QTextEdit, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtGui import QPalette, QColor, QFont

informationEnum =('','','','','','','','','','','','','','','START','END','TASK_SWITCHED_IN','INCREASE_TICK_COUNT','LOW_POWER_IDLE_BEGIN','LOW_POWER_IDLE_END','TASK_SWITCHED_OUT','TASK_PRIORITY_INHERIT','TASK_PRIORITY_DISINHERIT','BLOCKING_ON_QUEUE_RECEIVE','BLOCKING_ON_QUEUE_SEND','MOVED_TASK_TO_READY_STATE',
'POST_MOVED_TASK_TO_READY_STATE','QUEUE_CREATE','QUEUE_CREATE_FAILED','CREATE_MUTEX','CREATE_MUTEX_FAILED','GIVE_MUTEX_RECURSIVE','GIVE_MUTEX_RECURSIVE_FAILED','TAKE_MUTEX_RECURSIVE','TAKE_MUTEX_RECURSIVE_FAILED','CREATE_COUNTING_SEMAPHORE','CREATE_COUNTING_SEMAPHORE_FAILED','QUEUE_SEND','QUEUE_SEND_FAILED','QUEUE_RECEIVE','QUEUE_PEEK','QUEUE_PEEK_FROM_ISR','QUEUE_RECEIVE_FAILED','QUEUE_SEND_FROM_ISR','QUEUE_SEND_FROM_ISR_FAILED','QUEUE_RECEIVE_FROM_ISR','QUEUE_RECEIVE_FROM_ISR_FAILED','QUEUE_PEEK_FROM_ISR_FAILED','QUEUE_DELETE',
'TASK_CREATE','TASK_CREATE_FAILED','TASK_DELETE','TASK_DELAY_UNTIL','TASK_DELAY','TASK_PRIORITY_SET','TASK_SUSPEND','TASK_RESUME','TASK_RESUME_FROM_ISR','TASK_INCREMENT_TICK','TIMER_CREATE','TIMER_CREATE_FAILED','TIMER_COMMAND_SEND','TIMER_EXPIRED','TIMER_COMMAND_RECEIVED',
'MALLOC','FREE','EVENT_GROUP_CREATE','EVENT_GROUP_CREATE_FAILED','EVENT_GROUP_SYNC_BLOCK','EVENT_GROUP_SYNC_END','EVENT_GROUP_WAIT_BITS_BLOCK','EVENT_GROUP_WAIT_BITS_END','EVENT_GROUP_CLEAR_BITS','EVENT_GROUP_CLEAR_BITS_FROM_ISR','EVENT_GROUP_SET_BITS','EVENT_GROUP_SET_BITS_FROM_ISR',
'EVENT_GROUP_DELETE','PEND_FUNC_CALL','PEND_FUNC_CALL_FROM_ISR','QUEUE_REGISTRY_ADD','TASK_NOTIFY_TAKE_BLOCK','TASK_NOTIFY_TAKE','TASK_NOTIFY_WAIT_BLOCK','TASK_NOTIFY_WAIT','TASK_NOTIFY','TASK_NOTIFY_FROM_ISR','TASK_NOTIFY_GIVE_FROM_ISR','CUSTOM_MARKER_1','CUSTOM_MARKER_2','CUSTOM_MARKER_3','CUSTOM_MARKER_4','CUSTOM_MARKER_5')

queueInfoTuple = (23,24,27,28,29,30,36,37,38,39,40,41,42,43,44,45,46,47)

queueEnum = ('Queue','Mutex','Counting Semaphore','Binary Semaphore','Recursive Mutex')
payloadList = []
communicationQueue = queue.Queue()


class SerialThread(QtCore.QThread):

    startInterpretationSignal = QtCore.pyqtSignal()
    stopMe = QtCore.pyqtSignal()
    
    def kill(self):
        self.isReading = False
        self.quit()
        
    def stop(self):
        self.isReading = False
        self.isWaiting = False
    
    def __init__(self, serialHandle, singleshotTime, timeByteCount, triggerOn, waitResetOn, selectedTrigger, saveIncTime, parent=None):
        super(SerialThread, self).__init__(parent)
        self.serialHandler = serialHandle
        self.singleshotTime = singleshotTime
        self.timeByteCount = timeByteCount
        self.triggerOn = triggerOn
        self.saveIncTime = saveIncTime
        self.selectedTrigger = selectedTrigger
        self.snifferCnt = 0
        self.waitResetOn = waitResetOn
        self.myCnt = 0
        self.failCnt = 0
        self.waitCnt = 0
        # Todo: Fix timeout
        self.timeOut = 100000
        self.isReading = True
        self.isWaiting = True
        self.killme = False
        payloadList.clear() 

    def run(self):
        # Todo: Improve Stop-handling
        if(self.waitResetOn == True):
            self.resetCnt = 0
            self.timeOutCnt = 0
            while(self.resetCnt < 5 and self.isWaiting == True):
                print('Waiting for Reset')
                if(self.serialHandler.read(1) == b'\x00' and self.killme == False):
                    self.resetCnt = self.resetCnt + 1
                    self.timeOutCnt = self.timeOutCnt + 1
                    if(self.timeOutCnt > self.timeOut):
                        print('Timeout Occured! Please Stop the Thread!!!')
                        self.serialHandler.close()
                        self.isReading = False
                        self.killme = True
                        self.isWaiting = False
                        self.stopMe.emit()
                else:
                    self.resetCnt = 0
            print('I am free! Starting measurement')
        while (self.isReading):
            self.killme = False
            self.byteBuffer = (self.serialHandler.read(1))
            if self.byteBuffer == b'\x00':
                self.snifferPayload = PayloadData()
                self.snifferPayload.tickCount = int.from_bytes(self.serialHandler.read(2),byteorder='big',signed=False)
                if(self.timeByteCount == 0):
                    self.snifferPayload.timerValue = 0
                else:
                    self.snifferPayload.timerValue = int.from_bytes(self.serialHandler.read(int(self.timeByteCount)),byteorder='big',signed=False)
                infoID = int.from_bytes(self.serialHandler.read(1),byteorder='big',signed=False)
                print(infoID)
                if infoID > 13 and infoID < 100:
                    self.snifferPayload.infoType = informationEnum[infoID]    
                    print(self.snifferPayload.infoType)
                else:
                    self.snifferPayload.infoType = 'FAILED'
                    self.failCnt = self.failCnt + 1
                    communicationQueue.put_nowait('FAILED_PACKET_DETECTED')
                    if(self.failCnt > 10):
                        print('Too many failed packets, check parameters')
                        self.failCnt = 0
                        self.snifferCnt = 0
                        self.myCnt = 0
                        self.serialHandler.close()
                        self.stop()
                    continue
                length = self.serialHandler.read(1)
                self.snifferPayload.messageLength = int.from_bytes(length,byteorder='big',signed=False)
                if(self.snifferPayload.messageLength > 20):
                    self.snifferPayload.infoType = 'TOO_LONG'
                    self.snifferPayload.messageLength = 0
                    self.snifferPayload.message = 'CONTINUE'
                    continue #fix crash 
                self.snifferPayload.message="";
                if infoID in queueInfoTuple:
                    value = self.serialHandler.read(1)
                    queueNumber = int.from_bytes(value,byteorder='big',signed=False)
                    self.snifferPayload.message = queueEnum[queueNumber]
                else:
                    for _ in range(0,self.snifferPayload.messageLength):
                        value = self.serialHandler.read(1)
                        self.snifferPayload.message+=chr(value[0])
                        self.snifferPayload.message = str(self.snifferPayload.message)
                if self.triggerOn == True:
                    if (self.snifferPayload.infoType != self.selectedTrigger):
                        print('Wrong Trigger, skipping packet')
                        continue
                    else:
                        self.triggerOn = False
                if(self.snifferPayload.infoType == 'TASK_INCREMENT_TICK'):
                    self.snifferCnt+=1
                self.myCnt = self.myCnt + 1  
                communicationQueue.put_nowait('INCREMENT_PROGRESSBAR')
                if(self.singleshotTime != 0):
                    if(self.snifferCnt > self.singleshotTime):
                        print('Measure complete, stopping thread')
                        self.snifferCnt = 0
                        self.myCnt = 0
                        self.serialHandler.close()
                        self.stop()
                        self.startInterpretationSignal.emit()
                if self.saveIncTime == False:
                    if(self.snifferPayload.infoType != 'TASK_INCREMENT_TICK'):
                        payloadList.append(self.snifferPayload)
                else:
                    payloadList.append(self.snifferPayload)
        self.killme = True
          
class TraceSnifferMain(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self. title = 'TraceSniffer'
        self.initUI()        
        
    def initUI(self):               
        self.statusBar().showMessage('Ready')
                
        self.setGeometry(400, 400, 950, 650)
        self.setWindowTitle('TraceSniffer')    
        
        self.traceTabs = TraceTabs(self)
        self.setCentralWidget(self.traceTabs)
                
        self.show()
        
class TraceTabs(QWidget):
   
    def __init__(self,parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create necessary variables
        self.saveLogToggleState = 0
        self.saveMeasToggleState = 0
        self.saveIncTimeToggleState = 0
        self.waitResetCheckToggleState = 0
        self.writePayload = PayloadData()
        self.logPayload = PayloadData()
        self.singleShotTime = 0
        self.snifferPayload = PayloadData()
        self.configData = ConfigurationData()
        self.snifferCnt = 0
        self.failCnt = 0
        self.purge = 0
        self.currentTheme = 'Dark'
        self.measurementIsRunning = 0
        
        # Load configuration
        self.guiConfig = configparser.ConfigParser()
        self.guiConfig.read('sniffconfig.scfg')
        try:
            self.configData.parseConfig(self.guiConfig)
        except KeyError:
            print('Incorrect entry in sniffconfig.scfg found, defaulting to default.scfg')
            self.guiConfig.read('default.scfg')
            self.configData.parseConfig(self.guiConfig)
            
        # Initialize GUI-theme
        self.currentTheme = self.configData.currentTheme
        
        if self.currentTheme == 'Dark':
            self.loadTheme('Dark')
        else:
            self.loadTheme('Light')

        
        # Create necessary Lists
        self.COMList = OS_SerialPortList()
        self.BAUDList = ['9600','115200','1000000','2000000']
        self.STOPList = ['0','1','2']
        self.PARITYList = ['None','Even','Odd']
        self.MODEList = ['Singleshot','Continuous','Trigger']
        self.TIMEList = ['0','1','2','3','4']
        self.TRIGGERList = ['START','END','TASK_SWITCHED_IN','INCREASE_TICK_COUNT','LOW_POWER_IDLE_BEGIN','LOW_POWER_IDLE_END','TASK_SWITCHED_OUT','TASK_PRIORITY_INHERIT','TASK_PRIORITY_DISINHERIT','BLOCKING_ON_QUEUE_RECEIVE','BLOCKING_ON_QUEUE_SEND','MOVED_TASK_TO_READY_STATE',
        'POST_MOVED_TASK_TO_READY_STATE','QUEUE_CREATE','QUEUE_CREATE_FAILED','CREATE_MUTEX','CREATE_MUTEX_FAILED','GIVE_MUTEX_RECURSIVE','GIVE_MUTEX_RECURSIVE_FAILED','TAKE_MUTEX_RECURSIVE','TAKE_MUTEX_RECURSIVE_FAILED','CREATE_COUNTING_SEMAPHORE','CREATE_COUNTING_SEMAPHORE_FAILED','QUEUE_SEND','QUEUE_SEND_FAILED','QUEUE_RECEIVE','QUEUE_PEEK','QUEUE_PEEK_FROM_ISR','QUEUE_RECEIVE_FAILED','QUEUE_SEND_FROM_ISR','QUEUE_SEND_FROM_ISR_FAILED','QUEUE_RECEIVE_FROM_ISR','QUEUE_RECEIVE_FROM_ISR_FAILED','QUEUE_PEEK_FROM_ISR_FAILED','QUEUE_DELETE',
        'TASK_CREATE','TASK_CREATE_FAILED','TASK_DELETE','TASK_DELAY_UNTIL','TASK_DELAY','TASK_PRIORITY_SET','TASK_SUSPEND','TASK_RESUME','TASK_RESUME_FROM_ISR','TASK_INCREMENT_TICK','TIMER_CREATE','TIMER_CREATE_FAILED','TIMER_COMMAND_SEND','TIMER_EXPIRED','TIMER_COMMAND_RECEIVED',
        'MALLOC','FREE','EVENT_GROUP_CREATE','EVENT_GROUP_CREATE_FAILED','EVENT_GROUP_SYNC_BLOCK','EVENT_GROUP_SYNC_END','EVENT_GROUP_WAIT_BITS_BLOCK','EVENT_GROUP_WAIT_BITS_END','EVENT_GROUP_CLEAR_BITS','EVENT_GROUP_CLEAR_BITS_FROM_ISR','EVENT_GROUP_SET_BITS','EVENT_GROUP_SET_BITS_FROM_ISR',
        'EVENT_GROUP_DELETE','PEND_FUNC_CALL','PEND_FUNC_CALL_FROM_ISR','QUEUE_REGISTRY_ADD','TASK_NOTIFY_TAKE_BLOCK','TASK_NOTIFY_TAKE','TASK_NOTIFY_WAIT_BLOCK','TASK_NOTIFY_WAIT','TASK_NOTIFY','TASK_NOTIFY_FROM_ISR','TASK_NOTIFY_GIVE_FROM_ISR','CUSTOM_MARKER_1','CUSTOM_MARKER_2','CUSTOM_MARKER_3','CUSTOM_MARKER_4','CUSTOM_MARKER_5']
        self.INACTIVEList = ['INACTIVE']
        
        # Create variables corresponding to the ComboBox states
        self.selectedCOM = self.COMList[0]
        self.selectedBAUD = self.BAUDList[0]
        self.selectedMODE = self.MODEList[0]
        print(self.selectedMODE)
        self.selectedTIME = self.TIMEList[0]
        self.selectedTRIGGER = self.TRIGGERList[0]
        
        # Create necessary Queues
        self.logQueue = queue.Queue()
        
        self.payloadListIndex = 0
            
        # Initialize Tabs
        self.tabs = QTabWidget()
        self.tabStart = QWidget()
        self.tabPlot = QWidget()
        self.tabDetails = QWidget()
        self.tabInstruct = QWidget()
        self.tabConfig = QWidget()
        self.tabs.resize(600,900)
        
        # Add Tabs
        self.tabs.addTab(self.tabStart,"Start")
        self.tabs.addTab(self.tabDetails,"Table")
        self.tabs.addTab(self.tabPlot,"Plot")
        self.tabs.addTab(self.tabConfig,"Configuration")
        self.tabs.addTab(self.tabInstruct,"Instructions")
        
        #-------------------------TAB CREATION-------------------------#
        
        # Create Start Tab --------------------###   
        # Create Layouts
        self.tabStart.Vlayout = QVBoxLayout()
        
        self.tabStart.H1layout = QHBoxLayout()
        self.tabStart.H1layout.setSpacing(15)
        self.tabStart.H1layout.addSpacing(60)
        
        self.tabStart.H2layout = QHBoxLayout()
        self.tabStart.H2SubV1Layout = QVBoxLayout()
        self.tabStart.H2SubH1Layout = QHBoxLayout()
        self.tabStart.H2SubV2Layout = QVBoxLayout()
        self.tabStart.H2layout.setSpacing(15)
        
        self.tabStart.H3layout = QHBoxLayout()
        self.tabStart.H3layout.setSpacing(15)
        #------------------------------------
        
        # Create Widgets for H1layout
        # First buttons
        self.startStopAnalyzingButt = QPushButton('START')
        self.startStopAnalyzingButt.clicked.connect(self.toggleAnalyzing)
        self.startStopAnalyzingButt.setStyleSheet('QPushButton {border: 2px solid; border-color: tomato; border-radius:100px}'
                                      'QPushButton:pressed {border: 2px solid; border-color: red; background-color: maroon; border-radius:100px}'
                                      'QPushButton:hover {border: 2px solid; border-color: white; border-radius:100px}'
                                      'QPushButton:focus {border: 2px solid; border-color: red; border-radius:100px}'
                                      )
        self.startStopFont = QFont()
        self.startStopFont.setPointSize(20)
        self.startStopAnalyzingButt.setFont(self.startStopFont)
        
        self.startStopAnalyzingButt.setFixedSize(200,200)
        # Add Widgets to H1layout
        self.tabStart.H1layout.addWidget(self.startStopAnalyzingButt)
        
        # Spacing for H1layout
        self.tabStart.H1layout.addSpacing(5)
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
        self.createPlotButt.clicked.connect(self.createPlot)
        self.waitResetCheck = QCheckBox('Wait for uC Reset')
        self.waitResetCheck.stateChanged.connect(self.waitResetCheckToggle)  
        # Set Init Value for checkbox
        self.waitResetCheck.setChecked(self.configData.waitResetCheckbox)

        # Add Widgets to H2layout        
        self.tabStart.H2layout.addWidget(self.statusLabel)
        self.tabStart.H2layout.addWidget(self.statusBox)
        self.tabStart.H2layout.addSpacing(40)
        self.tabStart.H2layout.addWidget(self.waitResetCheck)
        self.tabStart.H2layout.addWidget(self.createPlotButt)
        self.tabStart.H2layout.addWidget(self.saveMeasButt)
        self.tabStart.H2layout.addWidget(self.openMeasButt)
        
        # Endspacing for H2layout
        self.tabStart.H2layout.addSpacing(5)
        #------------------------------------
        
        # Create Widgets for H3layout
        self.progressShotBar = QProgressBar()
        
        # Add Widgets to H3layout
        self.tabStart.H3layout.addWidget(self.progressShotBar)
        #------------------------------------       
        self.tabStart.Vlayout.addSpacing(130)
        self.tabStart.Vlayout.addLayout(self.tabStart.H1layout)
        self.tabStart.Vlayout.addStretch()
        self.tabStart.Vlayout.addLayout(self.tabStart.H2layout)
        self.tabStart.Vlayout.addLayout(self.tabStart.H3layout)
        
        self.tabStart.setLayout(self.tabStart.Vlayout)
            
        
        # Create Table Tab --------------------###    
        # Create Layouts
        self.tabDetails.Vlayout = QVBoxLayout()
        self.tabDetails.H1layout = QHBoxLayout()
        
        # Create Widgets for H1layout
        # First buttons
        self.clearTableButt = QPushButton('Clear Table')
        self.stopTableButt = QPushButton('Stop Table')
        
        # Add Widgets to H1layout
        self.tabDetails.H1layout.addWidget(self.clearTableButt)
        #self.tabDetails.H1layout.addWidget(self.stopTableButt)
        self.clearTableButt.clicked.connect(self.clearTable)
        self.stopTableButt.clicked.connect(self.stopTable)

        # Spacing for H1layout
        self.tabStart.H1layout.addSpacing(30)
        #------------------------------------
        
        # Create Table
        self.detailTableIndex = 0
        self.detailTable = QTableWidget()
        self.detailTableItem = QTableWidgetItem()
        self.detailTable.setRowCount(0)
        self.detailTable.setColumnCount(5)
        
        self.detailTable.setHorizontalHeaderLabels('Tick;Timer;Type;Message;Length'.split(';'))
        self.detailTable.resizeColumnsToContents()
        self.detailTableHeader = self.detailTable.horizontalHeader()
        self.detailTableHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.detailTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)        
        self.detailTableHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.detailTableHeader.setSectionResizeMode(3, QHeaderView.Stretch)
        self.detailTableHeader.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        #------------------------------------                                      
        self.tabDetails.Vlayout.addLayout(self.tabDetails.H1layout)
        self.tabDetails.Vlayout.addWidget(self.detailTable)
        
        self.tabDetails.setLayout(self.tabDetails.Vlayout)       
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
         
        # Create Plot Tab --------------------###    
        # Create Layouts
        self.tabPlotVlayout = QVBoxLayout()
        self.tabPlotH1layout = QHBoxLayout()
        self.tabPlotH1layout.setSpacing(15)
        #------------------------------------
         
        # Create Widgets for H1layout
        # First buttons
        self.clearScreenButt = QPushButton('Clear Screen')
        self.stopDisplayButt = QPushButton('Stop Display')
        self.clearScreenButt.clicked.connect(self.clearScreen)
        self.stopDisplayButt.clicked.connect(self.stopDisplay)
         
        # Add Widgets to H1layout
        self.tabPlotH1layout.addWidget(self.clearScreenButt)
        self.tabPlotH1layout.addWidget(self.stopDisplayButt)
         
        # Create Browser
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.browser.load(QtCore.QUrl().fromLocalFile(os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources','img','launch.html')))
        #------------------------------------
         
        #self.tabPlotVlayout.addLayout(self.tabPlotH1layout)
        self.tabPlotVlayout.addWidget(self.browser)
         
        self.tabPlot.setLayout(self.tabPlotVlayout)  
        
             
        # Create Configurations Tab --------------------###    
        # Create Layouts
        self.tabConfig.Vlayout = QVBoxLayout()
        self.tabConfig.H1layout = QHBoxLayout()
        self.tabConfig.H1layout.setSpacing(10)
        self.tabConfig.H1SubV1Layout = QVBoxLayout()
        self.tabConfig.H1SubV1H1Layout = QHBoxLayout()
        self.tabConfig.H1SubV1H2Layout = QHBoxLayout()
        self.tabConfig.H1SubV1H3Layout = QHBoxLayout()
        self.tabConfig.H1SubV1H4Layout = QHBoxLayout()
        self.tabConfig.H1SubV1H5Layout = QHBoxLayout()
        self.tabConfig.H1SubV2Layout = QVBoxLayout()
        self.tabConfig.H1SubV2H1Layout = QHBoxLayout()
        self.tabConfig.H1SubV2H2Layout = QHBoxLayout()
        self.tabConfig.H1SubV2H3Layout = QHBoxLayout()
        self.tabConfig.H1SubV2H4Layout = QHBoxLayout()
        self.tabConfig.H2layout = QHBoxLayout()
        self.tabConfig.H2layout.setSpacing(10)
            
        #------------------------------------
        
        # Create Widgets TextBox
        #------------------------------------
        
        # First Buttons
        self.saveLogButt = QPushButton('Save Logfile')
        self.saveConfigButt = QPushButton('Save Configuration')
        self.toggleThemeButt = QPushButton('Toggle Theme')
                              
        # Then Checkbox and Comboboxes
        self.saveLogCheck = QCheckBox('Activate Logging')
        self.saveMeasCheck = QCheckBox('Activate Sniff')
        self.saveIncTimeCheck = QCheckBox('Save Inc_Tick Data')
        
        self.labelSerial = QLabel('Serial Configuration')
        self.labelCOM = QLabel('COM-PORT')
        self.labelBAUD = QLabel('BAUD-RATE')
        self.labelSTOP= QLabel('STOP-BITS')
        self.labelPARITY= QLabel('PARITY')
        self.labelMeasure = QLabel('Measurement Configuration')
        self.labelMODE = QLabel('MEASUREMENT MODE')
        self.labelTIME = QLabel('COUNT TIME BYTES')
        self.labelSINGLETIME = QLabel('MEASUREMENT TIME')
        self.labelTRIGGER = QLabel('TRIGGER TYPE')
        self.labelRATIO = QLabel('TICK TO MS RATIO')
        
        self.inputSingleDurBox = QLineEdit()
        self.inputSingleDurBox.setText('Duration(ticks)')
        self.inputSingleDurBox.setMaximumWidth(200)
        
        self.inputTickToMsBox = QLineEdit()
        self.inputTickToMsBox.setText('Set Ticks to Ms Ratio')
        self.inputTickToMsBox.setMaximumWidth(200)
        
        self.comboMODE = QComboBox()
        self.comboMODE.addItems(self.MODEList)  
              
        self.comboCOM = QComboBox()
        self.comboCOM.addItems(self.COMList)   
            
        self.comboBAUD = QComboBox()
        self.comboBAUD.addItems(self.BAUDList)
        
        self.comboSTOP = QComboBox()
        self.comboSTOP.addItems(self.STOPList)   
            
        self.comboPARITY = QComboBox()
        self.comboPARITY.addItems(self.PARITYList)      
        
        self.comboTRIGGER = QComboBox()
        self.comboTRIGGER.addItems(self.TRIGGERList)     
          
        self.comboTIME = QComboBox()
        self.comboTIME.addItems(self.TIMEList)
        
        #--- SIGNAL/SLOT CONNECTIONS ---#
        # Button Signal/Slot connections
        self.saveLogButt.clicked.connect(self.saveLog)
        self.saveConfigButt.clicked.connect(self.saveConfiguration)
        self.toggleThemeButt.clicked.connect(self.toggleTheme)
        
        # Checkbox Signal/Slot connections
        self.saveLogCheck.stateChanged.connect(self.saveLogCheckToggle)
        self.saveMeasCheck.stateChanged.connect(self.saveMeasCheckToggle)  
        self.saveIncTimeCheck.stateChanged.connect(self.saveIncTimeCheckToggle)
        
        # Combobox Signal/Slot connections
        self.comboMODE.currentIndexChanged[int].connect(self.comboMODEchanged)     
        self.comboCOM.currentIndexChanged[int].connect(self.comboCOMchanged)
        self.comboBAUD.currentIndexChanged[int].connect(self.comboBAUDchanged) 
        self.comboSTOP.currentIndexChanged[int].connect(self.comboSTOPchanged)
        self.comboPARITY.currentIndexChanged[int].connect(self.comboPARITYchanged) 
        self.comboTRIGGER.currentIndexChanged[int].connect(self.comboTRIGGERchanged)
        self.comboTIME.currentIndexChanged[int].connect(self.comboTIMEchanged)  
        
        # Create necessary Timers
        self.serialTimer = QTimer()
        self.serialTimer.timeout.connect(self.serialDataTick)
        
        # Initialize the widgets from config file
        self.saveLogCheck.setChecked(self.configData.logCheckbox)
        self.saveMeasCheck.setChecked(self.configData.measureCheckbox)
        self.saveIncTimeCheck.setChecked(self.configData.incTimeCheckbox)
        
        self.comboCOM.setCurrentText(self.configData.comPort)
        self.comboBAUD.setCurrentText(str(self.configData.baudRate))
        self.comboMODE.setCurrentText(self.configData.measureMode)
        self.comboTRIGGER.setCurrentText(self.configData.selectedTrigger)
        self.comboTIME.setCurrentText(str(self.configData.timeBytes))
        self.inputSingleDurBox.setText(str(self.configData.singleshotTime))
        self.inputTickToMsBox.setText(str(self.configData.timeValueToMs))
        
        # Add the Widgets to the corresponding Layouts
        self.tabConfig.H1SubV1H1Layout.addWidget(self.labelCOM)
        self.tabConfig.H1SubV1H1Layout.addWidget(self.comboCOM)
        self.tabConfig.H1SubV1H2Layout.addWidget(self.labelBAUD)
        self.tabConfig.H1SubV1H2Layout.addWidget(self.comboBAUD)
        self.tabConfig.H1SubV1H3Layout.addWidget(self.labelSTOP)
        self.tabConfig.H1SubV1H3Layout.addWidget(self.comboSTOP)
        self.tabConfig.H1SubV1H4Layout.addWidget(self.labelPARITY)
        self.tabConfig.H1SubV1H4Layout.addWidget(self.comboPARITY)
        
        self.tabConfig.H1SubV1Layout.addWidget(self.labelSerial)
        self.tabConfig.H1SubV1Layout.addLayout(self.tabConfig.H1SubV1H1Layout)
        self.tabConfig.H1SubV1Layout.addLayout(self.tabConfig.H1SubV1H2Layout)
        self.tabConfig.H1SubV1Layout.addLayout(self.tabConfig.H1SubV1H3Layout)
        self.tabConfig.H1SubV1Layout.addLayout(self.tabConfig.H1SubV1H4Layout)
        
        self.tabConfig.H1SubV2H1Layout.addWidget(self.labelMODE)
        self.tabConfig.H1SubV2H1Layout.addWidget(self.comboMODE)
        self.tabConfig.H1SubV2H2Layout.addWidget(self.labelTRIGGER)
        self.tabConfig.H1SubV2H2Layout.addWidget(self.comboTRIGGER)
        self.tabConfig.H1SubV2H3Layout.addWidget(self.labelTIME)
        self.tabConfig.H1SubV2H3Layout.addWidget(self.comboTIME)
        self.tabConfig.H1SubV2H4Layout.addWidget(self.saveIncTimeCheck)
        self.tabConfig.H1SubV2H4Layout.addWidget(self.saveLogCheck)
        self.tabConfig.H1SubV2H4Layout.addWidget(self.saveLogButt)
        self.tabConfig.H1SubV2H4Layout.addWidget(self.toggleThemeButt)
        
        self.tabConfig.H1SubV2Layout.addWidget(self.labelMeasure)
        self.tabConfig.H1SubV2Layout.addLayout(self.tabConfig.H1SubV2H1Layout)
        self.tabConfig.H1SubV2Layout.addLayout(self.tabConfig.H1SubV2H2Layout)
        self.tabConfig.H1SubV2Layout.addLayout(self.tabConfig.H1SubV2H3Layout)
        self.tabConfig.H1SubV2Layout.addLayout(self.tabConfig.H1SubV2H4Layout)
        
        self.tabConfig.H1layout.addLayout(self.tabConfig.H1SubV1Layout)
        self.tabConfig.H1layout.addLayout(self.tabConfig.H1SubV2Layout)
        
        self.tabConfig.H2layout.addWidget(self.labelSINGLETIME)
        self.tabConfig.H2layout.addWidget(self.inputSingleDurBox)
        self.tabConfig.H2layout.addWidget(self.labelRATIO)
        self.tabConfig.H2layout.addWidget(self.inputTickToMsBox)
        self.tabConfig.Vlayout.addLayout(self.tabConfig.H1layout)
        self.tabConfig.Vlayout.addLayout(self.tabConfig.H2layout)
        self.tabConfig.Vlayout.addStretch()
        self.tabConfig.Vlayout.addWidget(self.saveConfigButt)
        self.tabConfig.setLayout(self.tabConfig.Vlayout)  
        
        # Create Instructions Tab --------------------###    
        # Create Layouts
        self.tabInstruct.Vlayout = QVBoxLayout()
        #------------------------------------
        
        # Create scrollable TextBox
        self.scrollArea = QScrollArea()
        self.instructionBox = QTextEdit()
        self.instructionBox.setText('<b>LOREM IPSUM DOLOR SIT AMET</b>')
        self.instructionText=open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources','instructions','INSTRUCTIONS.html')).read()
        self.instructionBox.setHtml(self.instructionText)
        self.instructionBox.setReadOnly(True)
        self.instructionBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.instructionBox)
        #------------------------------------
        self.tabInstruct.Vlayout.addWidget(self.scrollArea)
        
        self.tabInstruct.setLayout(self.tabInstruct.Vlayout)
        
    #-------------------------STATUS MESSAGE IMPLEMENTATIONS-------------------------#
    def displayStatusMessage(self,myMessage):
        self.statusBox.setText('Message: ' + myMessage)    
                
    def displayException(self,myException):
        QMessageBox.about(self,'ERROR',myException)
        self.statusBox.setText('Exception occured: ' + myException)   
    
    #-------------------------HELPER FUNCTION IMPLEMENTATIONS-------------------------#
    def displayFunction(self,timerValueInMs_extern):
        knownTasks={} #All known tasks which will be displayed in the plot
        readyTasks={} #Saves the ready-state of a task
        dataFrame=[]
        eventWidth=1#Width of an displayed Event in ms
        overflowCounter=0 #Counts how often the tickOverflowValue is surpassed
        tickOverflow = 65536 
        timerValueInMs=timerValueInMs_extern
        previousElementTickCount=payloadList[0].tickCount #Reads the start Time
        for element in payloadList:
            if element.tickCount < previousElementTickCount: #Checks for overflow
                overflowCounter = overflowCounter+1
            previousElementTickCount=element.tickCount
            switch(element.infoType)
            if case("TASK_INCREMENT_TICK"): #switches depending on the infoType
                continue
            if case("TASK_SWITCHED_IN"):
                if element.message in readyTasks: #if the task was ready before,a ready block is plotted
                    try:
                        dataFrame.append({"Task":element.message, "Start":readyTasks[element.message], "Finish":element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs, "Description":"Ready"})
                    except:
                        print("TASK_SWITCHED_IN Failed")
                    del readyTasks[element.message]
                knownTasks.update({element.message:element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs})
                continue
            if case("TASK_SWITCHED_OUT"):#if the task was switched in before,an active block is plotted, otherwise an exception is captured
                try:
                    dataFrame.append({"Task":element.message, "Start":knownTasks[element.message], "Finish":element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs, "Description":"Active"})
                except:
                    print("TASK_SWITCHED_OUT Failed")
                continue
            if case("MOVED_TASK_TO_READY_STATE"):
                readyTasks.update({element.message:element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs})
                continue
            try: #General infoType append
                dataFrame.append({"Task":"Event", "Start":element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs, "Finish":element.tickCount+overflowCounter*tickOverflow+element.timerValue*timerValueInMs+eventWidth, "Description":element.infoType+":"+element.message})
            except:
                print("Other infos Failed")
        self.displayStatusMessage('Iterate over payloadList complete')
        fig = gfs.create_gantt(dataFrame,group_tasks=True, title="Sniffer-Chart"+" | Time: "+ str(datetime.now()),showgrid_x=True)# title beim speichern eingebbar?added Zeit automatisch
        self.displayStatusMessage('Figure Complete')
        plotly.offline.plot(fig, filename=os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources','plots','traceplots.html'),auto_open=False)
        self.displayStatusMessage('Displaying complete')
        self.browser.load(QtCore.QUrl().fromLocalFile(os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources','plots','traceplots.html')))
        self.tabs.setCurrentIndex(2)      
        
    def disableButtons(self):
        self.openMeasButt.setEnabled(False)
        self.saveMeasButt.setEnabled(False)
        self.saveConfigButt.setEnabled(False)
        self.createPlotButt.setEnabled(False)
        self.clearTableButt.setEnabled(False)
        self.saveLogButt.setEnabled(False)
        
    def enableButtons(self):
        self.openMeasButt.setEnabled(True)
        self.saveMeasButt.setEnabled(True)
        self.saveConfigButt.setEnabled(True)
        self.createPlotButt.setEnabled(True)
        self.clearTableButt.setEnabled(True)
        self.saveLogButt.setEnabled(True)
             
    #-------------------------TIMER AREA-------------------------#
    def serialDataTick(self):
        if(communicationQueue.empty() == False):
            myEvent = communicationQueue.get()
            if(myEvent == 'FAILED_PACKET_DETECTED'):
                self.failCnt = self.failCnt+1
                self.displayStatusMessage('FAILED_PACKET Received! Careful! Count: '+str(self.failCnt))
#             if(myEvent == 'INCREMENT_PROGRESSBAR'):
#                 self.progressValue = self.progressValue + 1
#                 self.progressShotBar.setValue(self.progressValue)
                
    #-------------------------HELPER FUNCTIONS-------------------------#    
    def logEvent(self,myEvent):
        print(myEvent)
        if (self.saveLogToggleState == True):
            self.logPayload.message = myEvent
            self.logPayload.timerValue = datetime.now().strftime("%H:%M - %d:%m:%Y")
            self.logQueue.put(self.logPayload)   
    
    def fillTable(self):
        print('Filling Table with all items in PayloadList')
        self.progressShotBar.setMaximum(len(payloadList))
        for self.tablePayload in payloadList:
            self.detailTable.insertRow(self.detailTableIndex)
            self.detailTable.setItem(self.detailTableIndex,0,QTableWidgetItem(str(self.tablePayload.tickCount)))
            self.detailTable.setItem(self.detailTableIndex,1,QTableWidgetItem(str(self.tablePayload.timerValue)))
            self.detailTable.setItem(self.detailTableIndex,2,QTableWidgetItem(str(self.tablePayload.infoType)))
            self.detailTable.setItem(self.detailTableIndex,3,QTableWidgetItem(str(self.tablePayload.message)))
            self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.messageLength)))
            self.detailTableIndex+=1
            self.progressShotBar.setValue(self.detailTableIndex)
        self.displayStatusMessage('Table filled completely, check the tab')
    #-------------------------SIGNAL/SLOT IMPLEMENTATION-------------------------#
    def startInterpreter(self):
        if(len(payloadList) > 0):
            self.fillTable()   
        self.measurementIsRunning = False
        self.setStartStopButtonStyle() 
        self.enableButtons()
    
    def toggleAnalyzing(self):
        print('Deciding wether to Start/Stop Analyzing')
        if self.measurementIsRunning == True:
            self.enableButtons()
            self.displayStatusMessage('Measurement is stopping...')
            self.measurementIsRunning = False
            self.setStartStopButtonStyle()
            self.logEvent('stop Analyzing clicked')     
            self.progressShotBar.setMaximum(100)
            self.progressShotBar.setMinimum(0)
            self.progressShotBar.setValue(0)
            self.serialTimer.stop()
            try:
                self.measureThread.stop()
                while(self.measureThread.killme == False):
                    print('Cannot kill, waiting until last measurement is complete')
                self.serialHandle.close()
                self.displayStatusMessage('Measurement stopped.')    
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                self.displayException('Probably a missing Handler')           
        elif self.measurementIsRunning == False:
            self.disableButtons()
            self.measurementIsRunning = True
            self.setStartStopButtonStyle()
            self.logEvent('start Analyzing clicked - ' + self.selectedMODE)
            self.tabStart.setLayout(self.tabStart.Vlayout)
            if(self.selectedMODE == 'Continuous'):
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.singleShotTime = 0xFFFFFFFF
                self.triggerOn = False
                self.displayStatusMessage('Measuring with Continuousmode')
                            
            if(self.selectedMODE == 'Singleshot'):
                try:
                    self.singleShotTime = int(self.inputSingleDurBox.text())
                except ValueError:
                    QMessageBox.about(self,'ERROR','No integer entered, defaulting to 50')
                    self.singleShotTime = 50
                #self.progressShotBar.setMaximum(self.singleShotTime)
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.progressValue = 0
                self.triggerOn = False
                self.displayStatusMessage('Measuring with Singleshotmode, wait for '+str(self.singleShotTime)+'ms.')
                    
            if(self.selectedMODE == 'Trigger'):
                try:
                    self.singleShotTime = int(self.inputSingleDurBox.text())
                except ValueError:
                    QMessageBox.about(self,'ERROR','No integer entered, defaulting to 50')
                    self.singleShotTime = 50
                self.progressShotBar.setMaximum(0)
                self.progressShotBar.setMinimum(0)
                self.progressShotBar.setValue(0)
                self.triggerOn = True
                self.displayStatusMessage('Measuring with Triggermode')
            try:
                self.serialHandle = serial.Serial(self.selectedCOM,int(self.selectedBAUD),timeout=None,parity=serial.PARITY_NONE,rtscts=False)
                self.measureThread = SerialThread(serialHandle = self.serialHandle, singleshotTime = self.singleShotTime, timeByteCount = self.comboTIME.currentIndex(), triggerOn = self.triggerOn, waitResetOn = self.waitResetCheckToggleState, selectedTrigger = self.selectedTRIGGER, saveIncTime = self.saveIncTimeToggleState)
                self.measureThread.startInterpretationSignal.connect(self.startInterpreter)
                self.measureThread.stopMe.connect(self.toggleAnalyzing)
                self.measureThread.start()
                self.failCnt = 0
                self.serialTimer.start(5)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.about(self,'ERROR','SerialHandle creation issue')
                self.measureThread.kill()   
            
    def createPlot(self):
        if(len(payloadList) == 0):
            self.displayException('The PayloadList ist empty. Run a measurement?')
            return
        self.displayFunction(timerValueInMs_extern = int(self.inputTickToMsBox.text()))
        
    def saveLog(self):
        print('Trying to save logs')
        if(self.logQueue.empty() == True):
            self.displayException('Logging Queue empty. Did you enable the checkbox?')
        else:
            self.displayStatusMessage('Logs found, trying to save...')
            self.saveLogDirectory, self.purge = QFileDialog.getSaveFileName(self, 'Save File', '', 'Logfile (*.slog)')
            print(self.saveLogDirectory)
            self.logFile = open(self.saveLogDirectory,'a+')
            while(self.logQueue.empty() == False):
                self.writePayload = self.logQueue.get()
                self.logFile.write(str(self.writePayload.timerValue)+', '+str(self.writePayload.infoType)+', '+str(self.writePayload.message)+'\n')
            self.logFile.close()
            self.displayStatusMessage('Done saving logs, check your file/directory')
        
    def saveLogCheckToggle(self):
        self.saveLogToggleState ^= 1
        if(self.saveLogToggleState == True):           
            print('Save Logs enabled')
        else:
            print('Save Logs Disabled')
            
    def saveMeasurement(self):
        print('Trying to save Measurement')
        if(len(payloadList)== 0):
            self.displayException('payload List empty. Did you run a measurement?')
        else:
            self.displayStatusMessage('Measurements found, trying to save...')
            self.saveMeasDirectory, self.purge = QFileDialog.getSaveFileName(self, 'Save File', '', 'Sniff files (*.sniff)')
            print(self.saveMeasDirectory)
            try:
                with open(self.saveMeasDirectory,'a+', newline='') as self.measFile:
                    try:
                        self.measWriter = csv.writer(self.measFile, quotechar='|', quoting = csv.QUOTE_MINIMAL)
                    except Exception as ex:
                        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                        message = template.format(type(ex).__name__, ex.args)
                        print (message)
                    for self.writePayload in payloadList:
                        self.measWriter.writerow([str(self.writePayload.tickCount)]+[str(self.writePayload.timerValue)]+[str(self.writePayload.infoType)]+[str(self.writePayload.message)]+[str(self.writePayload.messageLength)])
                    self.measFile.close()
                self.displayStatusMessage('Done saving measurements, check your file/directory')
            except:
                self.displayStatusMessage('Something went wrong when selecting a file. Did you select a .sniff?') 
            
    def openMeasurement(self):
        print('Trying to open Measurement')
        self.displayStatusMessage('Measurements found, trying to save...')
        self.openMeasDirectory, self.purge = QFileDialog.getOpenFileName(self, 'Save File', '', 'Sniff files (*.sniff)')
        print(self.openMeasDirectory)
        payloadList.clear()
        try:
            with open(self.openMeasDirectory,'r') as self.measFile:
                self.measReader = csv.reader(self.measFile, quotechar='|')
                for rows in self.measReader:
                    self.csvPayload=PayloadData()
                    self.csvPayload.tickCount = int(rows[0])
                    self.csvPayload.timerValue = int(rows[1])
                    self.csvPayload.infoType = rows[2]
                    self.csvPayload.message = rows[3]
                    self.csvPayload.messageLength = int(rows[4])
                    payloadList.append(self.csvPayload)
                self.measFile.close()
            self.fillTable()
            self.displayStatusMessage('Done opening measurements, check your table')
        except:
            self.displayStatusMessage('Something went wrong when selecting a file. Did you select a .sniff?/File might be corrupt')
        
    def saveMeasCheckToggle(self):
        self.saveMeasToggleState ^= 1
        if(self.saveMeasToggleState == True):           
            print('Save Measurement enabled')
        else:           
            print('Save Measurement disabled')
            
    def saveIncTimeCheckToggle(self):
        self.saveIncTimeToggleState ^= 1
        if(self.saveIncTimeToggleState == True):           
            print('Save IncTime enabled')
        else:           
            print('Save IncTime disabled')    
            
    def waitResetCheckToggle(self):
        self.waitResetCheckToggleState ^= 1
        if(self.waitResetCheckToggleState == True):           
            print('Wait for Reset enabled')
        else:           
            print('Wait for Reset disabled')    
            
    def saveConfiguration(self):
        self.writeConfig = configparser.ConfigParser()
        self.writeConfig['SERIALCONFIG'] = {'COM Port': self.selectedCOM, 'Baud Rate': self.selectedBAUD}
        self.writeConfig['MEASURECONFIG'] = {'Time Bytes': self.selectedTIME, 'Measure Mode': self.selectedMODE, 'Selected Trigger': self.selectedTRIGGER, 'Singleshot Time': self.inputSingleDurBox.text(), 'Timervalue to Ms': self.inputTickToMsBox.text()}
        self.writeConfig['CHECKBOXES'] = {'Logcheckbox': self.saveLogCheck.isChecked(), 'Measurecheckbox': self.saveMeasCheck.isChecked(), 'Inctimecheckbox': self.saveIncTimeCheck.isChecked(), 'Waitresetcheckbox': self.waitResetCheck.isChecked()}
        self.writeConfig['GUICONFIG'] = {'Themeselection': self.currentTheme}
        with open('sniffconfig.scfg','w+') as self.cFile:
            try:
                self.writeConfig.write(self.cFile)
                self.displayStatusMessage('Configuration saved successfully')
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)

    def clearScreen(self):
        self.logEvent('clear Screen (Box) clicked')     
        
    def stopDisplay(self):
        self.logEvent('stop Display (Box) clicked')         
        
    def clearTable(self):
        self.logEvent('clear Table clicked')          
        self.detailTable.setRowCount(0)
        self.detailTableIndex = 0
        
    def stopTable(self):
        self.logEvent('stop Table clicked')       
        print('Table stopped')        
        
    def toggleTheme(self):
        if(self.currentTheme == 'Light'):
            self.loadTheme('Dark')
            self.startStopAnalyzingButt.setStyleSheet('QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: #31363b; border-radius:100px}')
        else:
            self.loadTheme('Light')
            self.startStopAnalyzingButt.setStyleSheet('QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: white; border-radius:100px}')
        self.setStartStopButtonStyle()   
    def loadTheme(self,setTheme):
        if setTheme == 'Dark':
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            self.currentTheme = 'Dark'
        else:
            app.setStyleSheet('')
            self.currentTheme = 'Light'
            
    def setStartStopButtonStyle(self):#change the StartStopButton Stylesheets. We either need it to be start or stop, theme is provided by currentTheme var
        if self.measurementIsRunning == False:#We are in Stop mode, so we change button to Start
            if self.currentTheme == 'Dark': #Todo: Improve the theming, this is just a hotfix so the Button looks 'ok' in both themes.
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
            if self.currentTheme == 'Dark':
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
    
    #---CREATE COMBOBOX Callbacks---#
    def comboCOMchanged(self):
        self.selectedCOM = self.COMList[self.comboCOM.currentIndex()]
        self.logEvent('changed COM-Port to - '+ self.selectedCOM)    
    def comboBAUDchanged(self):
        self.selectedBAUD = self.BAUDList[self.comboBAUD.currentIndex()]
        self.logEvent('changed BAUD-Rate to - '+ self.selectedBAUD)   
    def comboSTOPchanged(self):
        self.selectedSTOP = self.STOPList[self.comboSTOP.currentIndex()]
        self.logEvent('changed STOP-Bits to - '+ self.selectedSTOP)    
    def comboPARITYchanged(self):
        self.selectedPARITY = self.PARITYList[self.comboPARITY.currentIndex()]
        self.logEvent('changed PARITY to - '+ self.selectedPARITY)   
    def comboMODEchanged(self):
        self.selectedMODE = self.MODEList[self.comboMODE.currentIndex()]
        self.logEvent('changed Measurement-mode to - '+ self.selectedMODE)   
    def comboTIMEchanged(self):
        print(self.comboTIME.currentText())
        self.selectedTIME = self.TIMEList[self.comboTIME.currentIndex()]
        self.logEvent('changed count of TimerBytes to - '+ self.selectedTIME)   
    def comboTRIGGERchanged(self):
        self.selectedTRIGGER = self.TRIGGERList[self.comboTRIGGER.currentIndex()]
        self.logEvent('changed TriggerType to - '+ self.selectedTRIGGER) 
            
                                          
class PayloadData:
    def __init__(self,startByte=0, tickCount = 0, timerValue = 0, infoType = 0, messageLength = 0, message = 0): 
        self.startByte = startByte
        self.tickCount = tickCount
        self.timerValue = timerValue
        self.infoType = infoType
        self.messageLength = messageLength
        self.message = message
        
class  ConfigurationData:
    def __init__(self,comPort = 'COM4', baudRate = 115200, timeBytes = 2, measureMode = 'Singleshot', selectedTrigger = 'START', singleshotTime = 50, timeValueToMs = 0, logCheckbox = False, measureCheckbox = False, incTimeCheckbox = False, waitResetCheckbox = False, currentTheme = 'Dark'):
        self.comPort = comPort
        self.baudRate = baudRate
        self.timeBytes = timeBytes
        self.measureMode = measureMode
        self.selectedTrigger = selectedTrigger
        self.singleshotTime = singleshotTime
        self.timeValueToMs = timeValueToMs
        self.logCheckbox = logCheckbox
        self.measureCheckbox = measureCheckbox
        self.incTimeCheckbox = incTimeCheckbox
        self.waitResetCheckbox = waitResetCheckbox
        self.currentTheme = currentTheme
        
    def parseConfig(self,configurationFile):
        self.comPort = configurationFile['SERIALCONFIG']['COM Port']
        self.baudRate = int(configurationFile['SERIALCONFIG']['Baud Rate'])
        self.timeBytes = int(configurationFile['MEASURECONFIG']['Time Bytes'])
        self.measureMode = configurationFile['MEASURECONFIG']['Measure Mode']
        self.selectedTrigger = configurationFile['MEASURECONFIG']['Selected Trigger']
        self.singleshotTime = int(configurationFile['MEASURECONFIG']['Singleshot Time'])
        self.timeValueToMs = int(configurationFile['MEASURECONFIG']['Timervalue to Ms'])
        self.logCheckbox = configurationFile.getboolean('CHECKBOXES','Logcheckbox')
        self.measureCheckbox = configurationFile.getboolean('CHECKBOXES','Measurecheckbox')
        self.incTimeCheckbox = configurationFile.getboolean('CHECKBOXES','Inctimecheckbox')
        self.waitResetCheckbox = configurationFile.getboolean('CHECKBOXES', 'Waitresetcheckbox')
        self.currentTheme = configurationFile['GUICONFIG']['Themeselection']

class switch(object):
    value = None
    def __new__(self, value):
        self.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))

WHITE =     QColor(255, 255, 255)
BLACK =     QColor(0, 0, 0)
RED =       QColor(255, 0, 0)
PRIMARY =   QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY =  QColor(42, 130, 218)


def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())

class QDarkPalette(QPalette):
    """Dark palette for a Qt application meant to be used with the Fusion theme."""
    def __init__(self, *__args):
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Static method to set the tooltip stylesheet to a `QtWidgets.QApplication`."""
        app.setStyleSheet("QToolTip {{"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QtWidgets.QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)
        
def OS_SerialPortList():

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # Exclude current terminal using this on unix
        ports = glob.glob('/dev/tty[A-Za-z\d]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

if __name__ == '__main__':
    configReg = re.compile(': (.*)')
    app = QApplication(sys.argv)
    #myPalette = QDarkPalette()
    #myPalette.set_app(app)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ex = TraceSnifferMain()
    sys.exit(app.exec_())