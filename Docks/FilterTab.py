from PyQt5.QtWidgets import QVBoxLayout

from TraceDocks import TraceDocks
from HardwareFilterWidget import HardwareFilter

## @package FilterTab
# FilterTab filters the the packets via the connected microcontroller.
# It utilizes the TraceSnifferProtocol to filter single IDs.

## The actual implementation of the FilterTab class
#  It inherits from TraceDocks in order to receive different modules, like SnifferConfig, SnifferFilter and so on \n
#  It utilizes the hardwarefilter widget
class FilterTab(TraceDocks):
    
    ## The constructor
    #  initialize the super-class, assign a name and first configItems
    def __init__(self,parent):
        super(FilterTab, self).__init__(parent,'FilterTab')
        self.tabName = 'FilterTab'
        self.logger.logEvent('Creating Tab now: '+ self.tabName)
    
    ## Create the visible UI
    def setFilterTabLayout(self):
        # Create Filter Tab --------------------###    
        # Create Layouts
        self.Vlayout = QVBoxLayout()
        self.hwFilter = HardwareFilter()
        self.Vlayout.addWidget(self.hwFilter)
        self.dockContents.setLayout(self.Vlayout)