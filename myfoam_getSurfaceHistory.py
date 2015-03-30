#!/usr/bin/python
#author:shawn
#date:Dec 1, 2014
#This script should be excuted in current case directory.

import os
import csv
import re
#directory to process
path="./postProcessing/freeSurface"
filename='alpha1_freeSurface.raw'#name of the file that contain input data
outputFileName='waveHeightHistoryAlongALine.csv'#name of the file that contain output data 

def mysort(tobesorted):
  'This function sort a list of float in ascending order.'
  for i in range(len(tobesorted)):
    for j in range(i,len(tobesorted)):
      if tobesorted[i]>tobesorted[j]: 
        swap=tobesorted[i]
        tobesorted[i]=tobesorted[j]
        tobesorted[j]=swap

def getfilelist():
  #'return a list containing the name of the time files, in type of string. E.g ['0','0.05','0.1'...].'
  list=[];
  for file in os.listdir(path):
    num = float(file)
    if num%1 == 0:#if num does not contain a decimal, do not add '.0' part after it.
      num = int(num)
    list = list + [num]
  mysort(list)
  for i in range(len(list)):
    list[i]=str(list[i])
  return list


def getpathlist():
  'return a list of directories containing the data in ascending order, ordered by value of file names. The element of the list is in the type of string'
  list = getfilelist() 
  for i in range(len(list)):
    list[i]=(path+'/'+list[i]+'/'+filename)
  return list


#################################################################################################
#main part
filelist=getfilelist()#A list containing the name of time directories. E.g. ['0','0.05','0.1',...]
pathlist=getpathlist()#A list containing the full path of the file to be processed in each time directory. 
if not(os.access('./postProcessing/history',os.F_OK)):
  os.mkdir('./postProcessing/history')
else:
  print "\n\n"
  print "///////////////////////////////////////"*4
  print "Warning! The directory, './postProcessing/history', already exist!!\n\n"
  print "///////////////////////////////////////"*4
  print "\n\n"


outputfile=open('./postProcessing/history/'+outputFileName,'w')
timeNo=0
for path in pathlist:#approach the data in each time-step directories, find what I need and write them into outputfile.
  file = open(path,'r')
  print "Processing the following file:\n",path
  if (file.closed):
    print "failed to open the file!"
  for line in file:
    items=line.split()
    if items[0] == '#':#skip the comment lines
      continue
    if abs(float(items[1])-0) < 0.0002:
      results = filelist[timeNo]+','+str(items[0])+','+str(items[1])+','+str(items[2])+'\n'
      #The columns from left to right represent time, x coords, y coords and y coords.
      outputfile.write(results)
  timeNo+=1
  file.close()


