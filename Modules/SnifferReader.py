# -*- coding: utf-8 -*-
from PayloadData import *
import Globals

class SnifferReader(object):
    def __init__(self,triggerOn):
        self.preamble=bytes([0xFD,0xFE,0xFF])
        self.preamble_length=len(self.preamble)
        self.buffer=bytes()
        self.ringbuffer=bytes()
        self.payload_type=None
        self.data_valid=False
        self.triggerOn = triggerOn
        self.reset()
        
    def process(self,payload):
        gplist = Globals.payloadList
        if  self.triggerOn is False:
            try:
                lastPayload = Globals.payloadList[-1]
            except IndexError as err:
                print(err)
                Globals.payloadList.append(payload)
                return
            if payload.payloadHead.packetID > lastPayload.payloadHead.packetID+1:
                pID = lastPayload.payloadHead.packetID
                errPayload = {
                    "payloadHead": {
                        "packetID": pID,
                        "informationID": 149, # Start of error
                        "tickCountHigh": lastPayload.payloadHead.tickCountHigh,
                        "tickCountLow": lastPayload.payloadHead.tickCountLow,
                        "timerByteHigh": lastPayload.payloadHead.timerByteHigh,
                        "timerByteLow": lastPayload.payloadHead.timerByteLow
                    }
                }
                errPayloadStruct = PayloadData.fromDict(None, errPayload)
                Globals.payloadList.append(errPayloadStruct)
                while (payload.payloadHead.packetID > pID-1):
                    pID = pID + 1
                    if (pID > 255):
                        pID = 0
                    
                    # Build intermediary error payload
                    errPayload["payloadHead"]["packetID"] = pID
                    errPayload["payloadHead"]["informationID"] = 148 # Intermediary Error
                    errPayload["payloadHead"]["tickCountHigh"] = 0
                    errPayload["payloadHead"]["tickCountLow"] = 0
                    errPayload["payloadHead"]["timerByteHigh"] = 0
                    errPayload["payloadHead"]["timerByteLow"] = 0
                    errPayloadStruct = PayloadData.fromDict(None, errPayload)
                    
                    Globals.payloadList.append(errPayloadStruct)
                    
                # Build last Error payload
                errPayload["payloadHead"]["packetID"] = pID
                errPayload["payloadHead"]["informationID"] = 150 # End of error
                errPayload["payloadHead"]["tickCountHigh"] = payload.payloadHead.tickCountHigh
                errPayload["payloadHead"]["tickCountLow"] = payload.payloadHead.tickCountLow
                errPayload["payloadHead"]["timerByteHigh"] = payload.payloadHead.timerByteHigh
                errPayload["payloadHead"]["timerByteLow"] = payload.payloadHead.timerByteLow
                
                Globals.payloadList[-1] = PayloadData.fromDict(None, errPayload)
                Globals.payloadList.append(payload)
            else:
                Globals.payloadList.append(payload)
    # reset internal state
    def reset(self):
        self.current_id=None
        self.buffer=bytes()
        self.payload_type=None
        self.OLBuffer=bytes()
    # append binary data from object list to buffer
    def handle_object_list(self,data):
        self.OLBuffer+=data
    # parse object list binary buffer to class instance
    def finalize_OL(self):
        objectlist_header=ObjectListHeader.parse(self.OLBuffer)
        offset=ObjectListHeader.sizeof()
        print(objectlist_header)
        objtype_str=str(objectlist_header.objectType)
        Globals.objectDict[objtype_str]={}
        for _ in range(objectlist_header.length):
            namelen=ObjectNoName.parse(self.OLBuffer[offset:]).lenObjectName
            objStruct=makeObjectStruct(namelen)
            objData=objStruct.parse(self.OLBuffer[offset:])
            Globals.objectDict[objtype_str][str(objData.ObjectNumber)]=objData.objectName
            offset+=objStruct.sizeof()
        self.reset()
    
    ## read and accumulate data from serial port into packets
    # @param data data from serial port as byte-array
    # read data from serial connection
    # append to buffer and once the packet is complete
    # parse it and return a packet
    def read(self,data):
        if not len(data):
            return
        self.ringbuffer+=data
        self.ringbuffer=self.ringbuffer[-self.preamble_length:]

        if len(self.ringbuffer)>=self.preamble_length and self.ringbuffer[:self.preamble_length]==self.preamble:
            self.data_valid=True
            if self.OLBuffer: self.finalize_OL()
            self.reset()
            return

        if self.data_valid:
            self.buffer+=data
            if self.current_id==Globals.tspName2Id["ID_OBJECT_LIST"]:
                self.handle_object_list(data)
                return
            if len(self.buffer)==2:
                self.current_id=ord(data)
                if self.current_id==Globals.tspName2Id["ID_OBJECT_LIST"]:
                    self.OLBuffer=bytes()
                    self.OLBuffer+=self.buffer
            if len(self.buffer)==payloadHead.sizeof():
                BaseHeader=payloadHead.parse(self.buffer)
                if BaseHeader.informationID in Globals.tspDict.keys() and Globals.tspDict[BaseHeader.informationID][1]:
                    self.payload_type=Globals.tspDict[BaseHeader.informationID][1]
                else:
                    print('Invalid InformationID', BaseHeader.informationID)
                    self.data_valid=False
                    self.buffer=bytes()
                    self.payload_type=None
                    return False
            if self.payload_type and len(self.buffer)==self.payload_type.sizeof():
                Payload=self.payload_type.parse(self.buffer)
                self.reset()
                self.data_valid=False
                self.process(Payload)
                return Payload