from datetime import datetime
import Globals

## @package SnifferLogger
#  SnifferLogger is a native logging system used by TraceSniffer.
#  It is mainly used to create simple eventlogs with a message and a timestamp
#  in order to debug what happens while the program is executing

## The actual implementation of the SnifferLogger class
class SnifferLogger:
    
    ## Constructor: create the SnifferLogger instance by assigning a name
    #  , setting the enabled status and creating a dummy Tuple
    def __init__(self,name):
        self.loggerName = name
        self.event = 'DummyEvent'
        self.logEnabled = False
        self.logTuple = ('Dummy1','Dummy2')
        
    ## Log an event by appending it with a timestamp to a global list, which can then be saved
    #  @param myEvent the cleartext string indicating what happened  
    def logEvent(self,myEvent):
        print(myEvent)
        if (self.logEnabled == True):
            self.logTuple = (myEvent,datetime.now().strftime("%H:%M - %d:%m:%Y"))
            Globals.snifferLogList.append(self.logTuple)
            
    ## Set the logstatus to enabled    
    def enableLogs(self):
        self.logEnabled = True
        
    ## Set the logstatus to disabled 
    def disableLogs(self):
        self.logEnabled = False