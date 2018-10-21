import queue
from ProtoSpec import *

## @package Globals
#  We need a couple of Global variables for a number of reasons. Explanation by field


# LEGACY: This tuple provides us with the ID-s where..actually need to ask Jonas
queueInfoTuple = (9, 10, 13, 14, 15, 16, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33)

# LEGACY: This tuple provides us with the names of the objects found in the objectList
queueEnum = ('Queue','Mutex','Counting Semaphore','Binary Semaphore','Recursive Mutex')

# This tuple provides us with the names of the IDs that are corresponding to memory
structEnum = ('MALLOC','FREE')

# --- READ ONLY!!
# This is the global payloadList. It is vital that this list is never modified
# unless a new measurement is started and the list is cleared and filled by the measurement thread
# For normal docks/tabs, this list is only for reading and building a local copy.
payloadList = []

# LEGACY: The queue used to store events fired between different docks / threads
communicationQueue = queue.Queue()

# -- Bool submodule
# In order to lookup all different variations of a bool 'true' or 'false',
# we need a couple of lookups and a lookupfunction
booleanFalse = ('0','False','FALSE','No')
booleanTrue = ('1','True','TRUE','Yes')
def getBoolValue(strval):
    if strval in booleanFalse:
        return False
    elif strval in booleanTrue:
        return True
    else:
        return False
    
# --- dock related --- #
# A list of all added docks. Automatically filled by inheriting from TraceDocks    
dockList = []
# REDUNDANT/LEGACY: A list of all dock-instances, rendered obsolete by the dockDict
dockInstanceList = []
# A lookup dictionary in order to associate a dockName with its instance
# Developers are encouraged to use the dockDict when communicating between docks.
dockDict = {}

# --- ui related --- #
# A global version-number to check for compatibility issues
versionNumber = 0.1

# A list of all events that were logged using the snifferLogger while
# the logCheckbox was enabled 
snifferLogList = []

# --- measurement related --- #

# --- READ ONLY!!!
# This dictionary stores the entire objectList in an easily accessible format
# and is the main interaction point between tracer-objects and their UI-side
# interpretation. Format: {ObjectType:{ObjectNo:cleartext-name,...},...}
objectDict = {}

# A simple lookup-dictionary for objectID -> cleartext objectType
objectTypeDict = {0:'QUEUE', 1:'MUTEX', 2:'COUNTING_SEMAPHORE', 3:'BINARY_SEMAPHORE', 4:'RECURSIVE_MUTEX', 5:'TASK'}

# A global counter for failed packets, used for debugging purposes
failedPacketCount = 0

serialQueue = queue.Queue()

globalFilter = 'kek'