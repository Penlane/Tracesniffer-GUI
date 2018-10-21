from Globals import *

import collections
from _collections import OrderedDict
import statistics
import traceback



## @package SnifferAPI
# SnifferAPI contains generic and tab-specific functions. For adaption of SnifferStats the specified functions can be consulted.
# rList is a shortcut for 'random list'
# tList is a shortcut for 'temporary list
# cLabel a shortcut for content label
class SnifferAPI():

    ## Checks if the id contains the object type given in the arguments.
    # @param id 
    # @param objType objectType
    # @return True or False 
    def isObjectType(self, id, objType):
        if id.contains(objType):
            return True
        else:
            return False


    ## Returns the amount of payload objects in the list
    # passed as parameter while excluding failed packets.
    # @param rList payloadList or filteredList or any other list
    # @param rDict global tspDict     
    # @return total count of payload objects
    def getAllPayloadCountWithoutFailed(self, rList, rDict):
        tList = []
        pcount = 0
        try: 
            for k, v in rDict.items():
                if(v[0].find('_FAILED') >= 0):
                    tList.append(k)
            for obj in rList:
                if(hasattr(obj, 'payloadHead')):
                    if(obj.payloadHead.informationID not in tList):
                        pcount += 1
        except Exception as e:
            print("Exception occurred: "+str(e))
        return pcount 
    
    
    ## Returns the amount of payload objects in the list
    # passed as parameter including failed packets.
    # @param rList payloadList or filteredList or any other list
    # @return total count of payload objects
    def getAllPayloadCountWithFailed(self, rList):
        pCount = 0
        try:
            for obj in rList:
                if(hasattr(obj, 'payloadHead')):
                    pCount += 1
        except Exception as e:
            print("Exception occurred: "+str(e))
        return pCount 
    
 
    ## Returns the amount of payload objects filtered by infoID in the list
    # passed as parameter.
    # @param rList payloadList or filteredList
    # @param infoID  informationID of packet
    # @return total count of payload objects with specified infoID  
    def getPayloadCountByID(self, rList, infoID):
        pCount = 0
        try:
            for obj in rList:
                if(hasattr(obj, "payloadHead")):
                    if(obj.payloadHead.informationID == infoID):
                        pCount += 1
        except Exception as e:
            print("Exception occurred: "+str(e))       
        return pCount
    
    
    ## Returns the object type of the payload object passed as parameter filtered by the internal object type 
    # This function is purposely coexistent to the above for comfort of usage.
    # @param obj global object
    # @return count of payload objects with specified packetID   
    def getPayloadByObjName(self, obj):
        if hasattr(obj, 'data1'):
            if hasattr(obj, 'data2'):
                if hasattr(obj, 'data3'):
                    return 3
                return 2
            return 1
        return 0 
    
                    
    ## This function filters global payload objects for payloadHead and appends the
    # filtered infoIDs to a new list. This function can be used to modify SnifferStats.
    # @param rList payloadList or filteredList
    # @return second list from the arguments with all informationIDs   
    def getAllInfoIDs(self, rList):
        rList2 = []
        try:
            for obj in rList:
                if(hasattr(obj,"payloadHead")):
                    rList2.append(obj.payloadHead.informationID)
        except Exception as e:
            print("Exception occurred: "+str(e))
        return rList2
    
    
    ## This function filters global payload objects for the infoID in the arguments and appends the
    # filtered tickCounts to a list. It calculates the difference in ticks between occurrences of that payload object (e.g. TASK_INCREMENT_TICK)
    # @param rList payloadList or filteredList
    # @param infoID informationID of object the user wants to scan
    # @return median of space between occurrence relative to the tick timebase 
    def getInfoIdTickCount(self, rList, infoID):
        tList2 = []
        tList = []
        try:
            for obj in rList:
                if(hasattr(obj,"payloadHead")):
                    if obj.payloadHead.informationID == infoID:
                        tList.append(obj.payloadHead.tickCountLow)
        except Exception as e:
            print("Exception occurred: "+str(e))
        try:
            for i, val in enumerate(tList):
                if(tList[i+1] <= len(tList) and tList[i+1] > tList[i]):
                    diff = tList[i+1] - tList[i]
                    tList2.append(diff)
                    if(tList[i+1] <= len(tList) and tList[i+1] < tList[i]):
                        diff = tList[i] - tList[i+1]
                        tList2.append(diff)
        except IndexError as ierr:
            print("IndexError"+str(ierr))
        return statistics.median(tList2)
    
    
    ## Counts identical informationIDs of the list given as the first parameter
    # This function can be further used to modify SnifferStats table.
    # @param rList payloadList or filteredList
    # @return counted infoIDs as dictionary in descending order from the collections module
    def getCountedInfoIDs(self, rList):
        try:
            counter = collections.Counter(rList)
            return OrderedDict(counter.most_common())
        except Exception as e:
            print("Exception occurred: "+str(e))
            
    
    ## Returns a string containing the duration of the measurement.
    # Subtracting the two tickCounts of first and last element contained in global payloadlist will return a timedelta object
    # which can be converted to seconds, when radix is specified.
    # Note: datetime is not required for this distance
    # @param rList payloadList
    # @return measurement time as string     
    def getMeasurementTimeSingleShot(self, rList):
        try:
            if(hasattr(rList[-1],"payloadHead") and hasattr(rList[0],"payloadHead")):
                if(hasattr(rList[-1], "tickCountHigh")):
                    lastByte = (rList[-1].payloadHead.tickCountHigh << 8) + rList[-1].payloadHead.tickCountHigh
                    if(hasattr(rList[0], "tickCountHigh")):
                        firstByte = (rList[0].payloadHead.tickCountHigh << 8) + rList[0].payloadHead.tickCountLow
                        return round(((lastByte - firstByte)/1000)*60, 4)                    
                    else:
                        return abs(round(((lastByte - rList[0].payloadHead.timerByteLow)/1000)*60, 4)) 
                else:
                    return abs(round(((rList[-1].payloadHead.tickCountLow - rList[0].payloadHead.tickCountLow)/1000)*60, 4))
                #str(divmod((rList[-1].payloadHead.timerByteLow-rList[0].payloadHead.timerByteLow).total_seconds(), 60))
        except Exception as e:
            print("Exception occurred: "+str(e))
            print(traceback.format_exc())
            
            
    ## Generates a list with all object sizes in bytes and returns that list
    # Note: This function is only for designed for SingleShot-mode.
    # @param rList object list (either payLoadList or filteredList or any other list)
    # @return list containing different sizes
    def getSizeOfObjects(self, rList):
        tList = []
        try:
            for obj in rList:
                tList.append(self.getPayloadSize(obj))
            return tList 
        except Exception as e:
            print("Exception occurred: "+str(e))
    
    
    ## Returns the minimum of the sizes of elements in a List
    # Note: This function calls the API function getSizeOfObjects
    # @param rList payloadlist for instance
    # @return the minimum of the size list
    def getMinSizeOfList(self, rList):
        try:
            return (min(self.getSizeOfObjects(rList)))
        except Exception as e:
            ("Exception occurred, consider consulting exception of inner function all")


    ## Returns the maximum of the sizes of elements in a List
    # Note: This function calls the API function getSizeOfObjects
    # @param rList payloadlist for instance
    # @return the maximum of the size list
    def getMaxSizeOfList(self, rList):
        try:
            return (max(self.getSizeOfObjects(rList)))
        except Exception as e:
            print("Exception occurred, consider consulting exception of inner function all")
    
    
    ## Returns the infoID and the corresponding name of the element with the smallest packet size
    # @param rList payloadlist
    # @param rDict tspDict useable
    # @return tuple containing infoID and name
    def getInfoIdOfMinObj(self, rList, rDict):
        tDict = {}
        try:
            for obj in rList:
                if(hasattr(obj,"payloadHead")):
                    tDict[obj.payloadHead.informationID] = self.getPayloadSize(obj)
            k = min(tDict.items(), key=lambda x: x[1])[0]
        except Exception as e:
            print("Exception occurred: "+str(e))
        return (rDict[k][0], k)
    
    
    ## Returns the infoID and the corresponding name of the element with the largest packet size
    # @param rList payloadlist
    # @param rDict tspDict useable
    # @return tuple containing infoID and name
    def getInfoIdOfMaxObj(self, rList, rDict):
        tDict = {}
        try: 
            for obj in rList:
                if(hasattr(obj,"payloadHead")):
                    tDict[obj.payloadHead.informationID] = self.getPayloadSize(obj)
            k = max(tDict.items(), key=lambda x: x[1])[0]
            return (rDict[k][0], k)  
        except Exception as e:
            print("Exception occurred: "+str(e))
  
    
    
    ## Returns all packetIDs in the list given as parameter
    # @param rList payloadlist
    # @return list of packetIDs
    def getPacketIDs(self, rList):
        tList = []
        try:
            maximum = max(rList)
            if sum(rList) != maximum * (maximum+1) /2 : 
                raise ValueError("non-consecutive packetIDs")
            if(len(rList) != len(set(rList))):
                raise ValueError("Duplicate packetIDs")
            for obj in rList:
                if(hasattr(obj, "payloadHead")):
                    tList.append(obj.payloadHead.packetID)
        except Exception as e:
            print("Exception occurred: "+str(e)+"\n")
            print(traceback.format_exc())
        except ValueError as err:
            print("Value Error was raised: "+err.args)
        return list(set(tList))
                
                
    ## Return the size of the list specified in the arguments in bytes
    # counts all payload0-payload3 objects and returns a byte-size for the entire measurement
    # Note This function is only for designed for SingleShot-mode.
    # @param rList (either payLoadList or filteredList or any other list)
    # @return size of list
    def getListSize(self, rList):
        size1 = 12
        size2 = 11
        size3 = 10
        size4 = 9
        cnt1 = 0
        cnt2 = 0
        cnt3 = 0
        cnt4 = 0
        try:
            for elem in rList:
                if self.getPayloadSize(elem) == 12:
                    cnt1 += 1
                elif self.getPayloadByObjName(elem) == 11:
                    cnt2 += 1               
                elif self.getPayloadByObjName(elem) == 10:    
                    cnt3 +=1  
                elif self.getPayloadSize(elem) == 9:
                    cnt4 += 1;
        except Exception as e:
            print("Exception occurred: "+str(e))
            print(traceback.format_exc())
        return cnt1*size1+cnt2*size2+cnt3*size3+cnt4*size4
    
    
    ## returns the size in bytes of the object passed as parameter
    # @param obj the payload object
    # @return size the object size
    def getPayloadSize(self, obj):
        if hasattr(obj, 'data1'):
            if hasattr(obj, 'data2'):
                if hasattr(obj, 'data3'):
                    return 12
                return 11
            return 10
        return 9 
    
    
    ## Generates a list with all object sizes in bytes 
    # and returns the sorted list in value-descending order
    # Duplicates are being summarized to one element.
    # This will always give the same result currently, since every payload has the same size.
    # This function is only for designed for SingleShot-mode.
    # @param rList object list (either payLoadList or filteredList)
    # @return sorted list in descending order
    def getSizeOfObjectsForTable(self, rList):
        tList = []
        try:
            for obj in rList:
                tList.append(self.getPayloadSize(obj))
            tList = list(set(tList))
            tList.sort(reverse = True)
        except Exception as e:
            print("Exception occurred: "+str(e))
        return tList


    ## Returns the count of task objects in the current sniff
    # This function can be further used to modify SnifferStats table.
    # @param rDict e.g the object_list (dictionary)
    # @return number of task objects    
    def getCountTaskObj(self, rDict):
        try:
            idx = 0
            for k, v in rDict.items():
                if (k == 'TASK'):
                    for k, v in rDict['TASK'].items():
                        idx +=1
        except Exception as e:
            print("Exception occurred: "+str(e))
        return idx
    
    
    ## Returns the count of non task objects in the current sniff
    # This function can be further used to modify SnifferStats table.
    # @param rDict e.g the object_list (dictionary)
    # @return number of non task objects      
    def getCountNonTaskObj(self, rDict):
        try:
            idx = 0
            for k, v in rDict.items():
                if(k != 'TASK'):
                    if(bool(rDict[k]) == True):
                        idx += 1
        except Exception as e:
            print("Exception occurred: "+str(e))
        return idx
    
    
    ## time for each marker should be previously 
    # received with time.time() or datetime.now(). 
    # By subtracting two datetime objects this operation will return a timedelta
    # object which can then be converted to seconds.
    # This function is only for suited for SingleShot-mode.
    # @param rList (either payLoadList or filteredList)
    # @return measurement time as string in kBit/second rounded to three decimal places
    def getDatarate(self, rList):
        try:
            tList = self.getSizeOfObjects(rList)
            time = self.getMeasurementTimeSingleShot(rList)
            if time:
                return round((((11/1000)*sum(tList))/(time)), 3)
        except Exception as e:        
            print("Exception occurred: "+str(e))
            print(traceback.format_exc())
    
    
    ## callback for when getPacketRate is executed
    # @param rList random list
    # @return measurement time as string in kBit/second  
    def PacketRateTimeout(self, rList):
        print("heres the action")
        return self.cnt
        
    
    ## time for each marker should be previously 
    # received with time.time() or datetime.now(). 
    # By subtracting two datetime objects this operation will return a timedelta
    # object which can then be converted to seconds.
    # This function is only for suited for SingleShot-mode.
    # @param rList (either payLoadList or filteredList)
    def getPacketRate(self, rList):
        try:
            from threading import Timer
            self.cnt = 0
            t = Timer(1*60, self.PacketRateTimeout)
            t.start()
            for elem in rList:
                self.cnt +=1
        except Exception as e:        
            print("Exception occurred: "+str(e))
        return 0
    
    
    ## Returns a list of all object types that occurred in the current trace
    # This function can be further used to modify SnifferStats table.
    # @param rDict e.g the object_list (dictionary)
    # @return list of all object types contained in the trace
    def getObjTypesList(self, rDict):
        tList = []
        try:
            for k1,v1 in rDict.items():
                if bool(v1) == True:
                    tList.append(k1);
            for k1,v1 in rDict.items():
                if k1 == 'TASK':
                    if bool(rDict[k1]) == True:
                        for k, v in rDict[k1].items():
                            tList.append(v)
        except Exception as e:        
            print("Exception occurred: "+str(e))
        
        ret = ", ".join( repr(e) for e in tList )
        return ret
    
    
    ## Returns the count of object occurred in the current trace specified by the argument parameter
    # This function can be further used to modify SnifferStats table.
    # @param rDict e.g the object_list (dictionary)
    # @param objType type to be searched for and counted
    # @return number of specific objType in the current trace   
    def getObjTypeOccurrence(self, rDict, objType):
        idx = 0
        try:
            for k, v in rDict.items():
                if (k == objType):
                    for k, v in rDict[objType].items():
                        if(bool(v) == True):
                            idx += 1
        except Exception as e:        
            print("Exception occurred: "+str(e))
        return idx
    
    
    ## Returns the count of all non task objects in the current sniff with their type as a key value pair
    # This function can be further used to modify SnifferStats table.
    # @param rDict e.g the object_list (dictionary)
    # @return Dictionary of non task objects with the count of occurrence
    def getCountWithObjName(self, rDict):
        tDict = {}
        idx = 0
        try:
            for k, v in rDict.items():
                if (bool(rDict[k]) == True):
                    if(k != 'TASK'):
                        for k1, v1 in rDict[k].items():
                            idx += 1
                        tDict[k] = idx
        except Exception as e:        
            print("Exception occurred: "+str(e))
        return tDict
    
## Get the object type for a payload object.
# @param payload in form of a payload object.
def getObjectType(payload):
    dPayload = payload.toDict()
    if 'DELAY' in Globals.tspDict[dPayload['payloadHead']['informationID']][0]:
        return 5
    if 'data1' and 'data2' in dPayload:
        return dPayload['data1']
    else:
        if 'TASK' in Globals.tspDict[dPayload['payloadHead']['informationID']][0]:
            return 5
        
## Get the datatype of a payload object specified as parameter.
# @param payload in form of a payload object. 
def getDataType(payload):
    if hasattr(payload, 'data1'):
        if hasattr(payload, 'data2'):
            if hasattr(payload, 'data3'):
                return 3
            return 2
        return 1
    return 0

## Check if the informationID of a payload is related to an Object
#  @param payload in form of a payload object.
def isRelatedToObject(payload):
    if Globals.tspDict[payload.payloadHead.informationID][2] is True:
        return True
    else:
        return False
    