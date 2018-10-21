import Globals
import json
from PayloadData import PayloadData

## @package SnifferFileParser
# SnifferFileParser is used for parsing all PayloadData type-independent from and to conforming JSON files.
# The files can be opened and viewed inside any JSON Editor.

## The actual implementation of the SnifferFilePaser class
class SnifferFileParser:
    ## Constructor
    def __init(self):
        print('losgehts')

    ## Saves all Entries from the global Payloadlist to the file specified in the arguments.
    # @param filename clear Path filename where the JSON file is to be stored       
    def saveToFile(self,filename):
        with open(filename,'w+') as f:
            dd = {}
            if isinstance(Globals.payloadList,list):
                realPayloadList = []
                for items in Globals.payloadList:
                    realPayloadList.append(items.toDict())
                for idx, n in enumerate(realPayloadList):
                    j_obj = n
                    dd['PayloadNumber'+str(idx).zfill(7)] = j_obj
                md = {'SnifferPayload':dd,'SnifferVersion':Globals.versionNumber,'SnifferObjectList':Globals.objectDict}
                json.dump(md,f, indent=2, sort_keys=True, skipkeys=True, separators=(',', ': '))
                
    ## Load payloadList entries from a file into the Global payloadlist.
    # @param filename clear Path filename where the JSON file is to be stored                 
    def getFromFile(self,filename):
        with open(filename,"r") as f:
            data=json.load(f)
            if data['SnifferVersion']:
                version = data['SnifferVersion']
                
            if data['SnifferPayload']:
                payloadList=data['SnifferPayload']
                Globals.payloadList.clear()
                for payload in payloadList.values():
                    #print(payload)
                    myPayload = PayloadData.fromDict(None,payload)
                    #print(myPayload)
                    Globals.payloadList.append(myPayload)
            
            # If we saved an Objectlist, we need to make sure that all filters
            # are updated        
            if data['SnifferObjectList']:
                objectDict = data['SnifferObjectList']
                Globals.objectDict.clear()
                for keys, values in objectDict.items():
                    Globals.objectDict[keys] = values
                for keys, values in Globals.dockDict.items():
                    values.snifferFilter.updateObjectFilter()
                Globals.globalFilter.updateObjectFilter()