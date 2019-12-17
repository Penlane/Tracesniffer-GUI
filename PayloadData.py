from ProtoSpec import *
from construct import *
import Globals

##Function to convert Construct Class instance to and from dict
# Primarily used for data storage in JSON or XML format
def Payload2Dict(payload,d=None):
    if d is None:
        d={}
    for k,v in  payload.items():
        if k.startswith("_"): continue
        if isinstance(v,Container):
            d[k]={}
            Payload2Dict(v,d[k])
        else:
            d[k]=v
    return d

def Dict2Payload(cls,data):
    payloadData={}
    if isinstance(cls,Struct):
        for x in cls.subcons:
            if x.name in data:
                payloadData[x.name]=data[x.name]
    else:
        payloadData = data
    if "payloadHead" in data:
        data["payloadHead"]=Container(**data["payloadHead"])
    return Container(**payloadData)


PayloadData=Container #backward compatibility
Container.toDict=Payload2Dict #make toDict
Container.fromDict=Dict2Payload #and fromDict
Struct.fromDict=Dict2Payload #avbl as Classmethods

## Struct definitions (needs to be the same as the C code for the uC)
payloadHead = Struct(
    "packetID" / Int8ub,
    "informationID" / Int8ub,
    "tickCountHigh" / Int8ub,
    "tickCountLow" / Int8ub,
    "timerByteHigh" / Int8ub,
    "timerByteLow" / Int8ub,
)
payloadHead.__name__="payloadHead"

Payload0 = Struct(
    "payloadHead" / payloadHead,
)

Payload1 = Struct(
    "payloadHead" / payloadHead,
    "data1" / Int8ub,
)

Payload2 = Struct(
    "payloadHead" / payloadHead,
    "data1" / Int8ub,
    "data2" / Int8ub,
)

Payload3 = Struct(
    "payloadHead" / payloadHead,
    "data1" / Int8ub,
    "data2" / Int8ub,
    "data3" / Int8ub,
)

PayloadLookup = {
    "Payload0": Payload0,
    "Payload1": Payload1,
    "Payload2": Payload2,
    "Payload3": Payload3
}


"""
this needs to be in format name : id
because it gets passed to construct.Enum
"""
#TODO: queueEnum aus globals entfernen?

"""defined here, because if we put this
into ProtoSpec, we get ImportError due to
Cyclic dependencies

e.g.
Globals.MAX_LENGTH_OF_OBJECTNAME is used here
but defined in ProtSpec,
ProtSpec imports PayloadData
PayloadData import Globals,
Globals imports ProtoSpec
"""
objectTypes={
    'QUEUE': 0,
    'MUTEX': 1,
    'COUNTING_SEMAPHORE': 2,
    'BINARY_SEMAPHORE': 3,
    'RECURSIVE_MUTEX': 4,
    'TASK': 5,
    'NUMBER_OF_OBJECTTYPES': 6
}
"""
Build Dynamic Struct for Object
"""
def makeObjectStruct(nameLen):
    return  Struct(
        "ObjectNumber" / Int8ub, #extend to 16bit when possible
        "lenObjectName" / Int8ub,
        "objectName" / PaddedString(nameLen,"utf8")
    )


ObjectNoName = Struct(
    "ObjectNumber" / Int8ub, #extend to 16bit when possible
    "lenObjectName" / Int8ub,
)

ObjectListHeader = Struct(
    "packetID" / Int8ub,
    "informationID" / Int8ub,
    "objectType" / Enum(Byte,**objectTypes),
    "length" / Int8ub,
)


