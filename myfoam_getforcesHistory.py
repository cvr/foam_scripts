#!/usr/bin/python
#author:shawn
#date:Nov 04, 2014
#updated for python2.7 on 04/21/2015

import os
import csv
import re

######################################################################
#input start
#directory to process
path="./postProcessing/forces"
#This is the filename in each time directories.
filename='forces.dat'
#end of input
######################################################################


######################################################################
#do not modify contents below

def mysort(tobesorted):
  'This function sort a list of floating numbers in ascending order.'
  for i in range(len(tobesorted)):
    for j in range(i,len(tobesorted)):
      if tobesorted[i]>tobesorted[j]: 
        swap=tobesorted[i]
        tobesorted[i]=tobesorted[j]
        tobesorted[j]=swap

def getfilelist():
  'This function return a list of the time files in ascending order.'
  #The returned list is a list of string type
  list=[];
  for file in os.listdir(path):
    num = float(file)
    if num%1 == 0:#if num does not contain a decimal, do not add '.0' part after it.
      num = int(num)
    list = list + [num]
  mysort(list)
  for i in range(len(list)):
    list[i] = str(list[i])
  return list

def getpathlist():
  'return list of full paths of the csv files to be processed, ordered by value of the names of time files containing them. The element of the list is in the type of string'
  list = getfilelist() 
  for i in range(len(list)):
    list[i]=(path+'/'+list[i]+'/'+filename)
  return list

######################################################################
#main part

tobewritten = open('./postProcessing/forces.csv','w')
filelist=getfilelist()
pathlist=getpathlist()#a list of string containing the full path of the file to be read. e.g. './postProcessing/1.2/forces2/forces.dat'
latestTime=0
for path in pathlist:
  file = open(path,'r')
  if (file.closed):
    print "failed to open the file!"

  for line in file:
    if not line.startswith("#"):#line that starts with "#" is a comment 
      line=re.sub(r'[\(\)\,\s]+',",",line)#Now line is a string of numbers.
      line=line[:-1]#delete the last character because there is a ',' there and I have not fix it.
      line=line+'\n'
      line=line.split(',')#Now line is a list of string of numbers
      if float(line[0])>float(latestTime):
        latestTime=line[0]
        line=','.join(line)#join the list to a string
        tobewritten.write(line) 
    
  file.close()
tobewritten.close()


