import Globals
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QLabel, QFileDialog, QComboBox
from TraceDocks import TraceDocks
from HardwareFilterWidget import HardwareFilter
from PayloadData import *

class CustomMarkerTab(TraceDocks):

    def __init__(self, parent):
        super(CustomMarkerTab, self).__init__(parent, 'Custom Marker Tab')
        self.tabName = self.name
        self.parent = parent

        self.logger.logEvent('Creating Tag now'+self.tabName)

        self.snifferConfig.configState = 'default'

        self.snifferConfig.parseConfigFromFile()

        self.payloadList = ['Payload0', 'Payload1', 'Payload2', 'Payload3', 'None']

    def setCustomerMarkerTabLayout(self):
        self.Vlayout = QVBoxLayout()
        self.H1layout = QHBoxLayout()
        self.H2layout = QHBoxLayout()
        self.H3layout = QHBoxLayout()
        self.H4layout = QHBoxLayout()
        self.H5layout = QHBoxLayout()

        self.label1 = QLabel(Globals.tspDict[73][0])
        self.label2 = QLabel(Globals.tspDict[74][0])
        self.label3 = QLabel(Globals.tspDict[75][0])
        self.label4 = QLabel(Globals.tspDict[76][0])
        self.label5 = QLabel(Globals.tspDict[77][0])

        self.comboCustomMarker1 = QComboBox()
        self.comboCustomMarker1.addItems(self.payloadList)
        self.comboCustomMarker1.currentTextChanged.connect(lambda: self.payloadChanged(self.label1.text()))

        self.comboCustomMarker2 = QComboBox()
        self.comboCustomMarker2.addItems(self.payloadList)  
        self.comboCustomMarker2.currentTextChanged.connect(lambda: self.payloadChanged(self.label2.text()))

        self.comboCustomMarker3 = QComboBox()
        self.comboCustomMarker3.addItems(self.payloadList)  
        self.comboCustomMarker3.currentTextChanged.connect(lambda: self.payloadChanged(self.label3.text()))

        self.comboCustomMarker4 = QComboBox()
        self.comboCustomMarker4.addItems(self.payloadList)  
        self.comboCustomMarker4.currentTextChanged.connect(lambda: self.payloadChanged(self.label4.text()))

        self.comboCustomMarker5 = QComboBox()
        self.comboCustomMarker5.addItems(self.payloadList)   
        self.comboCustomMarker5.currentTextChanged.connect(lambda: self.payloadChanged(self.label5.text()))

        self.comboBoxLookup = {
            Globals.tspDict[73][0]: self.comboCustomMarker1,
            Globals.tspDict[74][0]: self.comboCustomMarker2,
            Globals.tspDict[75][0]: self.comboCustomMarker3,
            Globals.tspDict[76][0]: self.comboCustomMarker4,
            Globals.tspDict[77][0]: self.comboCustomMarker5,
        }


        self.H1layout.addWidget(self.label1)
        self.H1layout.addWidget(self.comboCustomMarker1)

        self.H2layout.addWidget(self.label2)
        self.H2layout.addWidget(self.comboCustomMarker2)

        self.H3layout.addWidget(self.label3)
        self.H3layout.addWidget(self.comboCustomMarker3)

        self.H4layout.addWidget(self.label4)
        self.H4layout.addWidget(self.comboCustomMarker4)

        self.H5layout.addWidget(self.label5)
        self.H5layout.addWidget(self.comboCustomMarker5)


        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addLayout(self.H2layout)
        self.Vlayout.addLayout(self.H3layout)
        self.Vlayout.addLayout(self.H4layout)
        self.Vlayout.addLayout(self.H5layout)

        self.Vlayout.addStretch()

        self.dockContents.setLayout(self.Vlayout)

    def payloadChanged(self, marker):
        print(marker)
        print(self.comboBoxLookup[marker].currentText())
        if (self.comboBoxLookup[marker].currentText() == 'None'):
            Globals.tspDict[Globals.tspName2Id[marker]][1] = None
        else:
            Globals.tspDict[Globals.tspName2Id[marker]][1] = PayloadLookup[self.comboBoxLookup[marker].currentText()]
        print(Globals.tspDict)