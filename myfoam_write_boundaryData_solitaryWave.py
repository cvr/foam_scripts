#!/sw/epd-7.3-2/bin/python
import numpy as np
import sys,os
#from scipy import optimize
from math import sqrt,tanh
import matplotlib.pyplot as plt
from mylib_DictWriter import write_boundaryData_scalar,write_boundaryData_vector 
import pdb

################################################################################
#user input start here

#general parameters
para={}
para['startTime']=0.0#start time. Should be 0 at this stage.
para['endTime']=15.0#end time
para['deltaT']=0.001#time step in ./constant/boundaryData/inlet_patch_name
para['x_inlet']=0.0#x coordinates of inlet plane
para['ymin_inlet']=-0.5#min y coordinates of inlet plane
para['ymax_inlet']=0.5#max y coordinates of inlet plane
para['zmin_inlet']=0.0#min z coordinates of inlet plane
para['zmax_inlet']=1.5#max z coordinates of inlet plane
para['nz']=400#number of cells in z direction. must be integer
para['g']=9.81#gravity acceleration
para['log_path']='./'#path to save the log file when execute this script 
para['inlet_patch_name'] = 'inlet'#./constant/boundaryData/inlet_patch_name

#parameters for solitary wave 
#all must be float number rather than int
wave={}
wave['depth']=1.0#depth of water
wave['waveheight']=0.11#wave height
wave['rho']=998.8#density of water
wave['initial_phase']=12.0#initial value of kX in sech^2(kX)


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

def get_c(para,wave):#compute wave celerity
    #from math import tanh
    from math import sqrt
    d = wave['depth']
    g = para['g']
    a = wave['waveheight']
    ep = a/d
    #return sqrt(g*d*(1+a/d)) #Boussinesq's solution
    return sqrt(g*d)*sqrt(1+ep-1./20*ep**2-3/70*ep**3)#Grimshaw's solution

def get_k(para,wave):#compute wave number
    #from math import tanh
    from math import sqrt
    depth = wave['depth']
    a = wave['waveheight']
    return sqrt((3*a)/(4*depth**3))

################################################################################
#main
#some functions to be used
sech = lambda x: (2*np.cosh(x))/(np.cosh(2*x)+1)

#initial check
if ('boundaryData' in os.listdir('./constant')):
    print "Warning!!\n Old boundaryData exist in ./constant."
    print "You may need to clean it before creating new data."

log_file = open(para['log_path']+'myfoam_write_boundaryData_solitaryWave.log','w')
wave['c'] = get_c(para,wave)
log_file.write('Compute wave celerity, c. c = '+str(wave['c'])+'\n') 
wave['k'] = get_k(para,wave)
log_file.write('Compute wave number, k. k = '+str(wave['k'])+'\n') 

#some abbreviated alias of the input parameters
a = wave['waveheight']
d = wave['depth']
g = para['g']
c = wave['c']
k = wave['k']

points = generate_grid(para) #generate points on inlet plane
log_file.write( 'points on inlet patch: \n'+str(points)+'\n')
write_boundaryData_vector(points,'','points',para,foam_class = 'vectorField',foam_object = 'points') #write points file to ./constant/boundaryData
t_list = np.arange(para['startTime'],para['endTime'],para['deltaT'])
t_list = np.append(t_list,para['endTime'])#append endTime to the end of array
log_file.write( 'time files to be created: \n'+str(t_list)+'\n')
#from math import pi
phase_shifted = wave['initial_phase']-k*(para['x_inlet']-c*para['startTime'])

#Boussinesq's solution
#eta_list = a*(sech(k*(para['x_inlet']-c*t_list+phase_shifted)))**2#use phase_shifted so that at startTime eta = 0

#Grimshaw's solution
ep = a/d
alpha = sqrt(3./4*ep)*(1-5./8*ep+71./128*ep**2)
s = sech(alpha*(para['x_inlet']-c*t_list+phase_shifted)/d)
#pdb.set_trace()
q = np.tanh(alpha*(para['x_inlet']-c*t_list+phase_shifted)/d)
eta_list = d*(ep*s**2-3./4*(ep*s*q)**2+ep**3*(5./8*s**2*q**2-101./80*s**4*q**2))

#pdb.set_trace()
#plot eta_list
plt.figure()
plt.plot(t_list,eta_list,'rx',label='wave height')
legend = plt.legend(loc='upper center', shadow=True, prop={'size':7})
#plt.xlim(3.0,4.0)
plt.xlabel('time (s)')
plt.ylabel('wave height (m)')
plt.title('wave height history at inlet')
if not('myplot' in os.listdir('./')):
    os.mkdir('myplot')
plt.savefig('./myplot/waveheight_at_inlet.png', bbox_inches='tight')
plt.close()

log_file.write( 'wave height: \n'+str(eta_list)+'\n')
depth_list = eta_list+d#depth of water at inlet, varying with time
log_file.write( 'water depth at inlet: \n'+str(depth_list)+'\n')
log_file.write('\n\n')
log_file.write('#'*80+'n')
log_file.write('Create velocity U and alpha.water at inlet for each time step:\n')

u_history_1 = np.zeros(t_list.shape[0]) #z/d = 1.05
u_history_2 = np.zeros(t_list.shape[0]) #z/d = 0.45
w_history_1 = np.zeros(t_list.shape[0]) #z/d = 1.05
w_history_2 = np.zeros(t_list.shape[0]) #z/d = 0.45

for i,t in enumerate(t_list):
    print 't = ',t
    #if z coordinates in a row of points is smaller than eta, alpha_water should be 1 there and 0 otherwise.
    log_file.write( '\nt = '+str(t)+'\n')
    alpha_water = 0.5*(np.sign(depth_list[i]-points[:,2])+1)#a list containing value of alpha.water in each cell on inlet patch
    n1 = 0
    for n in range(alpha_water.size): #compute how many cells have value alpha.water=1 AT ONE COLUMN
        if alpha_water[n] > 0:
            n1=n1+1
            continue
        else:
            break
    n2 = para['nz'] - n1
    log_file.write( 'alpha.water in each cell: \n'+str(alpha_water)+'\n')
    write_boundaryData_scalar(alpha_water,t,'alpha.water',para)

    #compute u
    eta = eta_list[i] #wave height at this time 
    phase = para['x_inlet']-c*t+phase_shifted #X = x - ct + phase_shifted
    #eq. 5 in Lee 1982, Boussinesq's solution
    #{
    #ep = a/d
    #etas = eta/a
    #etas2_t2 = 4*(c**2)*(k**2)*(np.tanh(k*phase)**2)*(sech(k*phase)**2)-2*(c**2)*(k**2)*sech(k*phase)**4
    #u = sqrt(g*d)*ep*(etas-0.25*ep*etas**2+1./3*d**2/c**2*(1-1.5*(points[:,2]/d)**2)*(etas2_t2))
    #}

    #Grimshaw's solution
    #{
    s = sech(alpha*(para['x_inlet']-c*t+phase_shifted)/d)
    q = tanh(alpha*(para['x_inlet']-c*t+phase_shifted)/d)
    u = sqrt(g*d)*(ep*s**2-ep**2*(-1./4*s**2+s**4+(points[:,2]/d)**2*(1.5*s**2-9./4*s**4)) -ep**3*(19./40*s**2+1./5*s**4-6./5*s**6+(points[:,2]/d)**2*(-1.5*s**2-15./4*s**4+15./2*s**6)+(points[:,2]/d)**4*(-3./8*s**2+45./16*s**4-45./16*s**6)) )
    #}

    #u = eta/d*sqrt(g*d)*( 1-0.25*eta/d + d/3*d/eta*(1-1.5*(points[:,2]-d)**2/d**2) * (2*a* k**2 * (np.cosh(2*k*phase)-2) * (sech(k*phase))**4 ))
    #u = c/sqrt(g*a) * ( (a/d+3*(a/d)**2 * (1/6.-1/2.*((points[:,2]-d)/d)**2)) * eta/a - (a/d)**2*(7/4.-9/4.*((points[:,2]-d)/d)**2)*(eta/a)**2 )
    u=u*alpha_water#u in all cells above free surface are set to zero
    u[n1:para['nz']]=u[n1-1]#u in all cells above free surface are set to equal to velocity of water at the free surface 
    u[para['nz']+n1:]=u[para['nz']+n1-1]#u in all cells above free surface are set to equal to velocity of water at the free surface 

    #compute w
    #w= -1*(points[:,2]-d)/d*sqrt(g*d)* ((1-0.5*eta/d)* (-2*a*k*np.tanh(k*phase)*(sech(k*phase))**2) + 1./3.*d**2*(1-0.5 * (points[:,2]-d)**2/d**2) * (a* (16* k**3 * np.tanh(k*phase) * (sech(k*phase))**4 - 8* k**3 * (np.tanh(k*phase))**3 * (sech(k*phase))**2 ) ) )
    #Grimshaw's solution
    #{
    w = -1*sqrt(g*d)*sqrt(3*ep)*(points[:,2]/d)*q*(-1*ep*s**2+ep**2*(3./8*s**2+2*s**4+(points[:,2]/d)**2*(0.5*s**2-3./2*s**4))+ep**3*(49./640*s**2-17./20*s**4-18./5*s**6+(points[:,2]/d)**2*(-13./16*s**2-25./16*s**4+15./2*s**6)+(points[:,2]/d)**4*(-3./40*s**2+9./8*s**4-27./16*s**6)))
    #w = sqrt(g*d)*sqrt(3*ep)*(points[:,2]/d)*q*(-1*ep*s**2+ep**2*(3./8*s**2+2*s**4+(points[:,2]/d)**2*(0.5*s**2-3./2*s**4))+ep**3*(49./640*s**2-17./20*s**4-18./5*s**6+(points[:,2]/d)**2*(-13./16*s**2-25./16*s**4+15./2*s**6)))
    #}
    w=w*alpha_water#w in all cells above free surface are set to zero
    w[n1:para['nz']]=w[n1-1]#w in all cells above free surface are set to equal to velocity of water at the free surface 
    w[para['nz']+n1:]=w[para['nz']+n1-1]#w in all cells above free surface are set to equal to velocity of water at the free surface 

    #compute v
    v=points[:,2]*0#v is all zero
    log_file.write( 'u: \n'+str(u)+'\n')
    log_file.write( 'v: \n'+str(v)+'\n')
    log_file.write( 'w: \n'+str(w)+'\n')
    velocity=np.vstack((u,v,w))
    velocity=np.transpose(velocity)
    log_file.write( 'velocity:\n'+str(velocity)+'\n')
    write_boundaryData_vector(velocity,t,'U',para)

    ##plot velocity-u field
    #plt.figure()
    #plt.plot(points[:,2],u/sqrt(g*d),'rx',label='velocity-u')
    #legend = plt.legend(loc='upper center', shadow=True, prop={'size':7})
    #plt.ylim(-0.1,0.2)
    #plt.xlabel('z (m)')
    #plt.ylabel('velocity-u (m/s)')
    #plt.title('velocity-u distribution at inlet')
    #if not('myplot' in os.listdir('./')):
    #    os.mkdir('myplot')
    #plt.savefig('./myplot/distribution_velocity-u_at_t='+str(t)+'.png', bbox_inches='tight')
    #plt.close()

    #get u histories at some depths
    u_history_1[i] = u[34]
    u_history_2[i] = u[14]
    #get w histories at some depths
    w_history_1[i] = w[34]
    w_history_2[i] = w[14]

#plot u histories
plt.figure()
plt.plot(t_list*sqrt(g/d),u_history_1/sqrt(g*d),'r-',label='velocity-u')
plt.plot(t_list*sqrt(g/d),u_history_2/sqrt(g*d),'b-',label='velocity-u')
legend = plt.legend(loc='upper center', shadow=True, prop={'size':7})
plt.ylim(-0.1,0.2)
plt.xlabel('t (s)')
plt.ylabel('velocity-u (m/s)')
plt.title('velocity-u history at inlet')
if not('myplot' in os.listdir('./')):
    os.mkdir('myplot')
plt.savefig('./myplot/velocity-u_history.png', bbox_inches='tight')
plt.close()

#plot w histories
plt.figure()
plt.plot(t_list*sqrt(g/d),w_history_1/sqrt(g*d),'r-',label='velocity-u')
plt.plot(t_list*sqrt(g/d),w_history_2/sqrt(g*d),'b-',label='velocity-u')
legend = plt.legend(loc='upper center', shadow=True, prop={'size':7})
plt.ylim(-0.04,0.04)
plt.xlabel('t (s)')
plt.ylabel('velocity-w (m/s)')
plt.title('velocity-w history at inlet')
if not('myplot' in os.listdir('./')):
    os.mkdir('myplot')
plt.savefig('./myplot/velocity-w_history.png', bbox_inches='tight')
plt.close()


    

