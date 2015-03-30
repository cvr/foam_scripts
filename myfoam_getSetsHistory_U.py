#!/usr/bin/python3.4
#author:shawn
#date:Oct 12, 2014
#This script should be excuted in current case directory. It can abstract the velocity sampled by cloud points to corresponding history. The results are located in './postProcessing/history'.

import os
import csv
import re
#directory to process
path="./postProcessing/sets"
filename='velocity_sample1_U.csv'

def mysort(tobesorted):
  """This function sort a list of float in ascending order."""
  for i in range(len(tobesorted)):
    for j in range(i,len(tobesorted)):
      if tobesorted[i]>tobesorted[j]: 
        swap=tobesorted[i]
        tobesorted[i]=tobesorted[j]
        tobesorted[j]=swap

def getfilelist():
  """return a list containing the name of the time files, in ascending order and in type of string. E.g ['0','0.05','0.1'...]."""
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
  """return a list of directories containing the data in ascending order, ordered by value of file names. The elements of the list are strings"""
  list = getfilelist() 
  for i in range(len(list)):
    list[i]=(path+'/'+list[i]+'/'+filename)
  return list

def deletefstline(pathlist):
  #The first line of U data files contains unreadable characters, so it need to be deleted. And new file is written in the same directory with a suffix of .new.csv
  #Taking a list of full path as input, this function not only generate new files, but also return new list of path pointing to new files. 
  print ("\n\n////////////////////Called deletefstline().///////////////////////////\n\n")
  newpathlist=[]
  for path in pathlist:
    file = open(path,encoding = 'utf-8',errors='ignore')
    if file.closed:
      print("failed to open the file.")
    lines = file.readlines()
    file.close()
    file = open (path+'.new.csv','w') #write to a new file
    for line in lines:
      if re.match(r'\D',line):
        print ("  Deleted the line:\n","    ",line,"  in:",path)
        continue 
      #print(line)
      file.write(line)
    file.close()
    newpathlist = newpathlist + [path+'.new.csv']
  return newpathlist
  
  
   
def getNofPts():
  #This function returns the number of sampled points
  csv_tmp = open('./postProcessing/sets/0/'+filename,encoding = 'utf-8',errors='replace')
  if csv_tmp.closed:
    print("failed to open the file.")
  lines = csv_tmp.readlines()
  No = 0 
  for line in lines:
      No += 1
  return No-1

#################################################################################################
#main part
Nopts=getNofPts()#Find out how many points are sampled.
filelist=getfilelist()#A list containing the name of time directories. E.g. ['0','0.05','0.1',...]
pathlist=getpathlist()#A list containing the full path of the file to be processed in each time directory. 
newpl=deletefstline(pathlist)#New:A list containing the full path of the file to be processed in each time directory. 
if not(os.access('./postProcessing/history',os.F_OK)):
  os.mkdir('./postProcessing/history')
else:
  print("\n\n")
  print("///////////////////////////////////////"*4)
  print("Warning! The directory, './postProcessing/history', already exist!!\n\n")
  print("///////////////////////////////////////"*4)
  print("\n\n")


#Create a list containing new files to be written
newfile=[]
for i in range(Nopts):
  newfile.append(open('./postProcessing/history/'+filename+'.point_'+str(i)+'.csv','w'))

pos2=0
for path in newpl:
  file = open(path,'r')
  print ("Processing the following file:\n",path)
  if (file.closed):
    print( "failed to open the file!")
  #print(file.name)
  lines = file.readlines() 
  flag = 0
  for line in lines:
    time = filelist[newpl.index(path)]
    line = time +','+line
    newfile[flag].write(line)
    flag += 1
  
'''
  for j in range(len(results[i])):
    file.write(results[i][j])
'''

