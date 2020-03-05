from Globals import snifferLogList,dockDict
import Globals

from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox
from PyQt5.QtWidgets import QComboBox, QLineEdit, QLabel, QFileDialog

import OsSniffer

from TraceDocks import TraceDocks
from HardwareFilterWidget import HardwareFilter

## @package ConfigTab
# ConfigTab handles all user specified configuration.
# This includes serial configuration and measurement specific
# configuration as well as GUI - specific configuration.

## The actual implementation of the ConfigTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on
class ConfigTab(TraceDocks):
    
    ## The constructor
    #  initialize the super-class, assign a name and first configItems       
    def __init__(self,parent):
        super(ConfigTab, self).__init__(parent,'ConfigTab')
        self.tabName = 'ConfigTab'
        self.logger.logEvent('Creating Tab now: '+ self.tabName)
        
        # Set a couple of default-values, in case the configParser does not work
        self.snifferConfig.configBaud = 1000000
        self.snifferConfig.configCom = 'COM4'
        self.snifferConfig.configMode = 'Singleshot'
        self.snifferConfig.configParity = 'None'
        self.snifferConfig.configStopBits = 0
        self.snifferConfig.configTimeBytes = 2
        self.snifferConfig.configTrigger = 'Start'
        self.snifferConfig.configLogCheck = 0
        self.snifferConfig.configIncTimeCheck = 0
        self.snifferConfig.configTickToMsLine = 1000
        self.snifferConfig.configSingleDurLine = 3000
        self.snifferConfig.configMaxTickCountVal = 65536
        self.snifferConfig.configCurrentTheme = 'Dark'
                
        # By parsing the config now, we assure that we re-load everything
        # the way we left it
        self.snifferConfig.parseConfigFromFile()
        
        # Create necessary Lists
        self.COMList = OsSniffer.OS_SerialPortList()
        self.BAUDList = ['110','300','600','1200','2400','4800','9600','14400','19200','38400','57600','115200','128000','256000','921600','1000000','2000000']
        self.STOPList = ['0','1','2']
        self.PARITYList = ['None','Even','Odd']
        self.MODEList = ['Singleshot','Continuous','Trigger']
        self.TRIGGERList = []
        for triggers in Globals.tspDict.items():
            self.TRIGGERList.append(triggers[1][0])
            
        self.INACTIVEList = ['INACTIVE']
        # We need a list for the items and one for the actual Values
        
        
    ## Create the visible UI            
    def setConfigTabLayout(self):
        
        # Create Configurations Tab --------------------###    
        # Create Layouts
        self.Vlayout = QVBoxLayout()
        self.H1layout = QHBoxLayout()
        self.H1layout.setSpacing(10)
        self.H1SubV1Layout = QVBoxLayout()
        self.H1SubV1H1Layout = QHBoxLayout()
        self.H1SubV1H2Layout = QHBoxLayout()
        self.H1SubV1H3Layout = QHBoxLayout()
        self.H1SubV1H4Layout = QHBoxLayout()
        self.H1SubV1H5Layout = QHBoxLayout()
        self.H1SubV2Layout = QVBoxLayout()
        self.H1SubV2H1Layout = QHBoxLayout()
        self.H1SubV2H2Layout = QHBoxLayout()
        self.H1SubV2H3Layout = QHBoxLayout()
        self.H1SubV2H4Layout = QHBoxLayout()
        self.H1SubV2H5Layout = QHBoxLayout()
        self.H1SubV2H6Layout = QHBoxLayout()
        self.H1SubV2H7Layout = QHBoxLayout()
            
        #------------------------------------
        
        # Create Widgets TextBox
        #------------------------------------
        
        # First Buttons
        self.saveLogButt = QPushButton('Save Logfile')
        self.saveConfigButt = QPushButton('Save Configuration')
        self.toggleThemeButt = QPushButton('Toggle Theme')
        self.refreshComButt = QPushButton('Refresh COM')
        
        # Then Checkbox and Comboboxes
        self.saveLogCheck = QCheckBox('Activate Logging')
        self.saveIncTimeCheck = QCheckBox('Save Inc_Tick Data')
        
        self.labelSerial = QLabel('Serial Configuration')
        self.labelCOM = QLabel('COM-PORT')
        self.labelBAUD = QLabel('BAUD-RATE')
        self.labelSTOP= QLabel('STOP-BITS')
        self.labelPARITY= QLabel('PARITY')
        self.labelMeasure = QLabel('Measurement Configuration')
        self.labelMODE = QLabel('MEASUREMENT MODE')
        self.labelSINGLETIME = QLabel('MEASUREMENT TIME')
        self.labelTRIGGER = QLabel('TRIGGER TYPE')
        self.labelRATIO = QLabel('TICK TO MS RATIO')
        self.labelMaxTickCount = QLabel('MAX TICKOUT VAL')
        
        self.inputSingleDurBox = QLineEdit()
        self.inputSingleDurBox.setText('Duration(ticks)')
        #self.inputSingleDurBox.setMaximumWidth(20)
        
        self.inputTickToMsBox = QLineEdit()
        self.inputTickToMsBox.setText('Set Ticks to Ms Ratio')
        #self.inputTickToMsBox.setMaximumWidth(200)

        self.inputMaxTickCount = QLineEdit()
        self.inputMaxTickCount.setText('Set Maximum Tickcount Val')
        
        self.comboMODE = QComboBox()
        self.comboMODE.addItems(self.MODEList)  
        self.comboCOM = QComboBox()
        self.comboCOM.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboCOM.addItems(self.COMList)   
        self.comboBAUD = QComboBox()
        self.comboBAUD.addItems(self.BAUDList)
        self.comboBAUD.setEditable(True)
        self.comboSTOP = QComboBox()
        self.comboSTOP.addItems(self.STOPList)    
        self.comboPARITY = QComboBox()
        self.comboPARITY.addItems(self.PARITYList)      
        self.comboTRIGGER = QComboBox()
        self.comboTRIGGER.addItems(self.TRIGGERList)     
        
        # We need to sync the UI before connecting any slots in order to prevent accidental stateChanges.
        self.syncUiToConfig() 
        
        #--- SIGNAL/SLOT CONNECTIONS ---#
        # Button Signal/Slot connections
        self.saveLogButt.clicked.connect(self.saveLog)
        for keys, values in dockDict.items(): # We need to connect EVERY tab in order to save the ConfigurationData
            self.saveConfigButt.clicked.connect(values.snifferConfig.saveConfigToFile)  
        self.saveConfigButt.clicked.connect(self.snifferConfig.saveConfigToFile)
        self.toggleThemeButt.clicked.connect(self.toggleTheme)
        self.refreshComButt.clicked.connect(self.refreshCom)
        
        # Checkbox Signal/Slot connections
        self.saveLogCheck.stateChanged.connect(self.checkSaveLogChanged)
        self.saveIncTimeCheck.stateChanged.connect(self.checkSaveInctimeChanged)
        
        # Lineedit Signal/Slot connections
        self.inputSingleDurBox.textChanged.connect(self.lineSingleDurChanged)
        self.inputTickToMsBox.textChanged.connect(self.lineTickToMsChanged)
        self.inputMaxTickCount.textChanged.connect(self.lineMaxTickCountChanged)
        
        # Combobox Signal/Slot connections
        self.comboMODE.currentIndexChanged[int].connect(self.comboModeChanged)     
        self.comboCOM.currentIndexChanged[int].connect(self.comboComChanged)
        self.comboBAUD.currentIndexChanged[int].connect(self.comboBaudChanged) 
        self.comboBAUD.currentTextChanged.connect(self.comboBaudChanged)
        self.comboSTOP.currentIndexChanged[int].connect(self.comboStopBitsChanged)
        self.comboPARITY.currentIndexChanged[int].connect(self.comboParityChanged) 
        self.comboTRIGGER.currentIndexChanged[int].connect(self.comboTriggerChanged)
                
        # Add the Widgets to the corresponding Layouts
        self.H1SubV1H1Layout.addWidget(self.labelCOM)
        self.H1SubV1H1Layout.addWidget(self.refreshComButt)
        self.H1SubV1H1Layout.addWidget(self.comboCOM)
        self.H1SubV1H2Layout.addWidget(self.labelBAUD)
        self.H1SubV1H2Layout.addWidget(self.comboBAUD)
        self.H1SubV1H3Layout.addWidget(self.labelSTOP)
        self.H1SubV1H3Layout.addWidget(self.comboSTOP)
        self.H1SubV1H4Layout.addWidget(self.labelPARITY)
        self.H1SubV1H4Layout.addWidget(self.comboPARITY)
        
        self.H1SubV1Layout.addWidget(self.labelSerial)
        self.H1SubV1Layout.addLayout(self.H1SubV1H1Layout)
        self.H1SubV1Layout.addLayout(self.H1SubV1H2Layout)
        self.H1SubV1Layout.addLayout(self.H1SubV1H3Layout)
        self.H1SubV1Layout.addLayout(self.H1SubV1H4Layout)
        self.H1SubV1Layout.addStretch()
        
        self.H1SubV2H1Layout.addWidget(self.labelMODE)
        self.H1SubV2H1Layout.addWidget(self.comboMODE)
        self.H1SubV2H2Layout.addWidget(self.labelSINGLETIME)
        self.H1SubV2H2Layout.addWidget(self.inputSingleDurBox)
        self.H1SubV2H3Layout.addWidget(self.labelTRIGGER)
        self.H1SubV2H3Layout.addWidget(self.comboTRIGGER)
        self.H1SubV2H5Layout.addWidget(self.saveIncTimeCheck)
        self.H1SubV2H5Layout.addWidget(self.saveLogCheck)
        self.H1SubV2H5Layout.addWidget(self.saveLogButt)
        self.H1SubV2H5Layout.addWidget(self.toggleThemeButt)
        self.H1SubV2H6Layout.addWidget(self.labelRATIO)
        self.H1SubV2H6Layout.addWidget(self.inputTickToMsBox)
        self.H1SubV2H7Layout.addWidget(self.labelMaxTickCount)
        self.H1SubV2H7Layout.addWidget(self.inputMaxTickCount)
        
        self.H1SubV2Layout.addWidget(self.labelMeasure)
        self.H1SubV2Layout.addLayout(self.H1SubV2H1Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H2Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H3Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H4Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H5Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H6Layout)
        self.H1SubV2Layout.addLayout(self.H1SubV2H7Layout)
        self.H1SubV2Layout.addStretch()
        
        self.H1layout.addLayout(self.H1SubV1Layout)
        self.H1layout.addStretch()
        self.H1layout.addLayout(self.H1SubV2Layout)
        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addStretch()
        self.Vlayout.addWidget(self.saveConfigButt)
        self.dockContents.setLayout(self.Vlayout)  
    
    # -- ! We need callbacks to update the actual Values ! --#
    
    #---CREATE COMBOBOX Callbacks---#
    ## CB: comboCOM // Serial COM-Port
    def comboComChanged(self):
        self.snifferConfig.configCom = self.COMList[self.comboCOM.currentIndex()]
        self.logger.logEvent('changed COM-Port to - '+ self.snifferConfig.configCom)  
    ## CB: comboBAUD // Serial BAUD-Rate  
    def comboBaudChanged(self):
        self.snifferConfig.configBaud = self.comboBAUD.currentText()
        self.logger.logEvent('changed BAUD-Rate to - '+ self.snifferConfig.configBaud)
    ## CB: comboSTOP // Serial STOP-bit count
    def comboStopBitsChanged(self):
        self.snifferConfig.configStopBits = self.STOPList[self.comboSTOP.currentIndex()]
        self.logger.logEvent('changed STOP-Bits to - '+ self.snifferConfig.configStopBits) 
    ## CB: comboPARTIY // Serial Parity-bit (odd/even/none)   
    def comboParityChanged(self):
        self.snifferConfig.configParity = self.PARITYList[self.comboPARITY.currentIndex()]
        self.logger.logEvent('changed PARITY to - '+ self.snifferConfig.configParity)   
    ## CB: comboMODE // Measurement mode
    def comboModeChanged(self):
        # Check which box is checked in order to show the user the necessary info
        self.snifferConfig.configMode = self.MODEList[self.comboMODE.currentIndex()]
        if self.snifferConfig.configMode == self.MODEList[0]:
            self.inputSingleDurBox.show()
            self.labelSINGLETIME.show()
            self.comboTRIGGER.hide()
            self.labelTRIGGER.hide()
        if self.snifferConfig.configMode == self.MODEList[1]:
            self.inputSingleDurBox.hide()
            self.labelSINGLETIME.hide()
            self.comboTRIGGER.hide()
            self.labelTRIGGER.hide()
        if self.snifferConfig.configMode == self.MODEList[2]:
            self.inputSingleDurBox.show()
            self.labelSINGLETIME.show()
            self.comboTRIGGER.show()
            self.labelTRIGGER.show()
        self.logger.logEvent('changed Measurement-mode to - '+ self.snifferConfig.configMode)
    ## CB: comboTRIGGER // the Trigger the measurement waits for (only in TRIGGER-measmode)
    def comboTriggerChanged(self):
        self.snifferConfig.configTrigger = self.TRIGGERList[self.comboTRIGGER.currentIndex()]
        self.logger.logEvent('changed TriggerType to - '+ self.snifferConfig.configTrigger)
    
    #---CREATE THEME Callbacks---#    
    ## CB: Toggles the theme between dark and light mode
    #  @details This happens by calling the appropriate function of the parent (QMainwindow), so that the theme
    #  is changed globally
    def toggleTheme(self):
        if(self.snifferConfig.configCurrentTheme == 'Light'):
            self.parent.loadTheme('Dark')
            #self.parent.tabStart.startStopAnalyzingButt.setStyleSheet('QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: #31363b; border-radius:100px}')
        else:
            self.parent.loadTheme('Light')
            #self.parent.tabStart.startStopAnalyzingButt.setStyleSheet('QPushButton:focus {border: 2px solid; border-color: limegreen; background-color: white; border-radius:100px}')
        #self.parent.setStartStopButtonStyle()   
    
    #---CREATE CHECKBOX Callbacks---#   
    ## CB: Handle the SaveLog checkbox event (Toggle)
    def checkSaveLogChanged(self):
        self.snifferConfig.configLogCheck ^= 1  
        if(self.snifferConfig.configLogCheck == 1):   
            self.logger.enableLogs()   
        else:
            self.logger.disableLogs()
        self.logger.logEvent('changed LogCheckbox to - '+ str(self.snifferConfig.configLogCheck))
        
    ## CB: Handle the SaveInctime checkbox event (Toggle)         
    def checkSaveInctimeChanged(self):
        self.snifferConfig.configIncTimeCheck ^= 1 
        self.logger.logEvent('changed Save Time-Increment Checkbox to - '+ str(self.snifferConfig.configIncTimeCheck))

    #---CREATE LINEEDIT Callbacks---#
    ## CB: Handle the SingleDur lineedit callback (adjust singleshot duration)        
    def lineSingleDurChanged(self):
        self.snifferConfig.configSingleDurLine = self.inputSingleDurBox.text()
        self.logger.logEvent('changed Singleshot Duration to - '+ str(self.snifferConfig.configSingleDurLine))
        
    ## CB: Handle the TickToMs lineedit callback (adjust ticks per ms)       
    def lineTickToMsChanged(self):
        self.snifferConfig.configTickToMsLine = self.inputTickToMsBox.text()
        self.logger.logEvent('changed Tick To Ms Ratio to - '+ str(self.snifferConfig.configTickToMsLine))

    ## CB: Handle the MaxTickCount lineedit callback (adjust maximum tickcount value)
    def lineMaxTickCountChanged(self):
        self.snifferConfig.configMaxTickCountVal = self.inputMaxTickCount.text()
        self.logger.logEvent('changed Max Tickcount Value to - '+ str(self.snifferConfig.configTickToMsLine))
    
    #---CREATE PUSHBUTTON Callbacks---#    
    ## CB: Handle the refreshCOM pushbutton callback (refresh all com-ports)      
    def refreshCom(self):
        self.COMList = OsSniffer.OS_SerialPortList()
        self.comboCOM.clear()
        self.comboCOM.addItems(self.COMList)
        self.snifferConfig.configCom = self.COMList[self.comboCOM.currentIndex()]
      
    #---CONTENT FUNCTIONS---#
    ## CB: Saves all logs saved in the logList to a output-file
    def saveLog(self):
        print('Trying to save logs')
        if(len(snifferLogList) == 0):
            self.displayException('Global Logging List empty. Did you enable the checkbox?')
        else:
            self.saveLogDirectory, self.purge = QFileDialog.getSaveFileName(self, 'Save File', '', 'Logfile (*.slog)')
            print(self.saveLogDirectory)
            self.logFile = open(self.saveLogDirectory,'a+')
            for logTuple in snifferLogList:
                self.logFile.write(str(logTuple[0])+', '+str(logTuple[1])+'\n')
            self.logFile.close()
            
    # --- MANDATORY UI FUNCTIONS --- #
    # -------------------------------#
    ## Read out all components of snifferConfig and set the UI elements according to
    #  the saved values.           
    def syncUiToConfig(self):
        self.inputSingleDurBox.setText(str(self.snifferConfig.configSingleDurLine))
        self.inputTickToMsBox.setText(str(self.snifferConfig.configTickToMsLine))
        self.inputMaxTickCount.setText(str(self.snifferConfig.configMaxTickCountVal))
        
        self.saveLogCheck.setChecked(self.snifferConfig.configLogCheck)
        self.saveIncTimeCheck.setChecked(self.snifferConfig.configIncTimeCheck)
        try:
            self.comboCOM.setCurrentIndex(self.COMList.index(self.snifferConfig.configCom))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboCOM - snifferConfig Error')
            self.comboCOM.setCurrentIndex(0)
        try:
            self.comboMODE.setCurrentIndex(self.MODEList.index(self.snifferConfig.configMode))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboMODE - snifferConfig Error')
            self.comboMODE.setCurrentIndex(0)
        try:
            self.comboBAUD.setCurrentIndex(self.BAUDList.index(str(self.snifferConfig.configBaud)))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboBAUD - snifferConfig Error')
            self.comboBAUD.setCurrentIndex(0)
        try:
            self.comboPARITY.setCurrentIndex(self.PARITYList.index(self.snifferConfig.configParity))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboPARITY - snifferConfig Error')
            self.comboPARITY.setCurrentIndex(0)
        try:
            self.comboSTOP.setCurrentIndex(self.STOPList.index(str(self.snifferConfig.configStopBits)))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboSTOP - snifferConfig Error')
            self.comboSTOP.setCurrentIndex(0)
        try:
            self.comboTRIGGER.setCurrentIndex(self.TRIGGERList.index(self.snifferConfig.configTrigger.upper()))
        except Exception as valException:
            print('Exception when syncing UI in Configtab: comboTRIGGER - snifferConfig Error')
            self.comboTRIGGER.setCurrentIndex(0)
        