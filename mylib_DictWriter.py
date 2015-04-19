#!/usr/bin/python
import sys

#def write_blockMeshDict(x_pts,y_pts,z_pts,nx,ny,nz,polyMeshDir = './constant/polyMesh'):
def write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size,polyMeshDir = './constant/polyMesh'):
#x_pts is a list specifying x coordinates of vertices along x axis
#y_pts is a list specifying y coordinates of vertices along y axis
#z_pts is a list specifying z coordinates of vertices along z axis
#nx is a list specifying number of cells along each edge along x axis. Length of nx = Length of x_pts - 1.
#ny is a list specifying number of cells along each edge along y axis. Length of ny = Length of y_pts - 1.
#nz is a list specifying number of cells along each edge along z axis. Length of nz = Length of z_pts - 1.
    import os.path

    n_xpts=len(x_pts) #number of vertices along x axis
    n_ypts=len(y_pts)
    n_zpts=len(z_pts)
    
    mesh_file = open(os.path.join(polyMeshDir, 'blockMeshDict'), 'w')
    log_file = open(os.path.join(polyMeshDir, 'write_blockMeshDict.log'), 'w')
    mesh_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    mesh_file.write('FoamFile\n')
    mesh_file.write('{\n')
    mesh_file.write('  version 2.0;\n')
    mesh_file.write('  format  ascii;\n')
    mesh_file.write('  class   dictionary;\n')
    mesh_file.write('  object  blockMeshDict;\n')
    mesh_file.write('}\n')
    mesh_file.write('convertToMeters 1.0;\n')


    for i in range(n_xpts): 
        log_file.write('//x%d  %g \n'%(i,x_pts[i]))
    for j in range(n_ypts): 
        log_file.write('//y%d  %g \n'%(j,y_pts[j]))
    for k in range(n_zpts): 
        log_file.write('//z%d  %g \n'%(k,z_pts[k]))
        log_file.write('\n')



#write vertices
    mesh_file.write('vertices\n')
    mesh_file.write('(\n')
    n=0
    for i in range(n_xpts):
        for j in range(n_ypts):
            for k in range(n_zpts):
                mesh_file.write(' (%g %g %g) // %d\n'%(x_pts[i],y_pts[j],z_pts[k],n))
                #mesh_file.write(' (%g %g %g) // %d  (check %d )\n'%(x_pts[i],y_pts[j],z_pts[k],n,n_ypts*n_zpts*(i)+n_zpts*(j)+k))
                n = n+1
    mesh_file.write(' );\n')
#write blocks
    mesh_file.write('blocks\n')
    mesh_file.write('(\n')

    def id(i,j,k):
        #given indices in x,y,z direction, return No. of that vertice 
        #note given indices should start from 0 instead of 1
        return n_ypts*n_zpts*i+n_zpts*j+k

    nx=[] #number of cells along each edge in x direction
    ny=[]
    nz=[]
    lx=[] #length of each edge in x direction
    ly=[]
    lz=[]
    rx=[] #clustering ratio along each edge in x direction
    ry=[]
    rz=[]
    from myfoam_mesh_calculator import get_n, get_r_given_delta1
    #compute nx,ny,nz
    for i in range(n_xpts-1):
        length = x_pts[i+1]-x_pts[i]
        lx.append(length)
        nx.append(get_n(x_size[i][0],x_size[i][1],length))
        rx.append(get_r_given_delta1(x_size[i][0],length,nx[i]))
    for j in range(n_ypts-1):
        length = y_pts[j+1]-y_pts[j]
        ly.append(length)
        ny.append(get_n(y_size[j][0],y_size[j][1],length))
        ry.append(get_r_given_delta1(y_size[j][0],length,ny[j]))
    for k in range(n_zpts-1):
        length = z_pts[k+1]-z_pts[k]
        lz.append(length)
        nz.append(get_n(z_size[k][0],z_size[k][1],length))
        rz.append(get_r_given_delta1(z_size[k][0],length,nz[k]))

    def writelog(): #write data into log file
        log_file.write('length of each edge in x direction:\n')
        log_file.writelines("%s\n" % item  for item in lx)
        log_file.writelines("\n")
        log_file.write('length of each edge in y direction:\n')
        log_file.writelines("%s\n" % item  for item in ly)
        log_file.writelines("\n")
        log_file.write('length of each edge in z direction:\n')
        log_file.writelines("%s\n" % item  for item in lz)
        log_file.writelines("\n")
        log_file.write('number of cells along each edge in x direction:\n')
        log_file.writelines("%s\n" % item  for item in nx)
        log_file.writelines("\n")
        log_file.write('number of cells along each edge in y direction:\n')
        log_file.writelines("%s\n" % item  for item in ny)
        log_file.writelines("\n")
        log_file.write('number of cells along each edge in z direction:\n')
        log_file.writelines("%s\n" % item  for item in nz)
        log_file.writelines("\n")
        log_file.write('clustering ratio along each edge in x direction:\n')
        log_file.writelines("%s\n" % item  for item in rx)
        log_file.writelines("\n")
        log_file.write('clustering ratio along each edge in y direction:\n')
        log_file.writelines("%s\n" % item  for item in ry)
        log_file.writelines("\n")
        log_file.write('clustering ratio along each edge in z direction:\n')
        log_file.writelines("%s\n" % item  for item in rz)
        log_file.writelines("\n")

    writelog()

    for i in range(n_xpts-1):
        for j in range(n_ypts-1):
            for k in range(n_zpts-1):
                mesh_file.write(' hex ( %2d %2d %2d %2d %2d %2d %2d %2d )     (%4d %4d %4d)    simpleGrading (%10.6g %10.6g %10.6g)\n'%(id(i,j,k),id(i+1,j,k),id(i+1,j+1,k),id(i,j+1,k),id(i,j,k+1),id(i+1,j,k+1),id(i+1,j+1,k+1),id(i,j+1,k+1), nx[i],ny[j],nz[k], rx[i],ry[j],rz[k]))
    mesh_file.write(' );\n')

#write edges
    mesh_file.write('edges\n')
    mesh_file.write('(\n')
    mesh_file.write(');\n')

#write boundaries
    mesh_file.write('boundary\n')
    mesh_file.write('(\n')
    #leftWall
    mesh_file.write(' inlet\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type patch;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')

    for j in range(n_ypts-1):
        for k in range(n_zpts-1):
            i=0
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i,j,k+1),id(i,j+1,k+1),id(i,j+1,k)))

    mesh_file.write('      );\n')
    mesh_file.write(' }\n')

    #rightWall
    mesh_file.write(' outlet\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type patch;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')
    for j in range(n_ypts-1):
        for k in range(n_zpts-1):
            i=n_xpts-1
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i,j+1,k),id(i,j+1,k+1),id(i,j,k+1)))
    mesh_file.write('      );\n')
    mesh_file.write(' }\n')

    #bottom
    mesh_file.write(' bottom\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type wall;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')
    for i in range(n_xpts-1):
        for j in range(n_ypts-1):
            k = 0
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i,j+1,k),id(i+1,j+1,k),id(i+1,j,k)))
    mesh_file.write('      );\n')
    mesh_file.write(' }\n')
    
    #top
    mesh_file.write(' atmosphere\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type patch;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')
    for i in range(n_xpts-1):
        for j in range(n_ypts-1):
            k = n_zpts-1 
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i+1,j,k),id(i+1,j+1,k),id(i,j+1,k)))
    mesh_file.write('      );\n')
    mesh_file.write(' }\n')

    #frontSide
    mesh_file.write(' frontSide\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type symmetryPlane;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')
    for i in range(n_xpts-1):
        for k in range(n_zpts-1):
            j = 0 
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i+1,j,k),id(i+1,j,k+1),id(i,j,k+1)))
    mesh_file.write('      );\n')
    mesh_file.write(' }\n')

    #backSide
    mesh_file.write(' backSide\n')
    mesh_file.write(' {\n')
    mesh_file.write('   type symmetryPlane;\n')
    mesh_file.write('   faces\n')
    mesh_file.write('     (\n')
    for i in range(n_xpts-1):
        for k in range(n_zpts-1):
            j = n_ypts-1 
            mesh_file.write('      (%3d %3d %3d %3d)\n'%(id(i,j,k),id(i,j,k+1),id(i+1,j,k+1),id(i+1,j,k)))
    mesh_file.write('      );\n')
    mesh_file.write(' }\n')
    mesh_file.write(');\n')

#write mergePatchPairs
    mesh_file.write('mergePatchPairs\n')
    mesh_file.write('(\n')
    mesh_file.write(');\n')
    mesh_file.close()


#test - simple one block
#x_pts=[-3.2,9.6]
#y_pts=[-3.2,3.2]
#z_pts=[0,0.6]
#x_size=[[1,0.2]]
#y_size=[[0.2,0.2]]
#z_size=[[0.02,0.05]]
#write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size)



#test - multi-block
x_pts=[-4.5,-0.75,0.75,12.75]
y_pts=[-6.75,-0.75,0.75,6.75]
z_pts=[0.,0.7,1.0]
#x_size=[[delta1_1,deltan_1],[delta1_2,deltan_2],...]
x_size=[[0.2,0.05],[0.05,0.05],[0.05,0.5]]
y_size=[[0.2,0.05],[0.05,0.05],[0.05,0.2]]
z_size=[[0.05,0.05],[0.05,0.1]]
#write_blockMeshDict(x_pts,y_pts,z_pts,nx,ny,nz)    
write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size)
