#!/sw/epd-7.3-2/bin/python
import numpy as np
import sys,os
from scipy import optimize
from math import pi
import matplotlib.pyplot as plt
from mylib_DictWriter import write_boundaryData_scalar,write_boundaryData_vector 

################################################################################
#user input start here

#general parameters
para={}
para['startTime']=0#start time
para['endTime']=1#end time
para['deltaT']=0.1#time step in ./constant/boundaryData/inlet_patch_name
para['x_inlet']=0#x coordinates of inlet plane
para['ymin_inlet']=-0.5#min y coordinates of inlet plane
para['ymax_inlet']=0.5#max y coordinates of inlet plane
para['zmin_inlet']=0#min z coordinates of inlet plane
para['zmax_inlet']=2#max z coordinates of inlet plane
para['nz']=50#must be integer
para['g']=9.8#gravity acceleration
para['log_path']='./'#path to save the log file for this code
para['inlet_patch_name'] = 'inlet'#./constant/boundaryData/inlet_patch_name

#parameters for wave
wave={}
wave['depth']=1#depth of water, h
wave['waveheight']=0.5#wave height, H
wave['omega']=2*pi#wave circular frequency, omega
wave['rho']=998.2#density of water
#wave['k']=0.5 #wave number is not independent of omega thus it should not be defined here


#user input end here
################################################################################

def generate_grid(para):#generate points on inlet plane
    if type(para['nz']) != int:
        print 'nz must be integer!'
        sys.exit()
    x=np.zeros(para['nz']*2)+para['x_inlet']
    y1=np.zeros(para['nz'])+para['ymin_inlet']
    y2=np.zeros(para['nz'])+para['ymax_inlet']
    y=np.append(y1,y2)
    z1=np.linspace(para['zmin_inlet'],para['zmax_inlet'],para['nz'])
    z=np.append(z1,z1)
    points=np.vstack((x,y,z))
    points=np.transpose(points)
    return points#return a numpy array. each row is xyz coordinates of a points on the plane

def get_k(para,wave):#compute wave number from omega
    from math import tanh
    depth=wave['depth']
    g=para['g']
    omega=wave['omega']
    def dispersion(k,omega,depth,g):
        return g*k*tanh(k*depth)-omega**2
    max_root=1000
    return optimize.brentq(dispersion,0,max_root,args=(omega,depth,g))#return wave number k

#main
log_file=open(para['log_path']+'myfoam_write_boundaryData.log','w')
wave['k']=get_k(para,wave)
log_file.write('Compute wave number, k, from frequency, omega. k='+str(wave['k'])+'\n') 
points=generate_grid(para) #generate points on inlet plane
log_file.write( 'points on inlet patch: \n'+str(points)+'\n')
write_boundaryData_vector(points,'','points',para,foam_class='vectorField',foam_object='points') #write points file to ./constant/boundaryData
t_list=np.arange(para['startTime'],para['endTime'],para['deltaT'])
t_list=np.append(t_list,para['endTime'])#append endTime to the end of array
log_file.write( 'time files to be created: \n'+str(t_list)+'\n')
from math import pi
phase_shifted=-pi/2
eta_list=0.5*wave['waveheight']*np.cos(-wave['omega']*t_list+phase_shifted)#add -pi/2 so that eta=0 at t=0
log_file.write( 'wave height: \n'+str(eta_list)+'\n')
depth_list=eta_list+wave['depth']#depth of water at inlet, varying with time
log_file.write( 'water depth at inlet: \n'+str(depth_list)+'\n')
log_file.write('\n\n')
log_file.write('#'*80+'n')
log_file.write('Create velocity and pressure for each time step:\n')
for i,t in enumerate(t_list):
    #if z coordinates in a row of points is smaller than eta, alpha_water should be 1 there and 0 otherwise.
    log_file.write( '\nt= '+str(t)+'\n')
    alpha_water=0.5*(np.sign(depth_list[i]-points[:,2])+1)#a list containing value of alpha.water in each cell on inlet patch
    log_file.write( 'alpha.water in each cell: \n'+str(alpha_water)+'\n')
    write_boundaryData_scalar(alpha_water,t,'alpha.water',para)
    u=0.5*wave['waveheight']*wave['omega']*np.cosh(wave['k']*(points[:,2]))/np.sinh(wave['k']*wave['depth'])*np.cos(-wave['omega']*t+phase_shifted)
    w=0.5*wave['waveheight']*wave['omega']*np.sinh(wave['k']*(points[:,2]))/np.sinh(wave['k']*wave['depth'])*np.sin(-wave['omega']*t+phase_shifted)
    v=points[:,2]*0#v is all zero
    log_file.write( 'u: \n'+str(u)+'\n')
    log_file.write( 'v: \n'+str(v)+'\n')
    log_file.write( 'w: \n'+str(w)+'\n')
    velocity=np.vstack((u,v,w))
    velocity=np.transpose(velocity)
    log_file.write( 'velocity:\n'+str(velocity)+'\n')
    write_boundaryData_vector(velocity,t,'U',para)
    #p=wave['rho']*para['g']*(-(points[:,2]-wave['depth'])+wave['waveheight']*0.5*np.cosh(wave['k']*(points[:,2]))/np.cosh(wave['k']*wave['depth'])*np.cos(-wave['omega']*t+phase_shifted))
    #p_rgh=wave['rho']*para['g']*(wave['waveheight']*0.5*np.cosh(wave['k']*(points[:,2]))/np.cosh(wave['k']*wave['depth'])*np.cos(-wave['omega']*t+phase_shifted))
    #log_file.write( 'p:\n'+str(p)+'\n')
    #log_file.write( 'p_rgh:\n'+str(p_rgh)+'\n')
    #write_boundaryData_scalar(p_rgh,t,'p_rgh',para)



    

