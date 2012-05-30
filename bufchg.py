##

import os,re,string,sys


def WKOpenFile(filename,mode):
    try:
        fobj = open(filename,mode)
    except IOError,e:
        print 'file open error',e
    else:
        return fobj


def readSDC(sdcFileName, checkoutFileName):
    sdcFile = WKOpenFile(sdcFileName,'r')
    searchResultsDict = {}
    regxPattern = r'(?:create_clock|create_generated_clock)\s+\[get_pins\s+([\w\d\/]+)\]'
    #regu Pattern for lines like:create_clock [get_pins chipmain/chipfun/clkgen_dig/clko_peri] ....
    for line, eachLine in enumerate(sdcFile):
        eachLine = eachLine.split('#')[0]                           #ignore chars after '#'
        temp = re.findall(regxPattern, eachLine)
        if temp != []:
            searchResultsDict[line] = temp
    
    sdcFile.close()  
    checkoutFile = WKOpenFile(checkoutFileName,'w')   
    for eachKey in searchResultsDict.keys():
        checkoutFile.write('%d %s \n' %(eachKey,searchResultsDict[eachKey]))
    checkoutFile.close()    


def delComment( Text ):
    """ removed comment """
    single_line_comment = re.compile(r"//(.*)$", re.MULTILINE)
    multi_line_comment  = re.compile(r"/\*(.*?)\*/",re.DOTALL)
    Text = multi_line_comment.sub('\n',Text)
    Text = single_line_comment.sub('\n',Text)
    return Text




def verilogModuleIndexDict(Text):
    regxPatternForModuleName = r'module\s+([\w\d\_\-]+)'
    state = 'initial'
    currentModuleName = ''
    moduleDict = {}
    patModuleBlock = r'(module\s+[\w\d\s\n\[\]\(\)\;\.\,\:\'\{\}\=]+?)[\s\n]+endmodule[\s\n]+'
    result = re.findall(patModuleBlock,Text)
    for eachModule in result:
        moduleName = re.findall(regxPatternForModuleName, eachModule)[0]
        moduleDict[moduleName] = eachModule
    return moduleDict


def verilogModule(Text,moduleName):
    patModuleBlock = '(module\s+' + moduleName + '[\w\d\s\n\[\]\(\)\;\.\,\:\'\{\}\=]+?)[\s\n]+endmodule[\s\n]+'
    module = re.findall(patModuleBlock,Text)
    result = ''
    if module != []:
        result = re.sub(r'\n+','',module[0],count=0)
        result = result.split(';')
    return result
    

   
    #for line,eachLine in enumerate(Text):
    #    if state == 'initial':  #find module name
    #        temp = re.findall(r'\s+module\s+([\w-_\d]+)',eachLine)
    #        if temp != []:
    #            currentModuleName = temp
    #            state = 'module section'
                
            
def findNode(moduleName, nodeToFind):
    module = verilogModule(verilogText, moduleName)
    if module == '':
        return nodeToFind
    pat1 = r'^\s*(wire|input|output|inout|reg|module)\s'
    pat2 = '[\s+\(]+(' + nodeToFind + ')[\s+\)]+'
    pat3 = '[\w\d_-]+\s+([\w\d_-]+)\s+'
    pat4 = '\.([\w\d_-]+)[\s\(]+' + nodeToFind +'\s*\)'
    # this section needs discussion

    outputPorts = ['O','Q','QB']    

    for eachLine in module:
        if re.search(pat1, eachLine) is None:
            if re.search(pat2, eachLine) is not None:
                #print 'in module this instance line is:\n %s' %eachLine
                if re.findall(pat4, eachLine)[0] in outputPorts:
                    return '%s/%s' %(re.findall(pat3, eachLine)[0],re.findall(pat4, eachLine)[0])
                #print result
    return 'NOTFOUND:%s/%s' %(moduleName, nodeToFind)
            
    
    
    
    # end of this section needs discussion    
                
def modifyPath(aPath):
    path = aPath.split('/')
    path[-1] = findNode(path[-2], path[-1])
    result = ''
    for i,each in enumerate(path):
        if i == 0:
            result = result + each
        else:
            result = result + '/' + each
    return result
    


def main(sdcFileName, verilogFileName):
    if os.path.isfile(sdcFileName + '.log'):
        os.remove(sdcFileName + '.log')

    readSDC(sdcFileName, sdcFileName + '.log')

    verilogFile = WKOpenFile(verilogFileName,'r')
    global verilogText

    
    verilogText = verilogFile.read()
    verilogText = delComment(verilogText)
    
    sdcFile = WKOpenFile(sdcFileName,'r')
    newSdcFile = WKOpenFile(sdcFileName + '.new.sdc','w')
    logFile = WKOpenFile(sdcFileName + '.log', 'r')
    
    sdcText = sdcFile.read()
    
    for eachLine in logFile:
        lineNumber = re.findall(r'(\d+)\s\[', eachLine)
        pathName = re.findall(r'\[\'([\w\d\/\-\_]+)\'\]', eachLine)
        if lineNumber != [] and pathName != []:
            number = string.atoi(lineNumber[0])
            sdcText = re.sub(pathName[0],modifyPath(pathName[0]),sdcText,count = 0)
    
    newSdcFile.write(sdcText)
    logFile.close()
    verilogFile.close()
    sdcFile.close()
    newSdcFile.close()


if __name__ == '__main__' :
    version = 'v0.0.1c'
    print '*********************'
    print '**clkchg ver:%s' %version
    print '**Author:Wangke******'
    print '**Date:2012/05/29****'
    print '*********************'
    if len(sys.argv) > 2:
        main(sys.argv[1],sys.argv[2])
    else:
        sdcFileName = raw_input('input .sdc file name:')
        verilogFileName = raw_input('input .v file name:')
        main(sdcFileName, verilogFileName)