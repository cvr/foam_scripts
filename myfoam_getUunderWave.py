#!/sw/epd-7.3-2/bin/python
#author:shawn
#date:Oct 12, 2014
#This script should be excuted in current case directory. 
#It can output velocity time history at specified depth or at depth varying with wave height.

import os,pdb,sys,getopt
import csv
import re
import numpy as np
import codecs

def usage():
    print "USAGE: myfoam_getSetsHistory_U.py -i <input file> -r <name of wave height file as reference> -p <path of input files>"
    print "       -p option is optional"
    print "       wave height file should be put in ./postProcessing/"
    print "       example:"
    print "       myfoam_getSetsHistory_U.py -i a1_U.csv -p ./postProcessing/sets -r history_a1_alpha.water.csv"
    print "       Please also check the options at the end of this file"

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


def getpathlist(filename):
  """return a list of directories containing the data in ascending order, ordered by value of file names. The elements of the list are strings"""
  list = getfilelist() 
  for i in range(len(list)):
    list[i]=(path+'/'+list[i]+'/'+filename)
  return list

  
   
def getNofPts(time,filename):
  #This function returns the number of sampled points
  csv_tmp = codecs.open('./postProcessing/sets/'+time+'/'+filename,encoding = 'utf-8',errors='replace')
  #print "filename in getNofPts(): ",filename
  if csv_tmp.closed:
    print"failed to open the file."
  lines = csv_tmp.readlines()
  No = 0 
  for line in lines:
      No += 1
  return No-1

def interpolate(x,f):
    #y=f(x). f is a numpy array with 1st column as x, 2nd column as y.
    #given x, return y=f(x) by interpolation. y should be a monotonic func of x
    if ( (x-f[0,0])*(x-f[-1,0]) ) > 0:#x is not in proper range 
        print "x is not in proper range"
        sys.exit()
    x1 = f[0,0]
    y1 = f[0,1]
    for i,item in enumerate(f):
        if x == item[0]:#don't need interpolate
            y = item[1]
            break

        if i == 0:#skip first loop
            continue
        else:
            x2 = item[0]
            y2 = item[1]

        if ( ( (x2-x)*(x1-x) )<0 ):
            y = float((y2-y1))/(x2-x1)*(x-x1)+y1
            break
        x1 = x2
        y1 = y2
    return y
#testing interpolate func
#x = np.linspace(0,10,11)
#y = x**2+3
#f = np.vstack((x,y))
#f = f.transpose()
#print interpolate(5.0,f)

def main(argv,input_filename,input_path,input_waveheight,options):
    default_filename = True
    default_path = True
    default_wh = True
    #pdb.set_trace()
    try:
        opts, args = getopt.gnu_getopt(argv,"i:p:r:h",["ifile=","ipath=","iwaveheight=","help"])
       #opts is a list of (option, value) pairs. 
       #args is the list of program arguments left after the option list was stripped.
    except getopt.GetoptError:
       print 'invalid options'
       usage()
       sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            filename = arg
            default_filename = False
        elif opt in ("-p", "--ipath"):
            path = arg
            default_path = False
        elif opt in ("-r","--iwaveheight"):
            waveheight_file = arg
            default_wh = False
        else:
            print "wrong input argument"
            usage()
            sys.exit()
            
       

    #if it did not get -i or -p or -r from command line:
    if default_filename == True:
        filename = input_filename
    if default_path == True:
        path = input_path
    if default_wh == True:
        waveheight_file = input_waveheight


    print "name of input files:",filename
    print "input file path:",path
    print "wave height file as reference:","./postProcessing/"+waveheight_file
    filelist=getfilelist()#A list containing the name of time directories. E.g. ['0','0.05','0.1',...]
    print "Time file list: ",filelist
    Nopts=getNofPts(filelist[0],filename)#Find out how many points are sampled.
    pathlist=getpathlist(filename)#A list containing the full path of the file to be processed in each time directory. 
    #print pathlist
    if not('history' in os.listdir('./postProcessing')):
      os.mkdir('./postProcessing/history')
    if not(filename in os.listdir('./postProcessing/history')):
      os.mkdir('./postProcessing/history/'+filename)
    print "Output will be output into: ./postProcessing/history/"+filename+"/"+"u_at_varying_depth.csv"
    


#Create a list containing new files to be written
    #newfile=[]# a list of files to be written into
    #for i in range(Nopts):
    #  newfile.append(open('./postProcessing/history/'+filename+'/point_'+str(i)+'.csv','w'))
    #print 'No. of output files: ',len(newfile)

    output = open('./postProcessing/history/'+filename+'/u_at_varying_depth.csv','w')
    h=np.genfromtxt('./postProcessing/'+waveheight_file, dtype=float, delimiter=',', skip_header=0)
    if h.shape[0] != len(filelist):
        print "number of times in h is not equal to that in postProcessing/sets. This wave height time history file is not compatible with current case"
        usage()
        sys.exit()
    for i,path in enumerate(pathlist):#eg. ./postProcessing/sets/40/a1_U.csv

        #d is distance to the bottom
        #pdb.set_trace()
        if options['mode'] == 0:
            d = options['d']
            if d > h[i,1]:
                d = h[i,1]*options['compress']
        elif options['mode'] == 1:
            d = h[i,1]*options['compress']
        else:
            print "cannot recognize the options in options['mode']"
            usage()
            sys.exit()
      
        #file = open(path,'r')
        #if (file.closed):
        #    print "failed to open the file!"

        u_d=np.genfromtxt(path, dtype=float, delimiter=',', skip_header=1)
        u_d = u_d[:,0:2]

        #lines = file.readlines() 
        if d < u_d[0,0]:#d is lower than first sampling point
            u = 0.0
        else:
            u=interpolate(d,u_d)#u at this depth
        time = filelist[i]
        line = time +','+str(d)+','+str(u)+'\n'
        output.write(line)
        #flag = 0
        #for line in lines:
        #    if line.startswith(tuple('0123456789')): # if starts with number
        #        time = filelist[pathlist.index(path)]
        #        line = time +','+line
        #        newfile[flag].write(line)
        #        flag += 1
  

#################################################################################################
#main part
#default directory and file to process
path="./postProcessing/sets"
filename='a1_U.csv'
waveheight_file = 'history_a1_alpha.water.csv' #path to file store time history of wave height
#end default setting
options = {}
options['mode'] = 1#0: sample velocity at constant depth; 1: sample velocity at varying depth based on wave height
options['d'] = 0.05#if options['mode'] = 0, this is the constant depth where velocity is sampled
options['compress'] = 0.8 #u is sampled at (distance from bottom) = waveheight*compress. 

main(sys.argv[1:],filename,path,waveheight_file,options)
#except:
#    print "Something went wrong."
#    usage()
#    print "Exit with error."
#else:
#    print "finished."



