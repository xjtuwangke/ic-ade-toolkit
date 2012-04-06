#!/usr/bin/env python

import ftplib
import os
import socket
import time


class WKFTPConnection(object):

    def __init__(self,host,loginName,loginPWD):
        self.host = host
        self.loginName = loginName
        self.loginPWD = loginPWD
        self.connected = False

    def connect(self):
        print 'connecting to host'
        try:
            self.ftp = ftplib.FTP(self.host)
        except (socket.error, socket.gaierror), e:
            print 'ERROR: cannot reach "%s"'  %self.host
            return
        print '***connected to host "%s"'  %self.host

        try:
            self.ftp.login(self.loginName,self.loginPWD)
        except ftplib.error_perm:
            print 'ERROR: cannot login'
            self.ftp.quit()
            return
        print '***logged in'
        self.connected = True

    def changePWD(self,DIRN):
        if self.connected == True:
            try:
                self.ftp.cwd(DIRN)
            except ftplib.error_perm:
                print 'ERROR: cannot change PWD to "%s"' %DIRN
                return
            print '***Changed PWD to "%s"' %DIRN
            return
        else:
            print 'cannot change PWD, not logged in'
            return

    def uploadTXT(self,fileName):
        if self.connected == True:
            try:
                file_handler = open(fileName,'r')
            except IOError,e:
                print 'Error: file open error', e
                logFile.write('Error: file open error')
            else:
                if fileName in self.ftp.nlst():
                    logFile.write('%s is uploading, skipped in uploadTXT()\n' %fileName)
                else:
                    try:
                        self.ftp.storlines('STOR %s' %fileName,file_handler)
                        file_handler.close()
                    except ftplib.error_perm:
                        print 'Error: cannot upload file "%s"' %fileName
                        logFile.write('Error: cannot upload file "%s"\n' %fileName)
                    else:
                        print '***uploaded "%s" to FTP server' %fileName
                        logFile.write('***uploaded "%s" to FTP server\n' %fileName)
                        return
        else:
            print 'cannot upload file , not logged in'

    def uploadBIN(self, fileName):
        bufSize = 2048
        if self.connected == True:
            try:
                file_handler = open(fileName,'rb')
            except IOError,e:
                print 'Error: file open error', e
                logFile.write('Error: file open error')
            else:
                if fileName in self.ftp.nlst():
                    logFile.write('%s is uploading, skipped in uploadBIN()\n' %fileName)
                else:
                    try:
                        self.ftp.storbinary('STOR %s' %fileName,file_handler,bufSize)
                        file_handler.close()
                    except ftplib.error_perm:
                        print 'Error: cannot upload file "%s"' %fileName
                        logFile.write('Error: cannot upload file "%s"\n' %fileName)
                    else:
                        print '***uploaded "%s" to FTP server' %fileName
                        logFile.write('***uploaded "%s" to FTP server\n' %fileName)
                        return      
        else:
            print 'cannot upload file , not logged in'
            logFile.write('cannot upload file , not logged in\n')

    def logout(self):
        if self.connected == True:
            self.ftp.quit()
            self.connected = False
            print 'logged out'
            logFile.write("logged out\n")
        return

    def rename(self, oldName, newName):
        if self.connected == True:
            print "trying to rename\n"
            try:
                #self.ftp.delete(newName)
                self.ftp.rename(oldName, newName)
            except ftplib.error_perm:
                logFile.write('Error: cannot rename a file from "%s" to "%s"\n' %(oldName,newName))
        return
        
class WKExpFTP(WKFTPConnection):
    def init(self):
        self.DialogList = []
        self.connect()
        self.subPath = 'OutputData'
        os.chdir(self.subPath)


    def updateDialog(self):
        if self.connected == True:
            self.changePWD('\\')
            self.uploadTXT('Dialog.txt')

    def updateDict(self,oneDict):
        if self.connected == True:
            self.changePWD('\\')
            try:
                self.ftp.mkd(oneDict)
            except  ftplib.error_perm:
                print "path already exists"
            self.changePWD(oneDict)
            if os.path.exists(oneDict):
                os.chdir(oneDict)
                if (oneDict + '.txt.temp' in self.ftp.nlst()) or (oneDict + '.jpg.temp' in self.ftp.nlst()):
                    logFile.write('%s still uploading, skip\n' %oneDict)
                    self.rename(oneDict + '.txt.temp', oneDict + '.txt')
                    self.rename(oneDict + '.jpg.temp', oneDict + '.jpg')
                else:
                    os.system('copy ' + oneDict + '.txt ' + oneDict + '.txt.temp')
                    os.system('copy ' + oneDict + '.jpg ' + oneDict + '.jpg.temp')
                    self.uploadTXT(oneDict + '.txt.temp')
                    self.uploadBIN(oneDict + '.jpg.temp')
                    self.rename(oneDict + '.txt.temp', oneDict + '.txt')
                    self.rename(oneDict + '.jpg.temp', oneDict + '.jpg')      
            else:
                print "local path %s does not exist" %oneDict
                logFile.write("local path %s does not exist\n" %oneDict)
            print "this mark"
            os.chdir('..')
            self.updateDialog()

    def timerHandler(self):
        thisDialog = []
        if os.path.exists('Dialog.txt.temp'):
            logFile.write('Dialog.txt is still uploading, skip\n')
        else:
            os.system('copy Dialog.txt Dialog.txt.temp')
        try:
            fobj = open('Dialog.txt','r')
        except IOError,e:
            print 'Dialog.txt.temp file open error', e
            logFile.write('Dialog.txt.temp file open error\n')
        else:
            for i,eachLine in enumerate(fobj):
                temp = eachLine.split('\n')
                if temp[0] is not None:
                    thisDialog.append(temp[0])
            fobj.close()
            for i,eachLine in enumerate(thisDialog):
                if i == 0:
                    if eachLine == '(doing:done)':
                        print 'experiment done, skipped uploading'
                        logFile.write('experiment done, skipped uploading\n')
                        self.DialogList = thisDialog
                        return
                else:
                    if i == 1:
                        self.updateDict('Experiment'+str(i))
                    else:
                        if i < len(self.DialogList):
                            if eachLine != self.DialogList[i]:
                                self.updateDict('Experiment'+str(i))
                        else:
                            self.updateDict('Experiment'+str(i))
            self.DialogList = thisDialog


def main():
    HOST = 'informore.meibu.com'
    DIRN = 'test'
    LoginNAME = 'test'
    LoginPWD  = 'test'
    newFTP = WKExpFTP(HOST,LoginNAME,LoginPWD)
    newFTP.init()
    
    while(True):
        time.sleep(10)
        newFTP.timerHandler()

    
    #newFTP.changePWD('exp1')
    #newFTP.changePWD('\\')
    #newFTP.uploadTXT('FTPtest.py')
    #newFTP.uploadBIN('1.jpg')
    #newFTP.logout()
    
    
    
    
if __name__ == '__main__':
    try:
        logFile = open('ftpclient.log','w')
    except IOError,e:
        print 'error, can not create log file:', e
    else:
        main()