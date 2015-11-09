##a script to read in an STL file and output an XYZ file in z(x,y) mode (a set of points on a rectangular grid ). 
##author: Shawn Qin, Matt Yi
import numpy as np
import pdb
import matplotlib.pyplot as plt
import os


#a triangle object here is a 3x3 numpy array, usually named as tri.
#tri = np.array([[x1,y1,z1], \ 
#                [x2,y2,z2], \
#                [x3,y3,z3]])

#a point object here is a point on x-y plane and is a 1x2 numpy array, usually named as pt,
#pt = np.array([x, y])


def inside_tri(pt,tri):
    #a function to check if a point, pt, is inside a triangle, tri, in x-y plane
    #pt is (x,y) coordinate of the point being checked
    #tri is a triangle object containing coordinate infomation of its three vertices
    #algorithm used to determine if a arbitrary point P is inside a triangle defined by three points A, B, C:
    #Define the vectors AB, BC and CA and vectors AP, BP and CP. Then P is inside the triangle formed by A, B and C if and only if all of the cross products AB*AP, BC*BP and CA*CP point in the same direction relative to the plane. That is, either all of them point out of the plane, or all of them point into the plane. 
    #in this function we assume pt and tri are all in x-y plane 
    
    #pdb.set_trace()
    a = tri[0,:]
    b = tri[1,:]
    c = tri[2,:]
    p = np.array([pt[0],pt[1],0])
    ab = b-a
    bc = c-b
    ca = a-c
    ap = p-a
    bp = p-b
    cp = p-c
    abap = ab[0]*ap[1] - ab[1]*ap[0]  #z component of crossproduct(ab,ap)
    bcbp = bc[0]*bp[1] - bc[1]*bp[0]  #z component of crossproduct(bc,bp)
    cacp = ca[0]*cp[1] - ca[1]*cp[0]  #z component of crossproduct(ca,cp)
    if (abap*bcbp >= 0) and (bcbp*cacp >= 0):
        #all three z component have the same sign -> pt is inside tri 
        #if pt is on edge of the triangle, we still think it is 'inside' and return True
        return True
    else:
        return False
        

def get_z(pt, tri):
#for i,xx in enumerate(x):
#    for j,yy in enumerate(y):
#        pt = [xx,yy]
#        log.write("processing point: "+ str(pt)+ '\n')
#        z = get_z(pt,list_tri)
#        Z[j,i] = z
#        #write (x,y,z) to output
#        pt = str(xx)+' '+str(yy)+' '+str(z) +'\n'
#        output.write(pt)
    #given (x,y) of a point, pt, and a triangle with coordinates of its 3 vertices, tri
    #return z coordinate of the point if it is on the plane described by the triangle
    #this func will not check if pt is inside tri
    #first we project the triangle onto x-y plane to get a triangle on x-y plane. If pt(x_p,y_p) is inside the triangle on x-y plane (determined by the algorithm above), then we interpolate z(x_p,y_p) linearly from z value of three vertices of the triangle.
    x1 = tri[0,0]
    x2 = tri[1,0]
    x3 = tri[2,0]
    y1 = tri[0,1]
    y2 = tri[1,1]
    y3 = tri[2,1]
    z1 = tri[0,2]
    z2 = tri[1,2]
    z3 = tri[2,2]
    J = np.array([[1,x1,y1],[1,x2,y2],[1,x3,y3]])
    detj = np.linalg.det(J)
    #if detj = 0, that means the triangle is vertical to x-y plane
    #then we should just ignore it and return false
    #we will find another triangle with which we can process this point
    if abs(detj)<1e-10:
        return [0,False]
    else:
        x = pt[0]
        y = pt[1]
        z = (x2*y3-x3*y2+(y2-y3)*x+(x3-x2)*y)/detj*z1 + (x3*y1-x1*y3+(y3-y1)*x+(x1-x3)*y)/detj*z2 + (x1*y2-x2*y1+(y1-y2)*x+(x2-x1)*y)/detj*z3
        return [z,True]

##test inside_tri()
#pt = [0.5,0]
#tri = np.array([[0,0,0],[1,0,0],[1,0,1]])
##tri = np.array([[0,0,0], [2,0,0], [1,2,0]])
#print inside_tri(pt,tri)

##test get_z()
#tri = np.array([[0,0,0],[1,0,0],[1,0,1]])
#list_tri = [tri]
#pt = [0.5,0]
#z = get_z(pt,list_tri)
#print z


################################################################################
#main
#stlfile = './test.stl'
stlfile = 'seaside_whole_nofillet.stl'
outputfile = 'seaside.xyz'
logfile = stlfile+'.STLToXYZ.log'
try:
    stl = open('./'+stlfile,'r')
except IOError:
    print "Failed to open the file: ",stlfile
    exit()

try:
    log = open('./'+logfile,'w')
except IOError:
    print "Failed to open the file: ",logfile
    exit()

#extract all triangle information from stl file
list_tri = []
start = False
for line in stl:
    line = line.split()
    if line[0] == 'outer' and start == False:#start a new scanning
        start = True
        #initialize a new numpy array to represent coordinates of 3 vertices
        pts = np.empty([0,3])
        continue
    if start == True:
        if line[0] == 'vertex':
            pt = np.array([float(line[1]),float(line[2]),float(line[3])])
            pts = np.vstack((pts,pt))#stack coordinate of this point into pts
    if line[0] == 'endloop' and start == True: #finish scanning one triangle
        start = False
        list_tri.append(pts)

try:
    output = open('./'+outputfile,'w')
except IOError:
    print "Failed to open the file: ", output
    exit()

x0 = 32.5
xn = 43.6 
#xn = 39.8 
y0 = -13.2
yn = 8.5
dx = 0.01
dy = 0.01
bottom = 0.995 #z coordiante of the tank bottom. Points under this plane should not be used.
sea_level = 0.97
x = np.arange(x0,xn+dx/10.,dx)
y = np.arange(y0,yn+dy/10.,dy)
print "mesh size: nx = ", str(x.size),', ny = ',str(y.size)
totalpt = float(x.size*y.size)
status = np.zeros((y.size,x.size))#for tracking status of each point
#status[i,j] = 0: pt at (i,j) has not been processed
#status[i,j] = 1: pt at (i,j) has been processed
Z = np.zeros((y.size,x.size))
Z = Z + bottom

#pseudo code:
#for each triangle, tri:
#   get a list of grid pts, pts, in rectangle: xmin<x<xmax, ymin<y<ymax
#   for each pt in pts:
#       if status of pt is "unprocessed":
#           if pt is inside tri:
#               compute z of pt
#               mark pt as "processed"
count = 0#count number of pt being processed
for tri in list_tri:
    log.write("processing triangle: \n")
    log.write(str(tri)+ '\n')
    x1 = tri[0,0]
    x2 = tri[1,0]
    x3 = tri[2,0]
    y1 = tri[0,1]
    y2 = tri[1,1]
    y3 = tri[2,1]
    z1 = tri[0,2]
    z2 = tri[1,2]
    z3 = tri[2,2]
    xmin = min(x1,x2,x3)
    xmax = max(x1,x2,x3)
    ymin = min(y1,y2,y3)
    ymax = max(y1,y2,y3)
    imin = int((xmin-x0)/dx)#minimum index of the potential points in this triangle in list x 
    imax = int((xmax-x0)/dx)#maximum index of the potential points in this triangle in list x 
    jmin = int((ymin-y0)/dy)#minimum index of the potential points in this triangle in list y 
    jmax = int((ymax-y0)/dy)#maximum index of the potential points in this triangle in list y 
    imin = min(max(imin,0),x.size-1)
    imax = min(max(imax,0),x.size-1)
    jmin = min(max(jmin,0),y.size-1)
    jmax = min(max(jmax,0),y.size-1)
    print '%3.2f' % (count/totalpt*100) + " % complete..."
    for i in np.arange(imin, imax+0.1, 1): 
        for j in np.arange(jmin, jmax+0.1, 1): 
            pt = [x[i],y[j]]
            if status[j,i] == 0: #if unprocessed, check whether it's inside the tri
                if inside_tri(pt,tri):
                    log.write("    Processing point: "+ str(pt)+ '\n')
                    [z,done] = get_z(pt,tri)
                    #if abs(pt[0]-36.0) < 1e-2 and abs(pt[1]-0.5) < 1e-2: 
                    #    pdb.set_trace()
                    if done == True and z > (bottom-0.1):
                        Z[j,i] = z
                        status[j,i] = 1#mark as processed
                        log.write("    Marked as processed, point: "+ str(pt)+ "at row " + str(j)+ " and column " +str(i) +'\n')
                        #pdb.set_trace()
                        #write (x,y,z) to output
                        #todo xyz file should be written in a different sequence
                        pt = str(pt[0])+' '+str(pt[1])+' '+str(z) +'\n'
                        output.write(pt)
                        count = count + 1

#check if all pts has been processed
residual = np.amin(status)#minimum absolute value in status
if residual < 1e-10:
    print "Warning! Some points in the grid may have not been processed!"
    log.write("Warning! Some points in the grid may have not been processed!")
    log.write("These points have not been processed:\n")
    for i in range(status.shape[1]):
        for j in range(status.shape[0]):
            if abs(status[j,i]-0) < 1e-10:#this pt has not been processed
                pt = str(x[i])+' '+str(y[j]) +' '+str(Z[j,i]) 
                output.write(pt+'\n')#write pt that did not get value from stl
                log.write("point at row: "+ str(j)+ ", column: "+ str(i)+ ". status: "+str(status[j,i])+'\n')

#sort xyz data
import time
start_time = time.clock()

output.close()
data = np.loadtxt(outputfile, delimiter = ' ')
#pdb.set_trace()
index = np.lexsort((data[:,0],-data[:,1]))
data_sorted = data[index]
t_sort = time.clock() - start_time
print "CPU time used to sort: ", t_sort , '\n'
data_sorted[:,2] = data_sorted[:,2] - sea_level #sea level
t_substract = time.clock() - t_sort
print "CPU time used to substract: ", t_substract , '\n'
np.savetxt(outputfile, data_sorted,fmt = '%1.7f',delimiter = ' ')

#write x,y,z data in seperate file
np.savetxt(outputfile+'.x',x,fmt = '%1.8f',delimiter = ' ')
np.savetxt(outputfile+'.y',y,fmt = '%1.8f',delimiter = ' ')
np.savetxt(outputfile+'.z',Z-sea_level,fmt = '%1.8f',delimiter = ' ')





#plot colormap
X, Y = np.meshgrid(x,y)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_aspect('equal')
#levels = np.linspace(-0.1, 1.2, 40)
#cs = plt.contourf(X, Y, p, levels=levels)
cs = plt.contourf(X, Y, Z,50,cmap=plt.cm.get_cmap('jet'))#50 specifys how many levels of colors is there in the plot
#cs2 = plt.contour(cs, levels=cs.levels[::4], colors = 'k', origin='upper', hold='on')
plt.colorbar(cs,format="%.2f",orientation='horizontal')
legend = plt.legend(loc='upper center', shadow=True,fontsize='x-large')
plt.xlabel(r'x')
plt.ylabel(r'y')
if not('myplot' in os.listdir('./')):
    os.mkdir('myplot')
plt.savefig('./myplot/'+outputfile+'.png', bbox_inches='tight',dpi=900)
plt.close()





