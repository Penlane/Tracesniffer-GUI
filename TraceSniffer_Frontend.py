import sys
import os

# Append all directories to PythonPath
mypath = os.getcwd()
dirmodules = os.path.join(mypath,'Modules')
dirdocks = os.path.join(mypath,'Docks')
dirhelper = os.path.join(dirmodules,'helper')
sys.path.append(dirmodules)
sys.path.append(dirdocks)
sys.path.append(dirhelper)

import Globals
import re

#PyQt Imports
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer, QFile, QTextStream

#View Imports
from StartTab import StartTab
from ConfigTab import ConfigTab
from TableTab import TableTab
from InstructionsTab import InstructionsTab
from MemoryTab import MemoryTab
from PlotTab import PlotTab
from FilterTab import FilterTab

import SnifferConfig
from PayloadData import PayloadData
from SnifferFilter import SnifferFilter
from SnifferHelpDialog import SnifferHelpDialog
import qdarkstyle

## @package TraceSnifferMain
# The MainWindow of the entire UI

## The actual TraceSnifferMain class implementation
#  Inherits from QMainWindow. Initializes all TraceTab / TradeDock instances and is responsible
#  for global UI relevant functions like theming.
class TraceSnifferMain(QMainWindow):
    
    ## The constructor
    #  initialize the super-class, assign a title etc.
    def __init__(self):
        super().__init__()
        self. title = 'TraceSniffer'
        
        Globals.mainInstance = self
        
        # Create our global filter instance
        globalFilter = SnifferFilter(self)
        Globals.globalFilter = globalFilter
        Globals.globalFilter.setSnifferFilterUi()
        self.configLogCheck = False
        
        # Create our global HelpFile instance
        self.sniffHelpDialog = SnifferHelpDialog(self)
        self.sniffHelpDialog.setSnifferHelpDialogUi()
        
        # Create necessary variables
        self.logPayload = PayloadData()
        self.snifferCnt = 0
        self.failCnt = 0
        self.purge = 0
        self.configCurrentTheme = 'Dark'
        self.measurementIsRunning = 0
        self.snifferConfigData = SnifferConfig.ConfigurationData(self)
        
        # Create necessary Lists
        self.logList = []
        
        self.payloadListIndex = 0
        
        # Create necessary Timers
        self.serialTimer = QTimer()
        self.serialTimer.timeout.connect(self.serialDataTick)
        self.serialTimer.stop()
        
        # Instantiate all tabs
        self.initUI() 
        
        # Create Menubar
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.helpMenu = self.menuBar.addMenu('Help')
        
        # Create Action that are performed when clicked on the items
        self.openFileMenu = QAction('Open Measurement', self)
        self.openFileMenu.setShortcut('Ctrl+O')
        self.openFileMenu.setStatusTip('Open a measurement file')
        # Access openMeasurement from StartTab
        self.openFileMenu.triggered.connect(self.dockStart.openMeasurement)
        
        self.saveFileMenu = QAction('Save Measurement', self)
        self.saveFileMenu.setShortcut('Ctrl+S')
        self.saveFileMenu.setStatusTip('Save the most recent measurement to a file')
        # Access saveMeasurement from StartTab
        self.saveFileMenu.triggered.connect(self.dockStart.saveMeasurement)
        
        self.helpFileMenu = QAction('Show help', self)
        self.helpFileMenu.setShortcut('Ctrl+H')
        self.helpFileMenu.setStatusTip('Shows a document providing help')
        # TODO: For now, raise the helpTab, this will be changed in the future
        self.helpFileMenu.triggered.connect(self.openHelpDialog)
        
        self.fileMenu.addAction(self.openFileMenu)
        self.fileMenu.addAction(self.saveFileMenu)
        self.helpMenu.addAction(self.helpFileMenu)
        
        
           
    # Create the UI by adding all the docks we want.    
    def initUI(self):            
        self.statusBar().showMessage('Ready')
                
        self.setGeometry(400, 30, 1050, 950)
        self.setWindowTitle('TraceSniffer')    
        
        
        self.dockStart = StartTab(self)        
        self.dockStart.setStartTabLayout()
        Globals.dockInstanceList.append(self.dockStart)
        Globals.dockDict['dockStart'] = self.dockStart
        
        self.dockTable = TableTab(self)
        self.dockTable.setTableTabLayout()
        Globals.dockInstanceList.append(self.dockTable)
        Globals.dockDict['dockTable'] = self.dockTable
        
        #self.dockMemory = MemoryTab(self)
        #self.dockMemory.setMemoryTabLayout()
        #Globals.dockInstanceList.append(self.dockMemory)
        
        #self.dockInstructions = InstructionsTab(self)
        #self.dockInstructions.setInstructionsTabLayout()
        #Globals.dockInstanceList.append(self.dockInstructions)
        
        self.dockPlot = PlotTab(self)
        self.dockPlot.setPlotTabLayout()
        Globals.dockInstanceList.append(self.dockPlot)
        Globals.dockDict['dockPlot'] = self.dockPlot
        
        self.dockFilter = FilterTab(self)
        self.dockFilter.setFilterTabLayout()
        Globals.dockInstanceList.append(self.dockFilter)
        Globals.dockDict['dockFilter'] = self.dockFilter
        
        self.dockConfig = ConfigTab(self)    
        self.dockConfig.setConfigTabLayout()
        Globals.dockInstanceList.append(self.dockConfig)
        Globals.dockDict['dockConfig'] = self.dockConfig
        
        # Raise the startDock as the default dock
        self.dockStart.raise_()
        
        
        self.show() 
    
    ## Load a qdarkstyle theme or default theme
    #  @param setTheme the theme that is to be set ('Dark'/'Light')        
    def loadTheme(self,setTheme):
        if setTheme == 'Dark':
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            # sync Configs
            for _, docks in Globals.dockDict.items():
                docks.snifferConfig.configCurrentTheme = 'Dark'
        else:
            app.setStyleSheet('')
            # sync Configs
            for _, docks in Globals.dockDict.items():
                docks.snifferConfig.configCurrentTheme = 'Light'
            
    #-------------------------STATUS MESSAGE IMPLEMENTATIONS-------------------------#
    ## OBSOLETE
    def displayStatusMessage(self,myMessage):
        self.tabStart.displayStatusMessage(myMessage) # We wrap around here, because the statusbox is technically located in the StartTab.
        #self.statusBox.setText('Message: ' + myMessage)    
    
    ## OBSOLETE           
    def displayException(self,myException):
        QMessageBox.about(self,'ERROR',myException)
        self.displayStatusMessage('Exception occured: ' + myException)
        
    #-------------------------HELPER FUNCTION IMPLEMENTATIONS-------------------------#     
    
    ## Disable all buttons in all tabs    
    def disableButtons(self):
        for tabs in self.tabList:
            tabs.disableButtons()
        print('Disabled all Buttons on all Tabs')
    
    ## Enable all buttons in all tabs   
    def enableButtons(self):
        for tabs in self.tabList:
            tabs.enableButtons()
        print('Enabled all Buttons on all Tabs')
        
    ## Open a dialog in order to display all Help-Files and User-guides
    def openHelpDialog(self):
        self.sniffHelpDialog.show()
             
    #-------------------------TIMER AREA-------------------------#
    
    ## LEGACY: CB: serialTimer // communicates with the interpretation thread via the communication Queue
    def serialDataTick(self):
        if(Globals.communicationQueue.empty() == False):
            myEvent = Globals.communicationQueue.get()
            if(myEvent == 'FAILED_PACKET_DETECTED'):
                self.failCnt = self.failCnt+1
                self.displayStatusMessage('FAILED_PACKET Received! Careful! Count: '+str(self.failCnt))
            if(myEvent == 'TRIGGER_FOUND'):
                self.displayStatusMessage('Found a trigger, measuring now!')
            if(myEvent == 'RESET_RECEIVED'):
                self.displayStatusMessage('Received a RESET, starting my Measurement...')
                
## Only for debugging       
def early_excepthook(exctype, value, tb,start=False):
    try:
        import traceback
        msgBox = QMessageBox()
        msgBox.setWindowTitle("FEHLER!")
        msgBox.setText("".join(traceback.format_exception(exctype,value,tb)))
        msgBox.exec_()
    except: pass
                          

#----------QDARKPALETTE WAS REMOVED HERE. IF NEEDED GOOGLE IT ------------#
if __name__ == '__main__':
    configReg = re.compile(': (.*)')
    app = QApplication(sys.argv)
    file = QFile(":/dark.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ex = TraceSnifferMain()
    sys.excepthook = early_excepthook
    sys.exit(app.exec_())