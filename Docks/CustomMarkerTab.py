import Globals
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QLabel, QFileDialog, QComboBox
from TraceDocks import TraceDocks
from HardwareFilterWidget import HardwareFilter

class CustomMarkerTab(TraceDocks):

    def __init__(self, parent):
        super(CustomMarkerTab, self).__init__(parent, 'Custom Marker Tab')
        self.tabName = self.name
        self.parent = parent

        self.logger.logEvent('Creating Tag now'+self.tabName)

        self.snifferConfig.configState = 'default'

        self.snifferConfig.parseConfigFromFile()

        self.customMakerList = [Globals.tspDict[73][0], Globals.tspDict[74][0], Globals.tspDict[75][0], Globals.tspDict[76][0], Globals.tspDict[77][0]]

    def setCustomerMarkerTabLayout(self):
        self.Vlayout = QVBoxLayout()
        self.H1layout = QHBoxLayout()
        self.H2layout = QHBoxLayout()
        self.H3layout = QHBoxLayout()
        self.H4layout = QHBoxLayout()

        self.label1 = QLabel(Globals.tspDict[73][0])
        self.label2 = QLabel(Globals.tspDict[74][0])
        self.label3 = QLabel(Globals.tspDict[75][0])
        self.label4 = QLabel(Globals.tspDict[76][0])
        self.label5 = QLabel(Globals.tspDict[77][0])

        self.comboCustomMarker1 = QComboBox()
        self.comboCustomMarker1.addItems(self.customMakerList)

        self.comboCustomMarker2 = QComboBox()
        self.comboCustomMarker2.addItems(self.customMakerList)  

        self.comboCustomMarker3 = QComboBox()
        self.comboCustomMarker3.addItems(self.customMakerList)  

        self.comboCustomMarker4 = QComboBox()
        self.comboCustomMarker4.addItems(self.customMakerList)  

        self.comboCustomMarker5 = QComboBox()
        self.comboCustomMarker5.addItems(self.customMakerList)   

        self.event1Label = QLabel('Event1')
        self.event2Label = QLabel('Event2')
        self.event3Label = QLabel('Event3')
        self.startEndLabel = QLabel('Start-End')

        self.H1layout.addWidget(self.event1Label)
        self.H1layout.addWidget(self.comboCustomMarker1)

        self.H2layout.addWidget(self.event2Label)
        self.H2layout.addWidget(self.comboCustomMarker2)

        self.H3layout.addWidget(self.event3Label)
        self.H3layout.addWidget(self.comboCustomMarker3)

        self.H4layout.addWidget(self.startEndLabel)
        self.H4layout.addWidget(self.comboCustomMarker4)
        self.H4layout.addWidget(self.comboCustomMarker5)


        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addLayout(self.H2layout)
        self.Vlayout.addLayout(self.H3layout)
        self.Vlayout.addLayout(self.H4layout)

        self.Vlayout.addStretch()

        self.dockContents.setLayout(self.Vlayout)