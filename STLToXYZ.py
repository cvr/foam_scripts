##a script to read in an STL file and output an XYZ file in z(x,y) mode (a set of points on a rectangular grid ). 
import numpy as np
import pdb
import matplotlib.pyplot as plt
import os
import matplotlib as mpl


def inside_tri(pt,tri):
    #pt is (x,y) coordinate of to point being checked
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
        #all three z component have the same sign -> the pt is inside the triangle
        #if pt is on edge of the triangle, we still think it is 'inside' and return True
        return True
    else:
        return False
        

def get_z(pt, list_tri):
    #given (x,y) of a point, a list of triangle with coordinates of 3 vertices
    #return z coordinate of vertical projection of the point on that triangle
    #first we project all triangles in stl file onto x-y plane to get triangles on x-y plane. If a point P(x_p,y_p) is inside a certain triangle on x-y plane (determined by the algorithm above), then we use interpolate z(x_p,y_p) linearly from z value of three vertices of the triangle.
    for i,item in enumerate(list_tri): #item is a triangle object
        if inside_tri(pt,item):
            x1 = item[0,0]
            x2 = item[1,0]
            x3 = item[2,0]
            y1 = item[0,1]
            y2 = item[1,1]
            y3 = item[2,1]
            z1 = item[0,2]
            z2 = item[1,2]
            z3 = item[2,2]
            J = np.array([[1,x1,y1],[1,x2,y2],[1,x3,y3]])
            detj = np.linalg.det(J)
            #what if detj = 0, which means the triangle is vertical to x-y plane?
            #disgard this triangle and continue to look for next triangle for this point
            if abs(detj)<1e-10:
                continue
            x = pt[0]
            y = pt[1]
            z = (x2*y3-x3*y2+(y2-y3)*x+(x3-x2)*y)/detj*z1 + (x3*y1-x1*y3+(y3-y1)*x+(x1-x3)*y)/detj*z2 + (x1*y2-x2*y1+(y1-y2)*x+(x2-x1)*y)/detj*z3
            return z
    #if not found, give a warning
    print "Warning! "
    print "Cannot found a triangle where pt,", str(pt), " was inside."
    return float('nan')




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
outputfile = 'output.xyz'
logfile = stlfile+'_STLToXYZ.log'
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
#x = np.arange(32.5,45,0.1)
#y = np.arange(-10,8,0.1)
x = np.arange(31.5,36,0.02)
y = np.arange(-2,0,0.02)
print "mesh size: ", str(x.size),' by ',str(y.size)
Z = np.zeros((y.size,x.size))
for i,xx in enumerate(x):
    for j,yy in enumerate(y):
        pt = [xx,yy]
        log.write("processing point: "+ str(pt)+ '\n')
        z = get_z(pt,list_tri)
        Z[j,i] = z
        #write (x,y,z) to output
        pt = str(xx)+' '+str(yy)+' '+str(z) +'\n'
        output.write(pt)



#plot colormap
X, Y = np.meshgrid(x,y)
levels = np.linspace(0, 2, 30)
fig = plt.figure()
ax = plt.gca()
ax.set_aspect('equal')
# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
cmap = mpl.cm.cool
norm = mpl.colors.Normalize(vmin=0, vmax=2)
# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
#cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
#cb1.set_label('Some Units')
plt.contourf(X,Y,Z,levels)
if not('myplot' in os.listdir('./')):
    os.mkdir('myplot')
plt.savefig('./myplot/'+outputfile+'.png', bbox_inches='tight')
plt.close()





