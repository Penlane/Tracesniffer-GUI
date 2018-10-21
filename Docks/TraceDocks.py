# Global module, should be imported in every significant file
import Globals

# PyQt Imports
from PyQt5.QtWidgets import QWidget, QTabWidget, QMessageBox
from PyQt5.Qt import QDockWidget
from PyQt5.QtCore import Qt

# Sniffer-own Imports
from SnifferConfig import ConfigurationData
from SnifferFileParser import SnifferFileParser
from SnifferLogger import SnifferLogger
from SnifferFilter import SnifferFilter
from SnifferStats import SnifferStats

## @package TraceDocks
# TraceDocks is the baseclass for every other Tab in the program.
# It provides different modules to the inheriting tabs and offers a widget container
# for the tab contents.

## The actual TraceDocks class implementation
#  TraceDocks inherits from QDockWidget in order to provide the draggable functionality
class TraceDocks(QDockWidget):
    
    ## The constructor
    #  initialize the super-class, assign a dockName, set all surround UI elements and initialize
    #  all common dock modules 
    def __init__(self,TraceMain,name):
        super(QDockWidget, self).__init__(TraceMain)
        
        #self.dockWidget = QDockWidget(TraceMain)
        self.dockContents = QWidget(TraceMain)     # Create container
        
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.setWindowTitle(name) # set dockwidget title
        
        self.setWidget(self.dockContents) # add container to dockwidget
        
        TraceMain.addDockWidget(Qt.DockWidgetArea(Qt.TopDockWidgetArea), self) # add widget to dock
        TraceMain.setTabPosition(Qt.DockWidgetArea(Qt.TopDockWidgetArea), QTabWidget.TabPosition(QTabWidget.North))
        
        Globals.dockList.append(self) # Keep track of all docks
        
        if (len(Globals.dockList) > 1):
            for i,purge in enumerate(Globals.dockList):
                if i < len(Globals.dockList)-1:
                    TraceMain.tabifyDockWidget(Globals.dockList[i],Globals.dockList[i+1])
        
        self.parent=TraceMain # Set parent, so we can access the MainWindow (e.g themeChange)
        
        # Initialize all modules
        self.name = name   
        self.snifferConfig = ConfigurationData(self,name)
        self.snifferParser = SnifferFileParser()
        
        self.snifferFilter = SnifferFilter(self)
        self.snifferFilter.setSnifferFilterUi()
        
        self.snifferStats = SnifferStats()
        self.snifferStats.setSnifferStatsUi()
        self.logger = SnifferLogger(name)
        
    def displayException(self,myException):
        QMessageBox.about(self,'ERROR',myException)
        self.displayStatusMessage('Error occured: ' + myException)