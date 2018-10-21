from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.Qt import QTextEdit, QWebEngineSettings
from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets
import os
from TraceDocks import TraceDocks
from SnifferLogger import SnifferLogger

## @package InstructionsTab
# InstructionTab shows instructions on how to use the Tracer
# or how to implement new tabs.

## The actual implementation of the InstructionsTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on
class InstructionsTab(TraceDocks):
    
    ## The constructor
    #  initialize the super-class, assign a name and first configItems
    def __init__(self,parent):
        super(InstructionsTab, self).__init__(parent,'Instructions Tab')
        self.parent = parent
        self.tabName = 'InstructionsTab'
        self.logger = SnifferLogger(self.tabName)
        self.logger.logEvent('Creating Tab now'+ self.tabName)
        
    ## Create the visible UI    
    def setInstructionsTabLayout(self):
        
        # Create Instructions Tab --------------------###    
        # Create Layouts
        self.Vlayout = QVBoxLayout()
        #------------------------------------
        
        # Create scrollable TextBox
#         self.scrollArea = QScrollArea()
#         self.instructionBox = QTextEdit()
#         self.instructionBox.setText('<b>LOREM IPSUM DOLOR SIT AMET</b>')
#         self.instructionText=open(os.path.join(os.path.abspath(os.getcwd()),'resources','instructions','INSTRUCTIONS.html')).read()
#         self.instructionBox.setHtml(self.instructionText)
#         self.instructionBox.setReadOnly(True)
#         self.instructionBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.scrollArea.setWidgetResizable(True)
#         self.scrollArea.setWidget(self.instructionBox)
        PDFJS = 'file:///C:/Users/Expertelis/workspace_devel/TraceSniffer/pdfjs-1.10.100-dist/web/viewer.html'
        PDF = 'file:///C:/Users/Expertelis/workspace_devel/TraceSniffer/Documentation/Guides/userguide.pdf'
        self.scrollArea = QScrollArea()
        self.instructionBox = QtWebEngineWidgets.QWebEngineView()
        self.instructionBox.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        print(QtCore.QUrl().fromLocalFile(os.path.join(os.path.abspath(os.getcwd()),'Documentation','Guides','userguide.pdf')))
        #self.instructionBox.load(QtCore.QUrl.fromUserInput('%s?file=%s%s' % (PDFJS, PDF,'#disableWorker=true')))
        #self.instructionBox.load(QtCore.QUrl().fromLocalFile(os.path.join(os.path.abspath(os.getcwd()),'Documentation','Guides','userguide.html')))
        self.instructionBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.instructionBox)
        #------------------------------------
        self.Vlayout.addWidget(self.scrollArea)
        
        self.dockContents.setLayout(self.Vlayout)