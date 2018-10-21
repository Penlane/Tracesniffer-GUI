import Globals
from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QTabWidget
from PyQt5.QtWidgets import QHeaderView
from PyQt5.Qt import QTableWidget, QTableWidgetItem, QTextEdit, QItemSelectionModel, QLineEdit, QFont
from PyQt5.QtCore import Qt
import re
from SnifferAPI import *
import SnifferAPI

## @package SnifferFilter
#  SnifferFilter is a dialog, the user can interact with in order to filter out
#  the Measurement results. The results can be filtered by either the ID or objectNames.
#  Currently, a distinction between local and global filter can be made, but the filter can be used
#  for all sorts of use-cases.


## The actual implementation of the SnifferFilter class
class SnifferFilter(QDialog):

    ## The constructor.
    #  Initialize lists to be filled with filtered payloads and
    #  create the dialog.
    def __init__(self,parent):
        super(SnifferFilter,self).__init__()
        self.parent = parent
        print('Initiating')
        self.setWindowTitle('SnifferFilter')
        self.filteredPayloadList = []
        self.filteredIdList = []
        self.layoutingComplete = False
        
        self.calledBy = 'NONE' # We store here which tab the filter belongs to, if there is no parent.(Like when the filter is global!)
        
        self.objectTabDict = {}
        self.filteredObjectDict = {}
        
        self.resize(670,700)
    
    ## Filters the global payloadList by ID by iterating through it and
    #  appending to a new list by filter-criteria
    #  @param filterList a list of IDs that are to be transferred to the new list
    def filterPayloadsByID(self,filterList):
        for payload in Globals.payloadList:
            if hasattr(payload, 'payloadHead'):
                if Globals.tspDict[payload.payloadHead.informationID][0] in filterList:
                    self.filteredPayloadList.append(payload)
                else:
                    #print('informationID is in filteredIdList, skipping packet')      
                    pass
                
    ## Filters the global payloadList by Message by iterating through it and
    #  appending to a new list by filter-criteria
    #  @param filterDict a dictionary of Key: ObjectType and Value: ObjectsToKeep as a template
    #  of which items are to be kept in the filteredList               
    def filterPayloadsByMessage(self,filterDict):
        localFilteredList = []
        for payload in self.filteredPayloadList:
            print('payloadID:'+str(payload.payloadHead.informationID))
            # If the ID has nothing to do with the object, we can safely add it.
            if payload.payloadHead.informationID is 23:
                x = 0
                pass
            if isRelatedToObject(payload):    
                for objType, messageID in filterDict.items():
                    print(Globals.objectTypeDict[getObjectType(payload)])
                    if Globals.objectTypeDict[getObjectType(payload)] == objType: # If the objectType matches the one in the dictionary
                        if objType == 0:
                            x = 0
                            pass
                        if getDataType(payload) == 2:
                            if payload.data2 not in messageID: # and the message does not match the dictionary
                                print('Passing data with msgid: '+str(payload.data2)) # don't append, but print that we skipped this one
                            else:
                                localFilteredList.append(payload) # the message does match the dictionary -> we want to keep it, so we add it to the list
                                
                        elif getDataType(payload) == 1:
                            if payload.data1 not in messageID:
                                print('Passing data with msgid: '+str(payload.data1))
                            else:
                                localFilteredList.append(payload)
                        else:                
                            localFilteredList.append(payload)
                    else:
                        # If the ID has nothing to do with the object, we can safely add it.
                        # Also, is the object is not even in the filterDict, we can add it too (this should not happen, but
                        # it's there for safety purposes
                        if getDataType(payload) == 0 or Globals.objectTypeDict[getObjectType(payload)] not in filterDict:
                            localFilteredList.append(payload)                 
            else:
                localFilteredList.append(payload)
                
        # In every other case, append it to the list, since we only want to filter out specific objects     
        self.filteredPayloadList = list(localFilteredList)  
                          
    ## Create the visible UI
    #  like the different tables, the searchbar etc.                                   
    def setSnifferFilterUi(self):

        self.filterTabs = QTabWidget()
        self.H1layout = QHBoxLayout()
        self.Vlayout = QVBoxLayout()
        
        self.searchInputField = QLineEdit()
        self.searchInputField.setPlaceholderText('Enter search term, then click search')
        self.searchButt = QPushButton('Search Table')
        self.saveFilterButt = QPushButton('Save Filter')
        self.filterTable = QTableWidget()
        
        self.saveFilterButt.clicked.connect(self.saveFilterList) 
        self.searchButt.clicked.connect(lambda: self.searchInTable(self.searchInputField.text(),0))
        
        # Create Table
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
        messageFilterItem = QTableWidgetItem('FILTER ALL Messages')
        messageFilterItem.setFont(font)
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
                  
        self.filterTabs.addTab(self.filterTable,'Information ID')
        
        self.H1layout.addWidget(self.searchInputField)
        self.H1layout.addWidget(self.searchButt)                
        self.Vlayout.addLayout(self.H1layout)
        self.Vlayout.addWidget(self.filterTabs)
        self.Vlayout.addWidget(self.saveFilterButt)
        #------------------------------------                                      
        self.setLayout(self.Vlayout)
        self.layoutingComplete = True
        
    ## Updates the visible filter UI to the new objectList
    #  This function is called, when either a new measurement was executed or an old measurement was loaded.
    #  Since the objects shown in the Filter need to be updated.
    def updateObjectFilter(self):
        # -- Add message filter rows -- #
        font = self.getFont()
        self.filterTabs.clear()
        self.filterTabs.addTab(self.filterTable,'Information ID')
        # For each object in objectList, create a new Table and add it to the tabs.
        for keys, values in Globals.objectDict.items():
            objectFilterTable = QTableWidget()
            objectFilterTable.setRowCount(0)
            objectFilterTable.setColumnCount(2)
            strSplit = keys+';Enable'
            objectFilterTable.setHorizontalHeaderLabels(strSplit.split(';'))
            objectFilterTable.resizeColumnsToContents()
            filterTableHeader = objectFilterTable.horizontalHeader()
            filterTableHeader.setSectionResizeMode(0, QHeaderView.Stretch)
            filterTableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
            checkBoxFilter = self.createCheckBox()
            
            objectFilterTable.itemChanged.connect(lambda *a,table=objectFilterTable: self.filterAllObjectIDs(*a,table=table))
            
            objectTableIndex = 0
            objectFilterTable.insertRow(objectTableIndex)
            objCat = QTableWidgetItem('FILTER ALL')
            objCat.setFont(font)
            objectFilterTable.setItem(objectTableIndex,0,objCat) 
            objectFilterTable.setItem(objectTableIndex,1,checkBoxFilter)
            objectTableIndex = objectTableIndex + 1 
            for keys2, values2 in values.items():
                objectFilterTable.insertRow(objectTableIndex)
                checkBoxFilter = self.createCheckBox()                
                objectFilterTable.setItem(objectTableIndex,0,QTableWidgetItem('ID: '+str(keys2)+' Name: '+str(values2)))
                objectFilterTable.setItem(objectTableIndex,1,checkBoxFilter)
                objectTableIndex = objectTableIndex + 1 
            
            # Add the newly create table to the tabs.
            self.filterTabs.addTab(objectFilterTable,keys)
            self.objectTabDict[keys] = objectFilterTable
    
    
    ## Searches the table for a string and scrolls to the found item.
    #  @param textToSearch the string that needs to be found in the table
    #  @param column the column where the search needs to take place                   
    def searchInTable(self, textToSearch, column):
        # Create a model of the table, so we can match a text
        tableModel = self.filterTable.model()
        start = tableModel.index(0, column)
        matches = tableModel.match(start, Qt.DisplayRole, textToSearch, 1, Qt.MatchContains)
        # If there are multiple matches, we take the first one, select it and scroll to it
        if matches:
            index = matches[0]
            self.filterTable.selectionModel().select(index, QItemSelectionModel.Select)
            self.filterTable.scrollToItem(self.filterTable.itemFromIndex(index))

    ## CB: SaveFilterButton // Call the filterFunctions -> Filter the unfiltered list by ID and Object and call the update
    #  function of the executing tab in order to update their UI.           
    def saveFilterList(self):
        self.filteredPayloadList.clear()
        
        #--Save by ID--#
        rowCnt = self.filterTable.rowCount()
        self.filteredIdList.clear()
        for rows in range(0,rowCnt):                      
            if self.filterTable.item(rows,1).checkState() == Qt.Checked:
                #print(self.filterTable.item(rows,0).text())
                self.filteredIdList.append(self.filterTable.item(rows,0).text())
        self.filterPayloadsByID(self.filteredIdList)
        print(len(self.filteredPayloadList))
        print(len(Globals.payloadList))
        
        #--Save By Objects--#
        self.filteredObjectDict.clear()
        for objType, objectTable in self.objectTabDict.items():
            rowCnt = objectTable.rowCount()
            objectsToFilter = []
            for rows in range(0,rowCnt):
                if objectTable.item(rows,1).checkState() == Qt.Checked:
                    #print(objectTable.item(rows,0).text())
                    try:
                        objectsToFilter.append(int(re.search('ID: (.*) Name:.*',objectTable.item(rows,0).text()).group(1)))
                        self.filteredObjectDict[objType] = objectsToFilter
                        #print('Found Regex: '+re.search('ID: (.*) Name:.*',objectTable.item(rows,0).text()).group(1))
                    except:
                        print('Error when parsing TableRegex...this is okay')
        self.filterPayloadsByMessage(self.filteredObjectDict)
            
        # We filtered the list, now we hide the windows and call the update-function
        # If the maintainer of the tab did not follow the implementation guide, there is no update-function to call.
        # We still save the filtered list, so we print a message to show where to find it.
        self.hide()
        try:
            self.parent.filterUpdated(self.filteredIdList,self.filteredPayloadList)
        except AttributeError:
            print('No corresponding callable function filterUpdated was found, you can access the most recent filteredList via self.snifferFilter.filteredIdList')
        try:
            Globals.dockDict[self.calledBy].filterUpdated(self.filteredIdList,self.filteredPayloadList)
        except:
            print('not global!')
            
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

    ## Check whether the first checkbox was checked and then update the entire ObjectIDtable to either checked or unchecked state
    #  @param checkBox a checkBox we perform the query on
    #  @param table the table that is to be updated        
    def filterAllObjectIDs(self,checkBox,table):
        if (self.objectTabDict):
                if checkBox.column() == 1 and checkBox.row() == 0: # We clicked the toggle ID checkbox
                    if checkBox.checkState() == Qt.Checked:
                        rowCnt = table.rowCount()
                        for rows in range(0,rowCnt):
                            try:
                                table.item(rows, 1).setCheckState(Qt.Checked)
                            except AttributeError:
                                print('no items after' + str(rows)+ 'found...Maybe this column has less items than'+str(rowCnt)+'?')    
                    elif checkBox.checkState() == Qt.Unchecked:
                        rowCnt = table.rowCount()
                        for rows in range (0,rowCnt):
                            try:
                                table.item(rows, 1).setCheckState(Qt.Unchecked)
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