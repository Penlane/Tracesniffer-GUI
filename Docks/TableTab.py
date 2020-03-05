#PyQt Imports
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QMessageBox, QHeaderView
from PyQt5.Qt import QTableWidget, QTableWidgetItem, QButtonGroup, QRadioButton, QLineEdit
from PyQt5.QtCore import Qt
from TraceDocks import TraceDocks
from SnifferAPI import *

## @package TableTab
# TableTab displays the opened measurement in a chronological order
# the table can be searched for special IDs and be reviewed for any measurement
# errors.

## The actual implementation of the TableTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on
class TableTab(TraceDocks):

    ## The constructor
    #  initialize the super-class, assign a name and first configItems
    def __init__(self,parent):
        super(TableTab, self).__init__(parent,'TableTab')
        self.tabName = 'TableTab'
        self.parent = parent
        self.logger.logEvent('Creating Tab now: '+ self.tabName)
        
        # Set a couple of default-values, in case the configParser does not work
        self.snifferConfig.configAutoClearCheck = 1
        self.snifferConfig.configFilterState = 'Local'
        self.snifferConfig.configFilterList = self.snifferFilter.filteredIdList
        
        # By parsing the config now, we assure that we re-load everything
        # the way we left it
        self.snifferConfig.parseConfigFromFile()
        
        self.lastSearchedText = 'nullthiswillneverbefound'
        self.lastMatch = 'purge'
        self.lastIndex = 0

    ## Create the visible UI
    def setTableTabLayout(self):
        
        # Create Table Tab --------------------###    
        # Create Layouts
        self.Vlayout = QVBoxLayout()
        self.H1layout = QHBoxLayout()
        self.H11layout = QHBoxLayout()
        self.H12layout = QHBoxLayout()
        self.H21layout = QHBoxLayout()
        self.V11layout = QVBoxLayout()
        self.V21layout = QVBoxLayout()
        
        # Create Widgets for H1layout
        # First buttons
        self.clearTableButt = QPushButton('Clear Table')
        self.clearTableButt.clicked.connect(self.clearTable)
        self.autoClearCheck = QCheckBox('Auto Clear')
        self.autoClearCheck.stateChanged.connect(self.checkAutoClearChanged)  
        
        self.searchInputField = QLineEdit()
        self.searchInputField.setPlaceholderText('Enter search term, then click search')
        self.searchButt = QPushButton('Search Table')
        self.searchButt.clicked.connect(lambda: self.searchInTable(self.searchInputField.text(),2))
        self.showSummaryButt = QPushButton('Show Summary')
        self.showSummaryButt.clicked.connect(self.showSummary)
         
        self.filterGroup = QButtonGroup()
        self.localFilterRadio = QRadioButton('Local',self)
        self.globalFilterRadio = QRadioButton('Global', self)
        self.configureFilterButt = QPushButton('Configure Filter')
        self.configureFilterButt.clicked.connect(self.configureFilter)
        self.localFilterRadio.clicked.connect(self.localRadioSelected)
        self.globalFilterRadio.clicked.connect(self.globalRadioSelected)
        
        self.H21layout.addWidget(self.localFilterRadio)
        self.H21layout.addWidget(self.globalFilterRadio)
        self.H21layout.addWidget(self.showSummaryButt)
        self.V21layout.addLayout(self.H21layout)
        self.V21layout.addWidget(self.configureFilterButt)
        
        # Add Widgets to H11layout
        self.H11layout.addWidget(self.clearTableButt)
        self.H11layout.addWidget(self.autoClearCheck)
        
        # Add Widgets to H12layout
        self.H12layout.addWidget(self.searchInputField)
        self.H12layout.addWidget(self.searchButt)
        self.H12layout.addStretch()
        
        self.V11layout.addLayout(self.H11layout)
        self.V11layout.addLayout(self.H12layout)
        
        self.H1layout.addLayout(self.V11layout)
        self.H1layout.addLayout(self.V21layout)
        
        self.syncUiToConfig()
        #------------------------------------
        
        # Create Table
        self.detailTableIndex = 0
        self.detailTable = QTableWidget()
        self.detailTableItem = QTableWidgetItem()
        self.detailTable.setRowCount(0)
        self.detailTable.setColumnCount(6)
        
        self.detailTable.setHorizontalHeaderLabels('packID;Tick;Timer;Type;Message;Length'.split(';'))
        self.detailTable.resizeColumnsToContents()
        self.detailTableHeader = self.detailTable.horizontalHeader()
        self.detailTableHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.detailTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)        
        self.detailTableHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.detailTableHeader.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.detailTableHeader.setSectionResizeMode(4, QHeaderView.Stretch)
        self.detailTableHeader.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        #------------------------------------                                      
        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addWidget(self.detailTable)
        
        self.dockContents.setLayout(self.Vlayout) 
        
         
    ## Fill the main table with the entries from the given list
    #  @param fillTableList the list which is to be parsed into the table        
    def fillTable(self,fillTableList):
        print('Filling Table with all items in PayloadList')
        self.detailTable.scrollToTop() # Scrolls to the top of the table
        self.configAutoClearCheck = True
        if self.configAutoClearCheck == True:
                self.detailTable.setRowCount(0)
                self.detailTableIndex = 0
        Globals.dockDict['dockStart'].progressShotBar.setMaximum(len(Globals.payloadList))
        for self.tablePayload in fillTableList:
            self.detailTable.insertRow(self.detailTableIndex)
            self.detailTable.setItem(self.detailTableIndex,0,QTableWidgetItem(str(self.tablePayload.payloadHead.packetID)))
            self.detailTable.setItem(self.detailTableIndex,1,QTableWidgetItem(str(self.tablePayload.payloadHead.tickCountHigh << 8 | self.tablePayload.payloadHead.tickCountLow)))
            self.detailTable.setItem(self.detailTableIndex,2,QTableWidgetItem(str(self.tablePayload.payloadHead.timerByteHigh << 8 | self.tablePayload.payloadHead.timerByteLow)))
            self.detailTable.setItem(self.detailTableIndex,3,QTableWidgetItem(Globals.tspDict[self.tablePayload.payloadHead.informationID][0]))
            testPayload = self.tablePayload.toDict()
            
            # This a little messy: We check whether an objectDict is available, and if it is
            # we check for the different DataTypes there might be, since the message section is unified.
            # Basically, we need to handle all the different cases there can be, payload0-payload3 and the actual objectType
            if Globals.objectDict:
                if getDataType(self.tablePayload) == 1:
                    if getObjectType(self.tablePayload) == 5:
                        try:
                            self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.data1)+': '+Globals.objectDict['TASK'][str(self.tablePayload.data1)])) 
                        except:
                            self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem('FAILED WITH KEYERROR - see printOutput'))
                            print('KEYERROR DETAILS:')
                            print(testPayload)                                                                                      
                elif getDataType(self.tablePayload) == 2:
                    try:
                        self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.data1)+': '+Globals.objectDict[Globals.objectTypeDict[self.tablePayload.data1]][str(self.tablePayload.data2)]))
                    except:
                        self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem('FAILED WITH KEYERROR - see printOutput'))
                        print('KEYERROR DETAILS:')
                        print(testPayload)
            # If the objectDict does not exist, we can just dump the raw information into the message-section -> no lookup will be happening
            # and it is up to the user to interpret the data                                 
            else:
                if getDataType(self.tablePayload) == 1:
                    self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.data1)))
                elif getDataType(self.tablePayload) == 2:
                    self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.data1)+';'+str(self.tablePayload.data2)))
                elif getDataType(self.tablePayload) == 3:
                    self.detailTable.setItem(self.detailTableIndex,4,QTableWidgetItem(str(self.tablePayload.data1)+';'+str(self.tablePayload.data2)+';'+str(self.tablePayload.data3)))  

            self.detailTable.setItem(self.detailTableIndex,5,QTableWidgetItem('payload'+str(getDataType(self.tablePayload))))
            
            self.detailTableIndex+=1
            Globals.dockDict['dockStart'].progressShotBar.setValue(self.detailTableIndex)
        Globals.dockDict['dockStart'].progressShotBar.setValue(len(Globals.payloadList))
        Globals.dockDict['dockStart'].displayStatusMessage('Table filled completely, check the tab')
        self.lastSearchedText = 'thisisAWorkAround' # No idea why this is there...

    # --- DOCK-SPECIFIC UI FUNCTIONS --- #
    # -----------------------------------#  
      
    ## Disable all UI-buttons belonging to the tab. This is implementation specific                    
    def disableButtons(self):
        self.clearTableButt.setEnabled(False)
        self.autoClearCheck.setEnabled(False)
        print('Disable TabTable Buttons')
        
    ## CB: clearTableButton // Clear the main table        
    def clearTable(self):
        self.logger.logEvent('clear Table clicked')          
        self.detailTable.setRowCount(0)
        self.detailTableIndex = 0
           
    ## CB: autoClearCheckbox // set the configAutoClearCheck state according to the checkbox   
    def checkAutoClearChanged(self):
        self.snifferConfig.configAutoClearCheck ^= 1          
        self.logger.logEvent('changed Auto Clear Checkbox to - '+ str(self.snifferConfig.configAutoClearCheck))  
        
    ## CB: localRadioButt // set the configFilterState to 'Local'    
    def localRadioSelected(self):
        self.snifferConfig.configFilterState = 'Local'
        self.logger.logEvent('changed Filter Radio to - '+ str(self.snifferConfig.configFilterState))
        
    ## CB: globalRadioButt // set the configFilterState to 'Global'    
    def globalRadioSelected(self):
        self.snifferConfig.configFilterState = 'Global'
        self.logger.logEvent('changed Filter Radio to - '+ str(self.snifferConfig.configFilterState))
            
    ## CB: Show Stats // opens the Stat-Dialog to show misc. information about the measurement           
    def showSummary(self):
        self.snifferStats.show()
        self.snifferStats.showStats()  
        
    ## Searches the table for a string and scrolls to the found item.
    #  @param textToSearch the string that needs to be found in the table
    #  @param column the column where the search needs to take place   
    def searchInTable(self, textToSearch, column):
        if textToSearch not in Globals.IDList:
            QMessageBox.about(self,'Not Found','SearchText not Found!')
            return   

        
        if self.lastSearchedText == textToSearch:
            self.detailTable.setCurrentItem(self.lastFound[self.lastIndex])
            self.detailTable.scrollToItem(self.lastFound[self.lastIndex]) 
            self.lastIndex = self.lastIndex + 1
            if self.lastIndex == len(self.lastFound):
                self.lastIndex = 0
        else:
            foundItems = self.detailTable.findItems(textToSearch, Qt.MatchExactly)
            self.lastSearchedText = textToSearch
            if len(foundItems) != 0:
                self.lastFound = foundItems
                self.lastIndex = 1
                self.detailTable.setCurrentItem(foundItems[0])
                self.detailTable.scrollToItem(self.lastFound[self.lastIndex])


    # --- MANDATORY UI FUNCTIONS --- #
    # -------------------------------# 
             
    ## Read out all components of snifferConfig and set the UI elements according to
    #  the saved values.        
    def syncUiToConfig(self):
        self.autoClearCheck.setChecked(self.snifferConfig.configAutoClearCheck)
        if self.snifferConfig.configFilterState == 'Local':
            self.localFilterRadio.click()
        elif self.snifferConfig.configFilterState == 'Global':
            self.globalFilterRadio.click()
        else:
            print('Error, neither local nor global in config')

    ## Open the correct filter based on the radioButton. If the Global-filter is checked
    #  we assign its calledby variable in order to execute the right callback after the filter is saved.    
    def configureFilter(self):
        if self.localFilterRadio.isChecked():
            self.snifferFilter.show()
        elif self.globalFilterRadio.isChecked():
            Globals.globalFilter.show()
            Globals.globalFilter.calledBy = 'dockTable'
        else:
            print('neither radios checked. Error!')
                                 
    ## CB: // Updates the UI-contents with after filtering has taken place.
    #  This function should not be called by the tab itself, but by the filter
    #  @param filteredIDs the IDs that are to be kept in the payloadList (obsolete)
    #  @param filteredPayloads the new payloadList, which only contains the payloads filtered by the SnifferFilter                   
    def filterUpdated(self, filteredIDs, filteredPayloads):
        print('we arrive from SnifferFilter')
        self.clearTable()
        self.fillTable(filteredPayloads)