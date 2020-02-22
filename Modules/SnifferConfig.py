import configparser
import json
import Globals
import copy
import os

## @package SnifferConfig
#  SnifferFilter is a dialog, the user can interact with in order to filter out
#  the Measurement results. The results can be filtered by either the ID or objectNames.
#  Currently, a distinction between local and global filter can be made, but the filter can be used
#  for all sorts of use-cases.

## The actual implementation of the SnifferConfig class
class  ConfigurationData:
    
    ## The constructor.
    #  Assign the name, so we can save it with the corresponding tab
    def __init__(self,parent,name = 'Implement a proper name...'):
        self.configName = name
        print('We currently only have one attribute. Name is: ' + self.configName)
        print('Feel free to add your own attributes')
        self.pop = 0
        
    ## Read and parse the specified config format from a file
    #  to update the dictionary      
    def parseConfigFromFile(self):
        print('Loading Config from <TabName>Config.jcfg, and populate our instance with the corresponding attributes which are assigned to a name')
        myDir = os.getcwd()
        configDir = os.path.join(myDir,'SnifferConfig')
        if not os.path.isdir(configDir):
            os.mkdir(configDir)
        openPath = os.path.join(configDir,self.configName+'Config.jcfg')
        if not os.path.isfile(openPath):
            print('There is no config for '+str(openPath))
            return
        with open(openPath,'r') as f:
            try:
                HighLevelDict = json.load(f)
                ConfigDict = HighLevelDict['Configuration']
                # We, as an instance actually store the information, so we update *ourselves*
                for _,values in ConfigDict.items():
                    self.__dict__.update(**values)
                    
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)   
                    
    ## Save the content from the own instance to a json file, corresponding to the name                      
    def saveConfigToFile(self):
        print('Saving own attributes + our name to a <TabName>Config.jcfg')
        myDir = os.getcwd()
        configDir = os.path.join(myDir,'SnifferConfig')
        if not os.path.isdir(configDir):
            os.mkdir(configDir)
            
        openPath = os.path.join(configDir,self.configName+'Config.jcfg')
        print(openPath)
        try:
            with open(openPath,'w+') as f:
                meAsDict = copy.deepcopy(self.__dict__)
                filteredDict = self.filterDict(meAsDict, 'config')
                jdict = {};
                jdict[self.configName] = filteredDict
                md = {'Configuration':jdict,'SnifferVersion':Globals.versionNumber}
                json.dump(md,f, indent=2, sort_keys=True,skipkeys=True, separators=(',', ': '))
                
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
       
    def filterDict(self,filterdict,filterexpr):
        myDict = {}
        for key, value in filterdict.items():
            if key.startswith(filterexpr):
                myDict[key] = value
        return myDict 