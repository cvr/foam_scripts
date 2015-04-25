#!/usr/bin/python
#author:shawn
#date:Oct 12, 2014

import os
import csv
import sys,getopt
#directory to process
path="./postProcessing/sets"
#This is the filename in each time directories.
filename='origin_alpha.water.csv'

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


def getpathlist(filename):
  'return list of full paths of the csv files to be processed, ordered by value of the names of time files containing them. The element of the list is in the type of string'
  list = getfilelist() 
  for i in range(len(list)):
    list[i]=(path+'/'+list[i]+'/'+filename)
  return list

####################################################################################################
#main part
def main(argv,input_filename,input_path):
    default_filename = True
    default_path = True
    try:
       opts, args = getopt.getopt(argv,"i:p:",["ifile=","ipath="])
       #opts is a list of (option, value) pairs. 
       #args is the list of program arguments left after the option list was stripped.
    except getopt.GetoptError:
       print 'invalid options'
       print 'myfoam_getSetsHistory_U -i <input file name> -p <input file path>'
       sys.exit(2)
    for opt, arg in opts:
       if opt in ("-i", "--ifile"):
          filename = arg
          default_filename = False
       elif opt in ("-p", "--ipath"):
          path = arg
          default_path = False
    if default_filename == True:
        filename = input_filename
    if default_path == True:
        path = input_path


    print "name of input files:",filename
    print "input file path:",path

    results=[['time','waveheight']]
    csvfile = open('./postProcessing/history_'+filename,'w')
    writer=csv.writer(csvfile,delimiter=',')
    filelist=getfilelist()
    pathlist=getpathlist(filename)    
    flag=0

    for path in pathlist:
      file = open(path,'r')
      if (file.closed):
        print "failed to open the file!"
      #print(file.name)
      reader=csv.reader(file) 
      first_loop = True
      for row in reader:
        if row[0]=='distance':
          continue
        if first_loop == True:#In first loop, do not interpolate
          dist1=float(row[0])
          alpha1=float(row[1])
          first_loop = False
          if alpha1<0.5:#alpha1 in first cell is less than 0.5 => water depth = 0
            writer.writerow([filelist[flag],dist1]) 
            break
          continue
        dist2=float(row[0])
        alpha2=float(row[1])
        #Define the water surface as where alpha1==0.5 and get the z coordinate value of that point by interpolation.
        if ((alpha1-0.5)*(alpha2-0.5))<0:
          waveheight=(dist1-dist2)/(alpha1-alpha2)*0.5+(alpha1*dist2-alpha2*dist1)/(alpha1-alpha2)
          writer.writerow([filelist[flag],waveheight]) 
          #results=results+[[filelist[flag],row[0]]]    
          write_status = True
          break
        #These two variables store current line for next iteration.
        dist1=dist2
        alpha1=alpha2

      flag+=1

#main part
main(sys.argv[1:],filename,path)
