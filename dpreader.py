import os
import re
import sys

print "*****dpreader for Laker-AMS******"
print "*********************************"
print "dpreader -lis xxx.lis -dp xxx.dp0"
print "dereader -i xxx"
print "*********************************"
print "**Version 0.01,  Author: wangke**"
print "*********************************"


lisFileName = ''
dpFileName  = ''


if len(sys.argv) == 1:
    fileName = raw_input("pleas input file name, without suffix. e.g. simulation for simulation.lis:")
    lisFileName = fileName + '.lis'
    dpFileName = fileName + '.dp0'

argvList = sys.argv
argvList.append('')

for i,eachArgv in enumerate(sys.argv):
    if i == 0:
        continue
    else:
        if eachArgv.lower() == '-lis' and lisFileName == '':
            lisFileName = argvList[i + 1]
            continue
        if eachArgv.lower() == '-dp' and dpFileName == '':
            dpFileName = argvList[i + 1]
            continue
        if eachArgv.lower() == '-i' and lisFileName == '' and dpFileName == '':
            lisFileName = argvList[i + 1] + '.lis'
            dpFileName = argvList[i + 1] + '.dp0'


if lisFileName == '' or dpFileName == '':
    print "Error: bad arguments"
    raw_input()
    sys.exit()


opsbaFileName = dpFileName + '.opsba'
    
                
                    



    
    



currentState = 'idle'       #idle->node voltage->idle, idle->subckt->idle
deviceInputFlag = 'notStart'   #notStart->doing->done

#initialization of device list
nodeDict = {}
elementDict = {}
#end of initialization of device list


class WKInstClass(object):
    "class for circuit instances"
    version = 0.0
    instPath = []
    instName = ''
    pinsAndNets = {}


class WKElementClass(object):
    "class for circuit elements"
    type = ''
    name = ''
    path = ''
    Info = {}
    dcopResults = {}
    def __init__(self,aPath,aName):
        if aName != '':
            self.type = aName[0]
            self.name = aName
            self.path = aPath
            self.Info = {}
            self.dcopResults = {}
         
    def elementID(self):
        if self.path == '':
            return self.name
        else:
            return self.path + '.' + self.name

    def dcopResultUpdate(self, aKey, aValue):
        if aKey != '':
            self.dcopResults[aKey] = aValue

    def print2opsba(self,fobj):
        fobj.write('[Instance %s]\n' %self.elementID())
        for eachKey in self.dcopResults.keys():
            fobj.write( '  %s=%s\n' %(eachKey, self.dcopResults[eachKey]))
        fobj.write('\n')





class WKNodeClass(object):
    "class for circuit nodes"
    version = '0.1'
    def __init__(self,aPath,aName):
        self.nodePath = aPath
        self.nodeName = aName
        self.nodeDCVolate = ''
        self.nodeConnections = []

    def nodeID(self):
        if self.nodePath == '':
            return self.nodeName
        else:
            return self.nodePath + '.' + self.nodeName

    def print2opsba(self,fobj):
        fobj.write('\n[NET %s]\n' %self.nodeID())
        fobj.write('V=%s' %self.nodeDCVolate)
        fobj.write('\n')


    
def circuitNameDictCreate(aLisFileName):   # {'1': {'multi': '1.00', 'number': '1', 'def': 'bias', 'name': 'xi2.'}}
    subcircuitList = []
    subcircuitDict = {}
    mark = 0
    try:
        fobj = open(aLisFileName,'r')
    except IOError,e:
        print "file open error:",e
    else:
        for eachLine in fobj:
            if re.search('number circuitname(\s)+definition(\s)+multiplier',eachLine) is not None:
                mark = 1
                continue
            if mark == 1:
                if re.search('[a-zA-Z0-9]',eachLine) is None:
                    break
                if re.search('circuit parameter definitions',eachLine) is not None:
                    break
                subcircuitList.append(eachLine)
        fobj.close()    
        
    for eachSubcircuitLine in  subcircuitList:
        subcircuitLineSplitList = re.findall(r'\s*(\S+)\s*',eachSubcircuitLine)
        if len(subcircuitLineSplitList) != 4:       # do some log
            #print "split list is not 4 ,skipped"
            1
        else:
            circuitNumber        = subcircuitLineSplitList[0]
            if circuitNumber != '0':    #ignore ' 0    main circuit'
                circuitName  = subcircuitLineSplitList[1]
                circuitDef   = subcircuitLineSplitList[2]
                circuitMulti = subcircuitLineSplitList[3]

                tempSubDict  = {'number' : circuitNumber , 'name' : circuitName , 'def' : circuitDef , 'multi' : circuitMulti}
                subcircuitDict[circuitNumber] = tempSubDict
    
    return subcircuitDict













def circuitNumber2Path(aNumberInString,theDict):   # returns ['xi1.',errCode]
    errCode = 0
    if aNumberInString == '0':   # for main circuit        
        return ['',errCode]
    if theDict.has_key(aNumberInString):
        if theDict[aNumberInString].has_key('name'):
            return [theDict[aNumberInString]['name'], errCode]
        else:
            return ['WKError', 1]
    else:
        return ['WKError', 2]
        
    
    





def nodeDCInfoFromListLine(aLisFileLine):  #[nodePathNumber, nodeName, nodeVoltage, errCode]
    # get info from line like ' 0:ena=  29.3887n      \n'
    errCode = 0
    if re.search(r'[\s]+(\d+):',aLisFileLine) is not None:
        nodePathNumber = re.findall(r'[\s]+(\d+):',aLisFileLine)[0]
    else:
        nodePathNumber = 'WKErrorMark'
        errCode += 1

    if re.search(r':(\w+)=',aLisFileLine) is not None:
        nodeName = re.findall(r':(\w+)=',aLisFileLine)[0]
    else:
        nodeName = 'WKErrorMark'
        errCode += 2
        
    if re.search(r'\s+([\w\.\-]+)\s+',aLisFileLine) is not None:
        nodeVoltage = re.findall(r'\s+([\w\.\-]+)\s+',aLisFileLine)[0]
    else:
        nodeVoltage = 'WKErrorMark'
        errCode += 4
    
    return [nodePathNumber, nodeName, nodeVoltage, errCode]    
        
        













circuitNameDict = circuitNameDictCreate(lisFileName)


try:
    fobj = open(dpFileName,'r')
except IOError,e:
    print "file open error:",e
else:
    for lineNum,eachLine in enumerate(fobj):
        #state dective, the state mark line will be skipped
        if re.search(r'\s+node\s+=voltage',eachLine) is not None:
            currentState = 'node voltage'
            continue
            
        if currentState == 'node voltage' and re.search(r'\w+=\s+',eachLine) is None:
            currentState = 'idle'
        if re.search('subckt\s+',eachLine) is not None:
            currentState = 'subckt'
        if currentState == 'subckt' and re.search(r'\w+',eachLine) is None:
            currentState = 'idle'
            elementDict[newElementID] = newElement
        #end of state dective        

        
        #the main section of .dp# file analysis
        if currentState == 'idle':
            # do nothing
            continue 
        if currentState == 'node voltage':
            # do something to get node voltage
            [nodePathNumber, nodeName, nodeVoltage, errCode] = nodeDCInfoFromListLine(eachLine)
            if errCode == 0:
                newNode = WKNodeClass(circuitNumber2Path(nodePathNumber,circuitNameDict)[0],nodeName)
                newNode.nodeDCVolate = nodeVoltage
                nodeDict[newNode.nodeID()] = newNode
            continue
        if currentState == 'subckt':
            #do something to get subckt info
            if re.search('subckt',eachLine) is not None: # head of subckt section
                if re.search('subckt\s+([\w\.]+)',eachLine) is not None:
                    thisElementPath = re.findall('subckt\s+([\w\.]+)',eachLine)[0]
                    thisElementPath = thisElementPath
                    continue
                else:
                    thisElementPath = ''
                    continue
            if re.search('element',eachLine) is not None: # second line of subckt section
                if re.search(r':([\w\.]+)\s',eachLine) is not None:
                    thisElementName = re.findall(r':([\w\.]+)\s',eachLine)[0]
                else:
                    thisElementName = 'WKError'
                newElement = WKElementClass(thisElementPath,thisElementName)
                newElementID = newElement.elementID()
                continue
                
            # get dcop information for elements
            eachLineToSplit = re.sub(r'\s\s+' , ':' , '  ' + eachLine)
            eachLineToSplit = re.sub(r'\s' , '' , eachLineToSplit)
            tempSplitResult = eachLineToSplit.split(':')
            if len(tempSplitResult) == 3:
                newElement.dcopResultUpdate(tempSplitResult[1],tempSplitResult[2])
            continue

try:
    fobj = open(opsbaFileName,'w')
except IOError,e:
    print "file create error:",e
else:
    for eachKey in nodeDict:
        nodeDict[eachKey].print2opsba(fobj)
    for eachKey in elementDict.keys():
        elementDict[eachKey].print2opsba(fobj)

fobj.close()
print "************results**************"
print "opsba file %s created successfully!" %opsbaFileName

                        
    

    
                
                
