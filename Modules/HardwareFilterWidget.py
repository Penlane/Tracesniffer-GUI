from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QSizePolicy
from PyQt5.Qt import QFont, QItemSelectionModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView
import Globals
import serial
import time

## @package HardwareFilter
#  A widget that interacts with the microcontroller in order to
#  filter the packets controller-sided 


## The actual implementation of the HardwareFilter class
class HardwareFilter(QWidget):
    
    ## The constructor  initialize superclass
    def __init__(self):
        super(HardwareFilter,self).__init__()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.layoutingComplete = False
        self.setUi()

    ## Create the Widget-Layout
    def setUi(self):
        self.H1layout = QHBoxLayout()
        self.Vlayout = QVBoxLayout()
        
        self.searchInputField = QLineEdit()
        self.searchInputField.setPlaceholderText('Enter search term, then click search')
        self.searchButt = QPushButton('Search Table')
        self.saveFilterButt = QPushButton('Send filter to device')
        
        self.saveFilterButt.clicked.connect(self.saveFilter) 
        self.searchButt.clicked.connect(lambda: self.searchInTable(self.searchInputField.text(),0))
        
        # Create Filter-Table
        self.filterTableIndex = 0
        self.filterTable = QTableWidget()
        self.filterTableItem = QTableWidgetItem()
        self.filterTable.setRowCount(0)
        self.filterTable.setColumnCount(2)
        
        self.filterTable.setHorizontalHeaderLabels('informationID;Enable'.split(';'))
        self.filterTable.resizeColumnsToContents()
        self.filterTableHeader = self.filterTable.horizontalHeader()
        self.filterTableHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        self.filterTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        
        font = self.getFont()
            
        self.checkBoxAllIds = self.createCheckBox()
        self.filterTable.itemChanged.connect(self.filterAllIDs)
        self.checkBoxAllMessages = self.createCheckBox()
        
        # -- Add first Row for all -- #
        self.filterTable.insertRow(self.filterTableIndex)
        idFilterItem = QTableWidgetItem('FILTER ALL IDs')
        idFilterItem.setFont(font)
        self.filterTable.setItem(self.filterTableIndex,0,idFilterItem)
        self.filterTable.setItem(self.filterTableIndex,1,self.checkBoxAllIds)
        self.filterTableIndex = self.filterTableIndex + 1
           
        # -- Add informationID filter rows -- #
        for keys, values in Globals.tspDict.items():
            if values[0].startswith('ID'):
                checkBoxFilter = self.createCheckBox()
                self.filterTable.insertRow(self.filterTableIndex)
                self.filterTable.setItem(self.filterTableIndex,0,QTableWidgetItem(values[0]))
                self.filterTable.setItem(self.filterTableIndex,1,checkBoxFilter)
                self.filterTableIndex = self.filterTableIndex + 1   
        
        self.H1layout.addWidget(self.searchInputField)
        self.H1layout.addWidget(self.searchButt)                
        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addWidget(self.filterTable)
        self.Vlayout.addWidget(self.saveFilterButt)
        #------------------------------------                                      
        self.setLayout(self.Vlayout)
        self.layoutingComplete = True
        
    def searchInTable(self, textToSearch, column):
        tableModel = self.filterTable.model()
        start = tableModel.index(0, column)
        matches = tableModel.match(start, Qt.DisplayRole, textToSearch, 1, Qt.MatchContains)
        if matches:
            index = matches[0]
            self.filterTable.selectionModel().select(
                index, QItemSelectionModel.Select)
            self.filterTable.scrollToItem(self.filterTable.itemFromIndex(index))
    
    ## Sends a series of filter packets to the controller based on TSP specification and 
    #  the user inputs on the filterTable. 
    def saveFilter(self):
        #--Save by ID--#
        rowCnt = self.filterTable.rowCount()
        # Document this later... no idea what I did there
        # I think it goes like this:
        # \n-> We go through the table and append a 1 to a string if a box is checked and a 0 if not
        # \n-> We convert this '10011011..' string to a series of bytes via TSP section XXX
        # \n-> We send to the filter byte-for-byte to the controller
        filterStr = ''
        for rows in range(1,rowCnt):                      
            if self.filterTable.item(rows,1).checkState() == Qt.Checked:
                #print(self.filterTable.item(rows,0).text())
                filterStr = filterStr + '1'
            else:
                filterStr = filterStr + '0'
        filterStr = filterStr.ljust(104,'1')
        concattedBytes = filterStr
        import re
        concattedBytes = re.findall('........', filterStr)    
        print(concattedBytes)
        byteList = []
        for byteStr in concattedBytes:
            byteList.append(bytes([int(byteStr[::-1],2)]))
        print(byteList)
        # Now we send the converted bytes over Serial interface
        try:
            self.serialHandle = serial.Serial(Globals.dockDict['dockConfig'].snifferConfig.configCom,int(Globals.dockDict['dockConfig'].snifferConfig.configBaud),timeout=3,parity=serial.PARITY_NONE,rtscts=False,dsrdtr=False)
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            return
                    
        self.serialHandle.write(b'\x98')
        time.sleep(0.00001) # We need to sleep because of the OS-hardware-buffer
        for bytesToSend in byteList:
            print(bytesToSend)
            self.serialHandle.write(bytesToSend)
            time.sleep(0.00001) # We need to sleep because of the OS-hardware-buffer
        self.serialHandle.write(b'\xff')
        self.serialHandle.write(b'\xff')
        self.serialHandle.close()
        
    ## Check whether the first checkbox was checked and then update the entire ID table to either checked or unchecked state
    #  @param checkBox a checkBox we perform the query on        
    def filterAllIDs(self,checkBox):
        if self.layoutingComplete == True:
            if checkBox.column() == 1 and checkBox.row() == 0: # We clicked the toggle ID checkbox
                if checkBox.checkState() == Qt.Checked:
                    rowCnt = self.filterTable.rowCount()
                    for rows in range(0,rowCnt):
                        try:
                            self.filterTable.item(rows, 1).setCheckState(Qt.Checked)
                        except AttributeError:
                            print('no items after' + str(rows)+ 'found...Maybe this column has less items than'+str(rowCnt)+'?')    
                elif checkBox.checkState() == Qt.Unchecked:
                    rowCnt = self.filterTable.rowCount()
                    for rows in range (0,rowCnt):
                        try:
                            self.filterTable.item(rows, 1).setCheckState(Qt.Unchecked)
                        except AttributeError:
                            print('no items after' + str(rows)+ 'found...Maybe this column has less items than'+str(rowCnt)+'?')    
                else:
                    print('neither checked nor unchecked...should never be here..')
            elif checkBox.column() == 3 and checkBox.row() == 0: # We clicked the toggle Message checkbox
                if checkBox.checkState() == Qt.Checked:
                    rowCnt = self.filterTable.rowCount()
                    for rows in range(0,rowCnt):
                        try:
                            self.filterTable.item(rows, 3).setCheckState(Qt.Checked)
                        except AttributeError:
                            print('no items after' + str(rows)+ 'found...Maybe this column has less items than'+str(rowCnt)+'?')    
                elif checkBox.checkState() == Qt.Unchecked:
                    rowCnt = self.filterTable.rowCount()
                    for rows in range (0,rowCnt):
                        try:
                            self.filterTable.item(rows, 3).setCheckState(Qt.Unchecked)
                        except AttributeError:
                            print('no items after' + str(rows)+ 'found...Maybe this column has less items than'+str(rowCnt)+'?')    
                else:
                    print('neither checked nor unchecked...should never be here..')
                    
    # --- HELPER FUNCTIONS --- #
    ## Create a defined checkbox within a tableWidgetItem to facilitate filling the table  
    #  @return the created checkbox                              
    def createCheckBox(self):
        myCheck = QTableWidgetItem()
        myCheck.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        myCheck.setCheckState(Qt.Checked)
        return myCheck  
     
    ## Create a defined font (bold,underlined) to facilitate filling the table
    #  @return the created font    
    def getFont(self):
        font = QFont()
        font.setBold(True)   
        font.setUnderline(True)  
        return font  