import os
import re
import win32com.client as win32
from Tkinter import Tk
from tkMessageBox import showwarning

ls=os.linesep
flist=[]

#open ini file
filename='hspreader.ini'
xlist=[]
ylist=[]
zlist=[]
valuelist=[]
try:
	fobj=open(filename,'r')
except IOError,e:
    print "file open error:",e
else:
    for eachline in fobj:
        eachline=re.findall('[\n]*[a-zA-Z_0-9+-.=#,]+',eachline)
        if re.search('[Xx][Ll][Ii][Ss][Tt][=]',eachline[0]) is not None:
            xline=re.split('=',eachline[0])
            xlist+=(re.split(',',xline[1]))
        if re.search('[Yy][Ll][Ii][Ss][Tt][=]',eachline[0]) is not None:
            yline=re.split('=',eachline[0])
            ylist+=(re.split(',',yline[1]))
        if re.search('[Zz][Ll][Ii][Ss][Tt][=]',eachline[0]) is not None:
            zline=re.split('=',eachline[0])
            zlist+=(re.split(',',zline[1]))
        if re.search('[Vv][Ll][Ii][Ss][Tt][=]',eachline[0]) is not None:
            vline=re.split('=',eachline[0])
            valuelist+=(re.split(',',vline[1]))
        if re.search('[Ff][Ii][Ll][Ee][=]',eachline[0]) is not None:
            fline=re.split('=',eachline[0])
            fname=(re.split(',',fline[1]))[0]
            filename=fname+'0'
            
    fobj.close()

#open files
try:
	fobj=open(filename,'r')
except IOError,e:
    print "file open error:",e
else:
	flist.append(fobj)
	counter=0
	while True:
		counter+=1
		filename=fname+str(counter)
		if os.path.exists(filename):
			fobj=open(filename,'r')
			flist.append(fobj)
		else:
			print "%d file(s) are opened" %counter
			break

#read files
filedata_all=[]
for eachfile in flist:
    filedata_one=[]
    for eachline in eachfile:
        if (re.search('\.[Tt][Ii][Tt][Ll][Ee]',eachline) is None)&(re.search('[$]',eachline) is None):
            filedata_one.append(eachline)  
    filedata_all.append(filedata_one)
eachfile.close()

#data analysis

list=[]
index=[]
titles=0
datas=0
flag='title'
for eachline in filedata_all[0]:
    if flag=='title':
        index=index+re.findall('[\n]*[a-zA-Z_0-9+-.]+#?',eachline)
        titles+=1
        if (re.search('#',eachline)) is not None:
            flag='data'
    else:
        datas+=1
        
datasheet=[]
datasheet1=[]

for eachfile in filedata_all:
    counter_title=titles
    for eachline in eachfile:
        if counter_title<=0:
            temp=re.findall('[\n]*[a-zA-Z0-9.+-]+',eachline)
            datasheet1.append(temp)
        counter_title-=1

raw=[]
counter_data=0
for eachline in datasheet1:
    counter_data+=1
    raw+=eachline
    if counter_data>=titles:
        datasheet.append(raw)
        raw=[]
        counter_data=0

try:
    fobj=open(fname,'w')
except IOError,e:
	print "file create error:",e
else:
    for eachline in index:
        fobj.write(' %20s\t' %(eachline))
    fobj.write('\n')
    for eachline in datasheet:
        for eachword in eachline:
            fobj.write(' %20s\t' %(eachword))
        fobj.write('\n')
    for eachline in index:
        fobj.write(' %20s\t' %(eachline))
    fobj.write('\n')
    fobj.write('*****END*****\n')
    fobj.close()



#seperator

xaddr=[]
yaddr=[]
zaddr=[]
vaddr=[]

xvalue=[]
yvalue=[]
zvalue=[]

xnum=len(xlist)
ynum=len(ylist)
znum=len(zlist)

valuenum=len(valuelist)

for eachx in xlist:
    xvalue.append([])
    xaddr.append(None)

for eachy in ylist:
    yvalue.append([])
    yaddr.append(None)

for eachz in zlist:
    zvalue.append([])
    zaddr.append(None)

for eachv in valuelist:
    vaddr.append(None)

for i,eachword in enumerate(index):
    for x,eachx in enumerate(xlist):
        if eachword==eachx:
            xaddr[x]=i
    for y,eachy in enumerate(ylist):
        if eachword==eachy:
            yaddr[y]=i
    for z,eachz in enumerate(zlist):
        if eachword==eachz:
            zaddr[z]=i
    for v,eachv in enumerate(valuelist):
        if eachword==eachv:
            vaddr[v]=i

for eachline in datasheet:
    for i,eachxaddr in enumerate(xaddr):
        if eachline[eachxaddr] not in xvalue[i]:
            xvalue[i].append(eachline[eachxaddr])
    for i,eachyaddr in enumerate(yaddr):
        if eachline[eachyaddr] not in yvalue[i]:
            yvalue[i].append(eachline[eachyaddr])
    for i,eachzaddr in enumerate(zaddr):
        if eachline[eachzaddr] not in zvalue[i]:
            zvalue[i].append(eachline[eachzaddr])

tablex=[]
for eachline in datasheet:
    temp=[]
    for i,eachgroup in enumerate(xvalue):
        for j,eachvalue in enumerate(eachgroup):
            if eachline[xaddr[i]]==eachvalue:
                temp.append(j)
    tablex.append(temp)

tabley=[]
for eachline in datasheet:
    temp=[]
    for i,eachgroup in enumerate(yvalue):
        for j,eachvalue in enumerate(eachgroup):
            if eachline[yaddr[i]]==eachvalue:
                temp.append(j)
    tabley.append(temp)

tablez=[]
for eachline in datasheet:
    temp=[]
    for i,eachgroup in enumerate(zvalue):
        for j,eachvalue in enumerate(eachgroup):
            if eachline[zaddr[i]]==eachvalue:
                temp.append(j)
    tablez.append(temp)

    

xweight=[]
for eachgroup in xvalue:
    temp=len(eachgroup)
    for i,each in enumerate(xweight):
        xweight[i]=each*temp
    xweight.append(temp)
xweight.append(1)

yweight=[]
for eachgroup in yvalue:
    temp=len(eachgroup)
    for i,each in enumerate(yweight):
        yweight[i]=each*temp
    yweight.append(temp)
yweight.append(1)

zweight=[]
for eachgroup in zvalue:
    temp=len(eachgroup)
    for i,each in enumerate(zweight):
        zweight[i]=each*temp
    zweight.append(temp)
zweight.append(1)

datatable=[]
for z in range(zweight[0]):
    temp1=[]
    for y in range(yweight[0]):
        temp2=[]
        for x in range(xweight[0]):
            temp3=[]
            for v in range(valuenum):
                temp3.append([])
            temp2.append(temp3)
        temp1.append(temp2)
datatable.append(temp1)

for i,eachline in enumerate(datasheet):
    weighted_x=0
    weighted_y=0
    weighted_z=0
    for j,each in enumerate(tablex[i]):
        weighted_x+=xweight[j+1]*each
    for j,each in enumerate(tabley[i]):
        weighted_y+=yweight[j+1]*each
    for j,each in enumerate(tablez[i]):
        weighted_z+=zweight[j+1]*each
    for j,each in enumerate(vaddr):
        datatable[weighted_z][weighted_y][weighted_x][j]=eachline[each]        

maxvalue=[]
minvalue=[]
for i,eachvalue in enumerate(valuelist):
    maxvalue.append([0,0,0,datatable[0][0][0][i]])
    minvalue.append([0,0,0,datatable[0][0][0][i]])
    
for z,eachz in enumerate(datatable):
  for y,eachy in enumerate(eachz):
      for x,eachx in enumerate(eachy):
          for i,eachvalue in enumerate(valuelist):
              if eachx[i]!='failed' and eachx[i]!=[] and eachx[i]!='Failed':
                print eachx[i]
                temp=float(eachx[i])
                if maxvalue[i][3]=='failed' or maxvalue[i][3]==[] or maxvalue[i][3]=='Failed':maxvalue[i]=[z,y,x,temp]
                else:
                    if float(maxvalue[i][3])<temp:maxvalue[i]=[z,y,x,temp]
                if minvalue[i][3]=='failed' or minvalue[i][3]==[] or minvalue[i][3]=='Failed':minvalue[i]=[z,y,x,temp]
                else:
                    if float(minvalue[i][3])>temp:minvalue[i]=[z,y,x,temp]                   

def excel(which_z,which_value):
  app='Excel'
  xl = win32.Dispatch('%s.Application' % app) 
  ss = xl.Workbooks.Add()
  sh = ss.ActiveSheet 
  xl.Visible = True 
  sh.Cells(1,1).Value = valuelist[which_value]
  x_lines=len(xlist)
  y_lines=len(ylist)
  for i in range(x_lines):
      k=0
      mod=len(xvalue[i])
      for j in range(1,xweight[0]+1,xweight[i+1]):
        sh.Cells(i+2,y_lines+j).Value = '%s=%s' % (xlist[i], xvalue[i][k])
        k=k+1
        k=k%mod
  for i in range(y_lines):
      k=0
      mod=len(yvalue[i])
      for j in range(1,yweight[0]+1,yweight[i+1]):
        sh.Cells(j+1+x_lines,i+1).Value = '%s=%s' % (ylist[i], yvalue[i][k])
        k=k+1
        k=k%mod
  for i,eachy in enumerate(datatable[which_z]):
      for j,eachx in enumerate(eachy):
          sh.Cells(i+2+x_lines,j+1+y_lines).Value='%s' %eachx[which_value]

  sh.Cells(x_lines+3+yweight[0],1).Value='max='
  sh.Cells(x_lines+3+yweight[0],2).Value=maxvalue[which_value][3]
  sh.Cells(x_lines+3+yweight[0],3).Value='Condition:'
  sh.Cells(x_lines+3+yweight[0],6).Value='Column='
  sh.Cells(x_lines+3+yweight[0],7).Value=maxvalue[which_value][2]+1
  sh.Cells(x_lines+3+yweight[0],4).Value='Line='
  sh.Cells(x_lines+3+yweight[0],5).Value=maxvalue[which_value][1]+1

  sh.Cells(x_lines+4+yweight[0],1).Value='min='
  sh.Cells(x_lines+4+yweight[0],2).Value=minvalue[which_value][3]
  sh.Cells(x_lines+4+yweight[0],3).Value='Condition:'
  sh.Cells(x_lines+4+yweight[0],6).Value='Column='
  sh.Cells(x_lines+4+yweight[0],7).Value=minvalue[which_value][2]+1
  sh.Cells(x_lines+4+yweight[0],4).Value='Line='
  sh.Cells(x_lines+4+yweight[0],5).Value=minvalue[which_value][1]+1  
  
        
 
excel(0,0)
warn=lambda version: showwarning(title=version,message='Job Concluded\nreport a bug:ke.wang@sinowealth.com')
Tk().withdraw()
warn('hspreader 0.0.1a')