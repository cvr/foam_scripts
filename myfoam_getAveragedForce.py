#!/sw/epd-7.3-2/bin/python

import numpy as np
import csv
import sys

force_file=open('./postProcessing/forces.csv','r') 
reader=csv.reader(force_file) 
list=[]
for row in reader:
    #sys.exit()

    force1=float(row[1])+float(row[4]) #total force in x direction
    list.append(force1)
force=np.array(list)
#force=force.astype(np.float)
force=force[1000:]#before 1000, force may be not steady
average=np.average(force)
std=np.std(force)
output_path= '../../forces_analysis'
output=open(output_path,'a')#append to file

import subprocess
output.write('case: '+subprocess.check_output(['pwd']).strip('\n')+'\n')
output.write('Averaged force = '+str(average)+'\n')
output.write('Standard derivation of force = '+str(std)+'\n'*2)


    
