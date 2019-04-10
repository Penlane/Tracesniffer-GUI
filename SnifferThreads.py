from PyQt5 import QtCore
import Globals
from PayloadData import PayloadData
from SnifferReader import SnifferReader
import queue

## @package SnifferThreads
#  SnifferThreads combine two types of thread-classes, which can be
#  created and executed independently, but work together in tandem.\n\n
#  First: SnifferQueueThread: Fill an internal queue as from the serial buffer as fast as we can in order to avoid congestion\n\n
#  Second: SnifferInterpretThread: Pop all queue elements individually and parse the binary data into payload objects, append
#  those objects to a global list. 

## The actual implementation SnifferInterpretThread class
#  @details This thread reads data as fast as possible from a the global queue
#  and uses the SnifferReader to parse the data to a payload and append it to the payloadList
class SnifferInterpretThread(QtCore.QThread):

    startInterpretationSignal = QtCore.pyqtSignal() # This signal gets called when the measurement has finished
    
    ## Kill the thread by setting the exit-parameter for the endless-loop
    #  and calling the quit-function 
    def kill(self):
        self.isReading = False
        self.quit()
        
    ## Stop the thread by setting the all exit-parameters in order for the
    #  endless loop to exit gracefully.             
    def stop(self):
        self.isReading = False
        self.isWaiting = False
        self.waitResetOn = False
        
    ## Constructor: Initialize the thread-object by assigning the corresponding parameter values.
    #  We need many parameters here, because we want to tailor the measurement to the user-config
    #  @param singleshotTime the time the thread is allowed to run if the mode is in singleshot or after a trigger has been found
    #  @param timeByteCount the amount of time bytes sent by the Tracer - configured by the user
    #  @param triggerOn indication whether or not the thread needs to wait for a specific trigger
    #  @param selectedTrigger the selected trigger, user-defined
    #  @param saveIncTime indication whether or not to save Increment-tick packets, because they might fill up the table needlessly
    def __init__(self, singleshotTime, timeByteCount, triggerOn, selectedTrigger, saveIncTime, parent=None):
        super(SnifferInterpretThread, self).__init__(parent)
        self.singleshotTime = singleshotTime
        self.timeByteCount = timeByteCount
        self.triggerOn = triggerOn
        self.saveIncTime = saveIncTime
        self.selectedTrigger = selectedTrigger
        self.failCnt = 0
        self.waitCnt = 0
        self.snifferCnt = 0
        # TODO: Currently, the timeout is a fixed value, we need to be able
        # to adjust this
        self.timeOut = 100000
        self.isReading = True
        self.isWaiting = True
        self.killme = False
        Globals.payloadList.clear() # New measurement, old payloadList is cleared
        self.readPayload = PayloadData()
        
    ## Endless-loop of the thread. Takes an element out of the filled raw-byte queue and utilizes
    #  the SnifferReader to parse the binary data into payloads.
    #  Exit conditions: self.killme and self.isReading, which can be set by external functions
    def run(self):
        print(self.singleshotTime)
        # TODO: Improve Stop-handling
        self.mySnifferReader = SnifferReader(self.triggerOn)
        while (self.isReading):
            if(self.killme == True and Globals.serialQueue.empty()):
                print('ReaderThread: I received the stop-command, am stopping now')
                self.stop()
                self.startInterpretationSignal.emit()
                break
            try:
                # Get an element from the Queue
                self.byteBuffer = Globals.serialQueue.get(timeout = 1)
            except queue.Empty: # We were a little to fast, try again...
                continue
            # Build the payload. If a complete payload is built, it is appended to
            # the payloadlist by the SnifferReader instance.
            for b in self.byteBuffer:
                myPayload = self.mySnifferReader.read(bytes([b]))
                if self.triggerOn is True:
                    if hasattr(myPayload, 'payloadHead'):
                        if hasattr(myPayload.payloadHead, 'informationID'):
                            if myPayload.payloadHead.informationID == Globals.tspName2Id[self.selectedTrigger]:
                                self.triggerOn = False
                                self.mySnifferReader.triggerOn = False
                                self.mySnifferReader.process(myPayload)
                else:                  
                    if hasattr(myPayload, 'payloadHead'):
                        if hasattr(myPayload.payloadHead, 'informationID'):
                            if myPayload.payloadHead.informationID == 44: # We got a tick, so we increment the counter.
                                self.snifferCnt = self.snifferCnt + 1
                                print(self.snifferCnt)
                    if self.snifferCnt > self.singleshotTime: # Time to kill the thread
                        self.killme = True
        
        self.killme = True

## The actual implementation of SnifferQueueThread class
#  @details This thread reads data as fast as possible from the serialport-buffer (in order to reduce overflow chances)
#  and appends it to a global queue, which can then be interpreted.
class SnifferQueueThread(QtCore.QThread):
    
    ## Kill the thread by setting the exit-parameter for the endless-loop
    #  and calling the quit-function         
    def kill(self):
        self.isReading = False
        self.quit()
        
    ## Stop the thread by setting the all exit-parameters in order for the
    #  endless loop to exit gracefully.            
    def stop(self):
        self.isReading = False
        
    ## Constructor: Initialize the thread-object by assigning the corresponding parameter values.
    #  We need many parameters here, because we want to tailor the measurement to the user-config
    #  \n\n *WARNING! many of these parameters are obsolete, need to look at this*
    #  @param serialHandle the handle to our serial instance in order to read the time
    #  @param singleshotTime the time the thread is allowed to run if the mode is in singleshot or after a trigger has been found
    #  @param timeByteCount the amount of time bytes sent by the Tracer - configured by the user
    #  @param triggerOn indication whether or not the thread needs to wait for a specific trigger
    #  @param selectedTrigger the selected trigger, user-defined
    #  @param saveIncTime indication whether or not to save Increment-tick packets, because they might fill up the table needlessly        
    def __init__(self, serialHandle, singleshotTime, timeByteCount, triggerOn, selectedTrigger, saveIncTime, parent=None):
        super(SnifferQueueThread, self).__init__(parent)
        self.serialHandler = serialHandle
        self.singleshotTime = singleshotTime
        self.timeByteCount = timeByteCount
        self.triggerOn = triggerOn
        self.saveIncTime = saveIncTime
        self.selectedTrigger = selectedTrigger
        self.failCnt = 0
        self.waitCnt = 0
        # TODO: Fix timeout
        self.timeOut = 100000
        self.isReading = True
        self.killme = False
        Globals.serialQueue.queue.clear()
        
    ## Endless-loop of the thread. Puts the raw data read from the serialHandle into a 
    #  queue as fast as possible.
    #  Before starting, request the objectList by writing the corresponding ID.  
    #  Exit conditions: self.killme and self.isReading, which can be set by external functions
    def run(self):
        # TODO: Improve Stop-handling
#         self.serialHandler.write(b'\x98')
#         for _ in range(0,14):
#             self.serialHandler.write(b'\xff')
        self.serialHandler.write(bytes([Globals.tspName2Id['ID_OBJECT_LIST']]))
        while (self.isReading):
            if(self.killme == True):
                self.serialHandler.close()
                print('QueueThread: I received the stop-command, am stopping now')
                self.stop()
                break
            
            Globals.serialQueue.put(bytes(self.serialHandler.read(100)))

        self.killme = True