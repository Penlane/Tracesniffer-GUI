from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QTabWidget
from PyQt5.QtWidgets import QHeaderView
from PyQt5.Qt import QTableWidget, QTableWidgetItem, QTextEdit, QItemSelectionModel, QLineEdit, QFont
from PyQt5.QtCore import Qt
import sys
import os
from functools import partial
rootdir = sys.path[0]
## @package SnifferHelpDialog


## The actual implementation of the SnifferHelpDialog class
class SnifferHelpDialog(QDialog):

    ## The constructor.
    #  Initialize lists to be filled with filtered payloads and
    #  create the dialog.
    def __init__(self,parent):
        super(SnifferHelpDialog,self).__init__()
        self.parent = parent
        self.setWindowTitle('CHOOSE A FILE')
        self.pdfItems = ['UserGuide.pdf','ImplementationGuide_Frontend.pdf','ImplementationGuide_Tracer.pdf']
        print('Initiating HelpDialog')        
        self.resize(250,150)
    
                          
    ## Create the visible UI
    #  like the different tables, the searchbar etc.                                   
    def setSnifferHelpDialogUi(self):
        self.Vlayout = QVBoxLayout()                            
        self.setLayout(self.Vlayout)
        for pdfs in self.pdfItems:
            pb = QPushButton(pdfs[:-4])
            #pb.clicked.connect(lambda pdfs=pdfs:self.displayPDF(pdfs))
            pb.clicked.connect(partial(self.displayPDF,pdfs))
            self.Vlayout.addWidget(pb)
        self.layoutingComplete = True
        
    def displayPDF(self,pdfName):
        os.startfile(os.path.join(rootdir,'Documentation','Guides',pdfName))