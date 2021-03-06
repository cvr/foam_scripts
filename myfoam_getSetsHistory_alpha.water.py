#!/usr/bin/python
#author:shawn
#date:Oct 12, 2014

import os
import csv
import sys,getopt
#input file should be obained with sample utility. (interpolation scheme should be cell)
#Algorithms to get wave height:
#1: sweep from top to bottom to get free surface position, which is defined as wave height; 
#2: sweep from bottom to top to get free surface; 
#3: integrate in upright direction to get wave height
method = 1

#DO NOT edit code below
################################################################################
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
  for file in os.listdir(path+'/sets'):
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
    list[i]=(path+'/sets/'+list[i]+'/'+filename)
  return list

####################################################################################################
#main part
def main(argv,input_filename,input_path):
    default_filename = True
    default_path = True
    try:
        opts, args = getopt.getopt(argv,"i:p:m:",["ifile=","ipath=","method="])
       #opts is a list of (option, value) pairs. 
       #args is the list of program arguments left after the option list was stripped.
    except getopt.GetoptError:
       print 'invalid options'
       print 'myfoam_getSetsHistory_U -i <input file name> -p <input file path> -m <method number>'
       print 'Example: myfoam_getSetsHistory_alpha.water.py -m 2 -i wavegauge1_alpha1.csv -p ./postProcessing_sample_at_cell_center'
       sys.exit(2)
    for opt, arg in opts:
       if opt in ("-i", "--ifile"):
          filename = arg
          default_filename = False
       elif opt in ("-p", "--ipath"):
          path = arg
          default_path = False
       elif opt in ("-m", "--method"):
           method = int(arg)
           if not method in (1,2,3):
               print 'invalid options'
               print 'myfoam_getSetsHistory_U -i <input file name> -p <input file path> -m <method number>'
               print 'method number should be 1, 2 or 3'
               print '#1: sweep from top to bottom to get free surface position, which is defined as wave height;' 
               print '#2: sweep from bottom to top to get free surface;' 
               print '#3: integrate in upright direction to get wave height'
           print "Select method: " + str(method) + ', which is: '
    if default_filename == True:
        filename = input_filename
    if default_path == True:
        path = input_path

    if method == 2:
        print "sweep from bottom to top to look for interface"
        m_name = 'bottomToTop'
    elif method == 1:
        print "sweep from top to bottom to look for interface"
        m_name = 'topToBottom'
    elif method == 3:
        print "integrate to get wave height to look for interface"
        m_name = 'integrate'
    else: 
        print "incorrect setup for sweeping direction"
        sys.exit()
    print "name of input files:",filename
    print "input file path:",path


    results=[['time','waveheight']]
    # csvfile = open('./postProcessing/history_'+m_name+'_'+filename,'w')
    csvfile = open(path+'/history_'+m_name+'_'+filename,'w')
    writer=csv.writer(csvfile,delimiter=',')
    filelist=getfilelist()
    pathlist=getpathlist(filename)    
    flag=0

    for path in pathlist:
      try:
          file = open(path,'r')
      except IOError:
          print "Failed to open the file: ",path
          print "It may not exist."
          print "Ignored this time file"
          flag+=1
          continue
      #print(file.name)
      reader=csv.reader(file) 
      if method ==2:#sweep from bottom to top
          first_loop = True
          for row in reader:
            if row[0]=='distance':
              continue

            if first_loop == True:#In first loop, do not interpolate
              dist1=float(row[0])
              alpha1=float(row[1])
              first_loop = False
              if alpha1<0.5:#alpha1 in first cell is less than 0.5 => water depth = 0 &
                #(in fact, output is distance listed in first row)
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
              break
            #These two variables store current line for next iteration.
            dist1=dist2
            alpha1=alpha2

          flag+=1
      elif method == 1:#sweep from top to bottom
          first_loop = True
          for row in reversed(list(reader)):
              if row[0]=='distance': #reached first row. Water depth should be 0
                  if first_loop != True:
                      writer.writerow([filelist[flag],dist1]) 
                  else:
                      print "Warning! There may be no data in file: " + path
                  break
              if first_loop == True:#In first loop, do not interpolate
                  dist1=float(row[0])
                  alpha1=float(row[1])
                  first_loop = False
                  if alpha1>0.5:#alpha1 in first cell is larger than 0.5 => water depth = height of domain &
                      #(in fact, output is distance listed in last row)
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
                break
              #These two variables store current line for next iteration.
              dist1=dist2
              alpha1=alpha2

          flag+=1
      elif method == 3:#integrate in z direction to get wave height
          first_loop = True
          h = 0
          for row in reader:
            if row[0]=='distance':
              continue

            if first_loop == True:#In first loop, do not interpolate
              dist1=float(row[0])
              alpha1=float(row[1])
              h = h + dist1
              first_loop = False
              #if alpha1<0.5:#alpha1 in first cell is less than 0.5 => water depth = 0 &
              #  #(in fact, output is distance listed in first row)
              #  writer.writerow([filelist[flag],dist1]) 
              #  break
              continue

            dist2=float(row[0])
            alpha2=float(row[1])
            h = h + (dist2-dist1)*alpha1
            dist1=dist2
            alpha1=alpha2
          writer.writerow([filelist[flag],h]) 
          flag+=1
      else: 
          print "incorrect setup for sweeping direction"
          sys.exit()
    print "Finished.\n"

#main part
#directory to process
path="./postProcessing"
#This is the default filename in each time directories.
filename='origin_alpha.water.csv'
main(sys.argv[1:],filename,path)
