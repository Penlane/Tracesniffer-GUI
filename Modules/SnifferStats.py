import Globals
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QDialog, QWidget, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QHeaderView
from PyQt5.Qt import QSizePolicy, QLabel, QTableWidget, QTableWidgetItem

from SnifferAPI import SnifferAPI
## @package SnifferStats
# SnifferStats gives an overview on relevant information regarding the previous measurement such as measurement time, total load size and table for object sizes

class SnifferStats(QDialog):
    
    
    ## The constructor.
    def __init__(self):
        super().__init__()
        
        self.iDList = []
        self.packetCount = 0
        self.counter = 0
        self.statsTableIndex = 0
        self.setWindowTitle('SnifferStats')
        self.snifferAPI = SnifferAPI()
        self.contentBox = QLabel()
        self.statsTable = QTableWidget()
        self.tabs = QTabWidget()
        self.tabBasic = QWidget()    
        self.tabAdvanced = QWidget()
        self.layout = QVBoxLayout()
        
        self.tabs.addTab(self.tabBasic,"Basic")
        self.tabs.addTab(self.tabAdvanced,"Advanced")
        self.tabBasic.layout = QVBoxLayout()
        self.tabAdvanced.layout = QVBoxLayout()
               
               
    ## Shows the stats in Label and Table (Basic and Advanced Tab).
    def showStats(self):
        self.clearTableStats()
        self.clearLabelStats()
        #-Advanced Tab
        self.iDList = self.snifferAPI.getAllInfoIDs(Globals.payloadList)
        self.counter = self.snifferAPI.getCountedInfoIDs(self.iDList)
        self.fillStatTable(Globals.payloadList, self.counter, self.statsTable, self.statsTableIndex)
        #-Basic Tab
        self.setBasicCount(self.contentBox, Globals.payloadList)
    
    
    ## Counts identical informationIDs of the list given as the first parameter
    #  and fills the StatTable in SnifferStats.
    #  This function can be further used to modify SnifferStats table.
    #  Note: This function requires access to the tspDict
    #  @param rList payloadList or filteredList
    #  @param counter as counted list
    #  @param statsTable member
    #  @param statsTableIndex variable
    def fillStatTable(self, rList, counter, statsTable, statsTableIndex):
        try: 
            for iD,amount in counter.items():
                statsTable.insertRow(statsTableIndex)
                statsTable.setItem(statsTableIndex, 0, QTableWidgetItem(Globals.tspDict[iD][0]))
                statsTable.setItem(statsTableIndex, 1, QTableWidgetItem(str(iD)))
                statsTable.setItem(statsTableIndex, 2,QTableWidgetItem(str(amount)))
                statsTableIndex = statsTableIndex + 1
            tList = self.snifferAPI.getSizeOfObjects(rList)
            statsTableIndex = 0
            for size in tList:
                statsTable.setItem(statsTableIndex, 3, QTableWidgetItem(str(size)))
                statsTableIndex = statsTableIndex + 1
        except Exception as e:
            print("Exception occurred: "+str(e))        
            
    ## Writes the PacketCount using getAllPayloadCount() to the label
    # specified as parameter
    # @param cLabel content label
    # @param rList payloadList or filteredList
    def setBasicCount(self, cLabel, rList):
        
        try:
            tList = self.snifferAPI.getSizeOfObjects(Globals.payloadList)
        
            myString = ("Total Packet Count (without failed): "+ str(self.snifferAPI.getAllPayloadCountWithoutFailed(Globals.payloadList, Globals.tspDict))+"\n"
            +"\nTotal Packet Count (all): "+ str(self.snifferAPI.getAllPayloadCountWithFailed(Globals.payloadList))+"\n"
            + "\nTotal load size: "+ str(self.snifferAPI.getListSize(Globals.payloadList))+"\n"
            + "\nMinimal packet size: "+str(self.snifferAPI.getMinSizeOfList(Globals.payloadList))+"\n"
            + "\nMaximal packet size: "+str(self.snifferAPI.getMaxSizeOfList(Globals.payloadList))+"\n"
            + "\nInfoID of minimal packet size: "+str(self.snifferAPI.getInfoIdOfMinObj(Globals.payloadList, Globals.tspDict)[0])
            +" ("+str(self.snifferAPI.getInfoIdOfMinObj(Globals.payloadList, Globals.tspDict)[1])+")\n"
            + "\nInfoID of maximal packet size: "+str(self.snifferAPI.getInfoIdOfMaxObj(Globals.payloadList, Globals.tspDict)[0])
            +" ("+str(self.snifferAPI.getInfoIdOfMaxObj(Globals.payloadList, Globals.tspDict)[1])+")\n"
            +"\nOccurrence of ID_MOVED_TASK_TO_READY_STATE: "+str(self.snifferAPI.getInfoIdTickCount(Globals.payloadList, 11))+" ticks \n" #id is here fix, group evaluates which types are most relevant
            +"\nCount of all non task objects : "+str(self.snifferAPI.getCountNonTaskObj(Globals.objectDict))+"\n"
            +"\nCount of task objects : "+str(self.snifferAPI.getCountTaskObj(Globals.objectDict))+"\n"
            +"\nAll objects: "+str(self.snifferAPI.getObjTypesList(Globals.objectDict))+"\n"
            +"\nTime of Measurement : "+str(self.snifferAPI.getMeasurementTimeSingleShot(Globals.payloadList))+" sec\n"
            +"\nAverage data rate : "+str(self.snifferAPI.getDatarate(Globals.payloadList))+" kbit/sec\n")
            cLabel.setText(myString)
        except Exception as e:
            print("Exception occurred: "+str(e))
     
    ## Sets the SnifferUI   
    def setSnifferStatsUi(self):
        self.setAdvancedTab()   
        self.setBasicTab()         
    
    
    ## Sets the Advanced Tab
    def setAdvancedTab(self):
        self.statsTableItem = QTableWidgetItem()
        self.statsTable.setRowCount(0)
        self.statsTable.setColumnCount(4)
        self.statsTable.setHorizontalHeaderLabels('InformationID;NumericID;Occurrence;PacketSize'.split(';'))
        self.statsTable.resizeColumnsToContents()
        self.statsTableHeader = self.statsTable.horizontalHeader()
        self.statsTableHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.statsTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        self.statsTableHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents) 
        self.statsTableHeader.setSectionResizeMode(3, QHeaderView.ResizeToContents) 
        self.closeButt = QPushButton('Clear')
        self.closeButt.clicked.connect(self.clearTableStats)     
        self.tabAdvanced.layout.addWidget(self.statsTable)
        self.tabAdvanced.layout.addWidget(self.closeButt)
        self.tabAdvanced.setLayout(self.tabAdvanced.layout)
        #------------------------------------
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    
    ## Sets the Basic Tab
    def setBasicTab(self):
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.contentBox)
        self.contentBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scrollArea.setWidgetResizable(True)
        self.closeButt = QPushButton('Clear')
        self.closeButt.clicked.connect(self.clearLabelStats) 
        self.tabBasic.layout.addWidget(self.scrollArea)
        self.tabBasic.layout.addWidget(self.closeButt)
        self.tabBasic.setLayout(self.tabBasic.layout)
        
    ## Clears the SnifferStats by calling an API function
    def clearTableStats(self):       
        self.deleteStats(self.iDList)
    
    
    ## Clears the SnifferStats by calling an API function
    def clearLabelStats(self):
        self.contentBox.clear()

    ## Clears the StatsView and resets according lists
    # @param list2 with all infoIDs (corresponding to second parameter in getAllInfoIDs()
    def deleteStats(self, list2):
        self.statsTable.setRowCount(0)
        self.statsTableIndex = 0
        self.counter = 0
        list2[:] = []