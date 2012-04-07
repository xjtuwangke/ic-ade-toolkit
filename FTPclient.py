#_*_encoding:utf-8_*_
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
        except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
            print 'ERROR: cannot reach "%s"'  %self.host
            return
        print '***connected to host "%s"'  %self.host

        try:
            self.ftp.login(self.loginName,self.loginPWD)
        except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
            print 'ERROR: cannot login'
            logFile.write('ERROR: cannot login to host=%s,user=%s,password=%s' %(self.host,self.loginName,self.loginPWD))
            self.ftp.quit()
            return
        print '***logged in'
        self.pasv = True
        self.connected = True

    def changePWD(self,DIRN):
        logFile.write('changePWD(%s)\n' %DIRN)
        if self.connected == True:
            try:
                self.ftp.cwd(DIRN)
            except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
                print 'ERROR: cannot change PWD to "%s"' %DIRN
                return
            print '***Changed PWD to "%s"' %DIRN
            return
        else:
            print 'cannot change PWD, not logged in'
            logFile.write('cannot change PWD, not logged in\n')
            return

    def uploadTXT(self,fileName):
        logFile.write('uploadTXT(%s)\n' %fileName)
        if self.connected == True:
            try:
                file_handler = open(fileName,'r')
            except IOError,e:
                print 'Error: file open error', e
                logFile.write('Error: txt file %s open error\n' %fileName)
            else:
                ##if fileName in self.ftp.nlst():
                    ##logFile.write('%s is uploading, skipped in uploadTXT()\n' %fileName)
                ##else:
                    try:
                        self.ftp.storlines('STOR %s' %fileName,file_handler)
                        file_handler.close()
                    except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
                        print 'Error: cannot upload file "%s"' %fileName
                        print e
                        logFile.write('Error: cannot upload file "%s"\n' %fileName)
                        return False
                    else:
                        print '***uploaded "%s" to FTP server' %fileName
                        logFile.write('***uploaded "%s" to FTP server\n' %fileName)
                        return True
        else:
            print 'cannot upload file , not logged in'
            logFile.write('cannot upload file , not logged in\n')
            return False

    def uploadBIN(self, fileName):
        logFile.write('uploadBIN(%s)\n' %fileName)
        bufSize = 32768
        if self.connected == True:
            try:
                file_handler = open(fileName,'rb')
            except IOError,e:
                print 'Error: file open error', e
                logFile.write('Error: BIN file %s open error\n' %fileName)
            else:
                ##if fileName in self.ftp.nlst():
                    ##logFile.write('%s is uploading, skipped in uploadBIN()\n' %fileName)
                ##else:
                    try:
                        self.ftp.storbinary('STOR %s' %fileName,file_handler,bufSize)
                        file_handler.close()
                    except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
                        print 'Error: cannot upload file "%s"' %fileName
                        logFile.write('Error: cannot upload file "%s"\n' %fileName)
                        return False
                    else:
                        print '***uploaded "%s" to FTP server' %fileName
                        logFile.write('***uploaded "%s" to FTP server\n' %fileName)
                        return  True
        else:
            print 'cannot upload file , not logged in'
            logFile.write('cannot upload file , not logged in\n')
            return False

    def logout(self):
        logFile.write('logout\n')
        ##if self.connected == True:
        try:
            self.ftp.quit()
        except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
            print 'Error: cannot logout'
            logFile.write('Error: failed to logout\n')
        else:
            ##self.connected = False
            print 'logged out'
            logFile.write("logged out\n")
        return

    def rename(self, oldName, newName):
        logFile.write('rename(%s,%s)\n' %(oldName,newName))
        if self.connected == True:
            print "trying to rename\n"
            try:
                #self.ftp.delete(newName)
                self.ftp.rename(oldName, newName)
            except (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
                logFile.write('Error: cannot rename a file from "%s" to "%s"\n' %(oldName,newName))
                return False
        return True
        
class WKExpFTP(WKFTPConnection):
    
    def init(self):
        self.DialogList = []
        self.connect()
        self.subPath = 'OutputData'
        os.chdir(self.subPath)
        try:
            fobj = open('Wait.txt','w')
        except IOError,e:
            print 'can not create file Wait.txt'
        else:
            fobj.write('please wait...\n')
            fobj.close()

    def disableExp(self, oneDict):
        self.connect()
        self.changePWD('\\')
        try:
            self.ftp.mkd(oneDict)
        except  (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
            donothing = 1
        self.changePWD(oneDict)
        txtName = 'Wait.txt'
        if self.uploadTXT(txtName):
            self.rename(txtName, oneDict + '.txt')
        self.rename(oneDict + 'jpg', oneDict + '.old.jpg')
        
        

    def updateDialog(self):
        watchDog = 3
        #if self.connected == True:
        self.connect()
        self.changePWD('\\')
        while watchDog > 0:
            if self.uploadTXT('Dialog.txt'):
                watchDog = 0
            else:
                self.connect()
                watchDog = watchDog - 1

    def updateDict(self,oneDict):
        print 'updateDict() is updating %s' %oneDict
        self.disableExp(oneDict)
        if self.connected == True:
            self.changePWD('\\')
            try:
                self.ftp.mkd(oneDict)
            except  (ftplib.error_perm, ftplib.error_reply, socket.error, socket.gaierror, ftplib.error_proto), e:
                print "path already exists"
            self.changePWD(oneDict)
            if os.path.exists(oneDict):
                print "os.chdir(%s)" %oneDict
                os.chdir(oneDict)
                ##if (oneDict + '.txt.temp' in self.ftp.nlst()) or (oneDict + '.jpg.temp' in self.ftp.nlst()):
                ##    logFile.write('%s still uploading, skip\n' %oneDict)
                ##self.rename(oneDict + '.txt.temp', oneDict + '.txt')
                ##self.rename(oneDict + '.jpg.temp', oneDict + '.jpg')
                ##else:
                timeStamp = str(os.stat(oneDict + '.txt').st_mtime)
                txtName = oneDict + '.txt'
                jpgName = oneDict + '.jpg'
                os.system('copy ' + txtName + ' ' + '~' + txtName + timeStamp)
                os.system('copy ' + jpgName + ' ' + '~' + jpgName + timeStamp)

                watchDog1 = 3
                watchDog2 = 3
                while watchDog1 > 0:
                    if self.uploadTXT('~' + txtName + timeStamp):
                        watchDog1 = 0
                        watchDog2 = 3
                        while watchDog2 > 0:
                            if self.rename('~' + txtName + timeStamp, txtName):
                                watchDog2 = 0
                            else:
                                self.connect()
                                self.changePWD(oneDict)
                                watchDog2 = watchDog2 - 1
                    else:
                        self.connect()
                        self.changePWD(oneDict)
                        watchDog1 = watchDog1 - 1


                watchDog1 = 3
                watchDog2 = 3
                while watchDog1 > 0:
                    if self.uploadBIN('~' + jpgName + timeStamp):
                        watchDog1 = 0
                        watchDog2 = 3
                        while watchDog2 > 0:
                            if self.rename('~' + jpgName + timeStamp, jpgName):
                                watchDog2 = 0
                            else:
                                self.connect()
                                self.changePWD(oneDict)
                                watchDog2 = watchDog2 - 1
                    else:
                        self.connect()
                        self.changePWD(oneDict)
                        watchDog1 = watchDog1 - 1

                
                #if self.uploadBIN('~' + jpgName + timeStamp):
                #    self.rename('~' + jpgName + timeStamp, jpgName)
                ##self.logout()
                self.connect()
            else:
                print "local path %s does not exist" %oneDict
                logFile.write("local path %s does not exist\n" %oneDict)
            print "os.chdir('..')"
            os.chdir('..')
            self.updateDialog()

    def timerHandler(self):
        thisDialog = []
        ##if os.path.exists('Dialog.txt.temp'):
        ##    logFile.write('Dialog.txt is still uploading, skip\n')
        ##else:
        ##    os.system('copy Dialog.txt Dialog.txt.temp')
        try:
            fobj = open('Dialog.txt','r')
        except IOError,e:
            print 'Dialog.txt file open error', e
            logFile.write('Dialog.txt file open error\n')
        else:
            for i,eachLine in enumerate(fobj):
                temp = eachLine.split('\n')
                if temp[0] is not None:
                    thisDialog.append(temp[0])
            fobj.close()
            logFile.write('end Dialog.txt analysising, go to upload module\n')
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
    
    newFTP.timerHandler()
    print 'first sleeping'
    time.sleep(20)
    newFTP.logout()
    newFTP.connect()

    while(True):
        #newFTP.connect()
        newFTP.timerHandler()
        #newFTP.logout()
        print 'sleeping\n'
        time.sleep(10)
        newFTP.logout()
        newFTP.connect()
        time.sleep(1)
        
        

    
    #newFTP.changePWD('exp1')
    #newFTP.changePWD('\\')
    #newFTP.uploadTXT('FTPtest.py')
    #newFTP.uploadBIN('1.jpg')
    #newFTP.logout()
    
def test_largefile():
    HOST = 'informore.meibu.com'
    DIRN = 'test'
    LoginNAME = 'test'
    LoginPWD  = 'test'
    newFTP = WKFTPConnection(HOST,LoginNAME,LoginPWD)
    newFTP.connect()
    newFTP.uploadBIN('test.rmvb')
    newFTP.rename('test.rmvb','test2.rmvb')
    
    
if __name__ == '__main__':
    version = 'v0.0.1b12'
    try:
        logFile = open('ftpclient.log','w')
    except IOError,e:
        print 'error, can not create log file:', e
    else:
        logFile.write('version = %s\n' %version)
        main()