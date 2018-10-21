from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets
import os
from TraceDocks import TraceDocks


## @package MemoryTab
# Stump implementation. Will show memory allocation later.

## The actual implementation of the MemoryTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on
class MemoryTab(TraceDocks):
    
    ## The constructor
    #  initialize the super-class, assign a name and first configItems    
    def __init__(self,parent):
        super(MemoryTab, self).__init__(parent,'Memory Tab')
        self.tabName = 'MemoryTab'
        self.parent = parent
        self.logger.logEvent('Creating Tab now'+ self.tabName)
        
    ## Create the visible UI
    def setMemoryTabLayout(self):
        
        # Create Memory Tab --------------------###
        # Create Layouts
        self.Vlayout = QVBoxLayout()
        self.H1layout = QHBoxLayout()
        self.H1layout.setSpacing(15)
        #------------------------------------
         
        # Create Widgets for H1layout
        # First buttons
        self.clearScreenButt = QPushButton('Clear Screen')
        self.stopDisplayButt = QPushButton('Stop Display')
         
        # Add Widgets to H1layout
        self.H1layout.addWidget(self.clearScreenButt)
        self.H1layout.addWidget(self.stopDisplayButt)
         
        # Create Browser
        self.memoryBrowser = QtWebEngineWidgets.QWebEngineView()
        self.memoryBrowser.load(QtCore.QUrl().fromLocalFile(os.path.join(os.path.abspath(os.getcwd()),'resources','img','launch.html')))
        #------------------------------------
         
        #self.tabMemoryVlayout.addLayout(self.tabMemoryH1layout)
        self.Vlayout.addWidget(self.memoryBrowser)
        self.dockContents.setLayout(self.Vlayout)
