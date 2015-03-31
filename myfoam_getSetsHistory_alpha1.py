#!/usr/bin/python
#author:shawn
#date:Oct 12, 2014

import os
import csv
#directory to process
path="./postProcessing/sets"
#This is the filename in each time directories.
filename='origin_alpha1.csv'

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

####################################################################################################
#main part

results=[['time','waveheight']]
csvfile = open('./postProcessing/history_'+filename,'w')
writer=csv.writer(csvfile,delimiter=',')
filelist=getfilelist()
pathlist=getpathlist()    
flag=0

for path in pathlist:
  file = open(path,'r')
  if (file.closed):
    print "failed to open the file!"
  #print(file.name)
  reader=csv.reader(file) 
  alpha1=1
  dist1=1
  for row in reader:
    if row[0]=='distance':
      continue
    dist2=float(row[0])
    alpha2=float(row[1])
    #Define the water surface as where alpha1==0.5 and get the z coordinate value of that point by interpolation.
    if ((alpha1-0.5)*(alpha2-0.5))<0:
      #print(row)
      waveheight=(dist1-dist2)/(alpha1-alpha2)*0.5+(alpha1*dist2-alpha2*dist1)/(alpha1-alpha2)
      writer.writerow([filelist[flag],waveheight]) 
      #results=results+[[filelist[flag],row[0]]]    
      break
    #These two variables store current line for next iteration.
    dist1=dist2
    alpha1=alpha2
  flag+=1


