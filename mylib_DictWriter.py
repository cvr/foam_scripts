#!/usr/bin/python
import sys

#--------------------------------------------------------------------#
#                        write_blockMeshDict                         #
#--------------------------------------------------------------------#
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
#x_pts=[-4.5,-0.75,0.75,12.75]
#y_pts=[-6.75,-0.75,0.75,6.75]
#z_pts=[0.,0.7,1.0]
##x_size=[[delta1_1,deltan_1],[delta1_2,deltan_2],...]
#x_size=[[0.2,0.05],[0.05,0.05],[0.05,0.5]]
#y_size=[[0.2,0.05],[0.05,0.05],[0.05,0.2]]
#z_size=[[0.05,0.05],[0.05,0.1]]
##write_blockMeshDict(x_pts,y_pts,z_pts,nx,ny,nz)    
#write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size)


#--------------------------------------------------------------------#
#                      write_snappyHexMeshDict                       #
#--------------------------------------------------------------------#
def write_snappyHexMeshDict(para,systemDir = './system'):
    #para is a python dictionary containing the parameters
    #In current version para should contain at least these keys:
    #stl_name,patch_name,eMesh_name
    import os
    dict_file = open(os.path.join(systemDir, 'snappyHexMeshDict'), 'w')
    log_file = open(os.path.join(systemDir, 'write_snappyHexMeshDict.log'), 'w')
    log_file.write('Input dictionary contains these parameters:\n')
    for (key,value) in para.items():
        line=str(key)+': '+str(value)+'\n'
        log_file.write(line)
    dict_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    dict_file.write('FoamFile\n')
    dict_file.write('{\n')
    dict_file.write('  version 2.0;\n')
    dict_file.write('  format  ascii;\n')
    dict_file.write('  class   dictionary;\n')
    dict_file.write('  object  snappyHexMeshDict;\n')
    dict_file.write('}\n')
    dict_file.write('castellatedMesh true;\n')
    dict_file.write('snap            true;\n')
    dict_file.write('addLayers       false;\n')
    dict_file.write('// Geometry. Definition of all surfaces. All surfaces are of class\n')
    dict_file.write('geometry\n')
    dict_file.write('{\n')
    if 'stl_name' in para:
        dict_file.write('    '+para['stl_name']+'\n')
    else:
        print 'must specify name of stl file in para'
        sys.exit()
    dict_file.write('    {\n')
    dict_file.write('        type triSurfaceMesh;\n')
    if 'patch_name' in para:
        dict_file.write('        name '+para['patch_name']+';\n')
    else:
        print 'must specify name of stl file in para'
        sys.exit()

    dict_file.write('    }\n')

    #can add refinementBox dictionary here

    dict_file.write('};\n')


    dict_file.write('\n')
    dict_file.write('\n')


    dict_file.write('// Settings for the castellatedMesh generation.\n')
    dict_file.write('castellatedMeshControls\n')
    dict_file.write('{\n')

    dict_file.write('    maxLocalCells 100000000;\n')
    dict_file.write('    maxGlobalCells 100000000;\n')
    dict_file.write('    minRefinementCells 1;\n')
    dict_file.write('    maxLoadUnbalance 0.30;\n')
    dict_file.write('    nCellsBetweenLevels 4;//For details, see:http://openfoamwiki.net/index.php/SnappyHexMesh#castellatedMeshControls\n')

    dict_file.write('    features\n')
    dict_file.write('    (\n')
    dict_file.write('        {\n')
    if 'eMesh_name' in para:
        dict_file.write('            file "'+para['eMesh_name']+'";\n')
    else:
        print 'must specify name of eMesh file in para'
        sys.exit()
    dict_file.write('            level 2;\n')
    dict_file.write('        }\n')
    dict_file.write('    );\n')

    dict_file.write('    // Surface based refinement\n')
    dict_file.write('    // Specifies two levels for every surface. The first is the minimum level,\n')
    dict_file.write('    // every cell intersecting a surface gets refined up to the minimum level.\n')
    dict_file.write('    refinementSurfaces\n')
    dict_file.write('    {\n')
    dict_file.write('        '+para['patch_name']+'\n')
    dict_file.write('        {\n')
    dict_file.write('            // Surface-wise min and max refinement level\n')
    dict_file.write('            level (1 2);\n')
    dict_file.write('        }\n')
    dict_file.write('    }\n')

    dict_file.write('    // Resolve sharp angles\n')
    dict_file.write('    resolveFeatureAngle 75;\n')
    dict_file.write('refinementRegions\n')
    dict_file.write('{\n')
    dict_file.write('}\n')
    dict_file.write('    locationInMesh (2 2 0.8);\n')
    dict_file.write('    allowFreeStandingZoneFaces true;\n')
    dict_file.write('}\n')


    dict_file.write('// Settings for the snapping.\n')
    dict_file.write('snapControls\n')

    dict_file.write('{\n')
    dict_file.write('    nSmoothPatch 3;\n')
    dict_file.write('    tolerance 4;\n')
    dict_file.write('    nSolveIter 30;\n')
    dict_file.write('    nRelaxIter 5;\n')
    dict_file.write('    nFeatureSnapIter 10;\n')
    dict_file.write('    implicitFeatureSnap false;\n')
    dict_file.write('    explicitFeatureSnap true;\n')
    dict_file.write('    multiRegionFeatureSnap false;\n')
    dict_file.write('}\n')
    dict_file.write('addLayersControls\n')
    dict_file.write('{\n')
    dict_file.write('    relativeSizes true;\n')
    dict_file.write('    layers\n')
    dict_file.write('    {\n')
    dict_file.write('	'+para['patch_name']+'\n')
    dict_file.write('        {\n')
    dict_file.write('            nSurfaceLayers 3;\n')
    dict_file.write('        }\n')
    dict_file.write('    }\n')
    dict_file.write('    expansionRatio 1.1;\n')
    dict_file.write('    finalLayerThickness 0.9;\n')
    dict_file.write('    minThickness 0.5;\n')
    dict_file.write('    nGrow 0;\n')
    dict_file.write('    featureAngle 60;\n')
    dict_file.write('    slipFeatureAngle 30;\n')
    dict_file.write('    nRelaxIter 3;\n')
    dict_file.write('    nSmoothSurfaceNormals 1;\n')
    dict_file.write('    nSmoothNormals 3;\n')
    dict_file.write('    nSmoothThickness 10;\n')
    dict_file.write('    maxFaceThicknessRatio 0.5;\n')
    dict_file.write('    maxThicknessToMedialRatio 0.3;\n')
    dict_file.write('    minMedianAxisAngle 90;\n')
    dict_file.write('    nBufferCellsNoExtrude 0;\n')
    dict_file.write('    nLayerIter 50;\n')
    dict_file.write('}\n')
    dict_file.write('meshQualityControls\n')
    dict_file.write('{\n')
    dict_file.write('    maxNonOrtho 65;\n')
    dict_file.write('    maxBoundarySkewness 20;\n')
    dict_file.write('    maxInternalSkewness 4;\n')
    dict_file.write('    maxConcave 80;\n')
    dict_file.write('    minFlatness 0.5;\n')
    dict_file.write('    minVol 1e-13;\n')
    dict_file.write('    minTetQuality 1e-30;\n')
    dict_file.write('    minArea -1;\n')
    dict_file.write('    minTwist 0.05;\n')
    dict_file.write('    minDeterminant 0.001;\n')
    dict_file.write('    minFaceWeight 0.05;\n')
    dict_file.write('    minVolRatio 0.01;\n')
    dict_file.write('    minTriangleTwist -1;\n')
    dict_file.write('    nSmoothScale 4;\n')
    dict_file.write('    errorReduction 0.75;\n')
    dict_file.write('    relaxed\n')
    dict_file.write('    {\n')
    dict_file.write('        maxNonOrtho 75;\n')
    dict_file.write('    }\n')
    dict_file.write('}\n')
    dict_file.write('debug 0;\n')
    dict_file.write('mergeTolerance 1e-6;\n')


#--------------------------------------------------------------------#
#                  write_surfaceFeatureExtractDict                   #
#--------------------------------------------------------------------#
def write_surfaceFeatureExtractDict(para,systemDir='./system'):
    #para is a python dictionary containing the parameters
    #para should at least contain these keys:
    #stl_name
    import os
    dict_file = open(os.path.join(systemDir, 'surfaceFeatureExtractDict'), 'w')
    log_file = open(os.path.join(systemDir, 'write_surfaceFeatureExtractDict.log'), 'w')
    log_file.write('Input dictionary contains these parameters:\n')
    for (key,value) in para.items():
        line=str(key)+': '+str(value)+'\n'
        log_file.write(line)
    dict_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    dict_file.write('FoamFile\n')
    dict_file.write('{\n')
    dict_file.write('  version 2.0;\n')
    dict_file.write('  format  ascii;\n')
    dict_file.write('  class   dictionary;\n')
    dict_file.write('  object  surfaceFeatureExtractDict;\n')
    dict_file.write('}\n')
    if 'stl_name' in para:
        dict_file.write(para['stl_name']+'\n')
    else:
        print 'must specify name of stl file in para'
        sys.exit()
    dict_file.write('{\n')
    dict_file.write('    extractionMethod    extractFromSurface;\n')
    dict_file.write('    extractFromSurfaceCoeffs\n')
    dict_file.write('    {\n')
    dict_file.write('        includedAngle   150;\n')
    dict_file.write('    }\n')
    dict_file.write('    subsetFeatures\n')
    dict_file.write('    {\n')
    dict_file.write('        nonManifoldEdges       no;\n')
    dict_file.write('        openEdges       yes;\n')
    dict_file.write('    }\n')
    dict_file.write('    writeObj                yes;\n')
    dict_file.write('}\n')


#--------------------------------------------------------------------#
#                         write_setFieldsDict                        #
#--------------------------------------------------------------------#
def write_setFieldsDict(para,systemDir='./system'):
    #para is a python dictionary containing the parameters
    #para should at least contain these keys:
    #water_depth
    import os
    dict_file = open(os.path.join(systemDir, 'setFieldsDict'), 'w')
    log_file = open(os.path.join(systemDir, 'write_setFieldsDict.log'), 'w')
    log_file.write('Input dictionary contains these parameters:\n')
    for (key,value) in para.items():
        line=str(key)+': '+str(value)+'\n'
        log_file.write(line)
    dict_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    dict_file.write('FoamFile\n')
    dict_file.write('{\n')
    dict_file.write('  version 2.0;\n')
    dict_file.write('  format  ascii;\n')
    dict_file.write('  class   dictionary;\n')
    dict_file.write('  object  setFieldsDict;\n')
    dict_file.write('}\n')

    dict_file.write('defaultFieldValues\n')
    dict_file.write('(\n')
    dict_file.write('    volScalarFieldValue alpha.water 0\n')
    dict_file.write(');\n')
    dict_file.write('regions\n')
    dict_file.write('(\n')
    dict_file.write('    boxToCell\n')
    dict_file.write('    {\n')
    if 'water_depth' in para:
        dict_file.write('        box (-999 -999 -999) (999 999 '+para['water_depth']+');\n')
    else:
        print 'must specify name of water_depth in para'
        sys.exit()
    dict_file.write('        fieldValues\n')
    dict_file.write('        (\n')
    dict_file.write('            volScalarFieldValue alpha.water 1\n')
    dict_file.write('        );\n')
    dict_file.write('    }\n')
    dict_file.write('    boxToFace\n')
    dict_file.write('    {\n')
    if 'water_depth' in para:
        dict_file.write('        box (-999 -999 -999) (999 999 '+para['water_depth']+');\n')
    else:
        print 'must specify name of water_depth in para'
        sys.exit()
    dict_file.write('        fieldValues\n')
    dict_file.write('        (\n')
    dict_file.write('            volScalarFieldValue alpha.water 1\n')
    dict_file.write('        );\n')
    dict_file.write('    }\n')
    dict_file.write(');\n')


#--------------------------------------------------------------------#
#                      write_myfoam_runCase.sh                       #
#--------------------------------------------------------------------#
def write_myfoam_runCase(para,dir='./'):
    #para is a python dictionary containing the parameters
    #para should at least contain these keys:
    #case_name,case_dir

    import os
    output_file = open(os.path.join(dir, 'myfoam_runCase.sh'), 'w')
    log_file = open(os.path.join(dir, 'write_myfoam_runCase.log'), 'w')
    log_file.write('Input dictionary contains these parameters:\n')
    for (key,value) in para.items():
        line=str(key)+': '+str(value)+'\n'
        log_file.write(line)


    output_file.write('#!/bin/bash\n')
    if 'case_name' in para:
        output_file.write('#PBS -N '+para['case_name']+'\n')
    else:
        print 'must specify case name in para'
        sys.exit()

    output_file.write('#PBS -l walltime=05:00:00,nodes=1:ppn=16\n')
    if 'case_dir' in para:
        output_file.write('#PBS -d '+para['case_dir']+'\n')
        output_file.write('#PBS -o '+para['case_dir']+'\n')
    else:
        print 'must specify case path in para'
        sys.exit()
    output_file.write('#PBS -j oe\n')
    output_file.write('#PBS -m abe\n')
    output_file.write('#PBS -W group_list=hyak-motley\n')
    output_file.write('##PBS -W group_list=hyak-lehman\n')
    output_file.write('module load icc_14.0-impi_4.1.1\n')
    output_file.write('source /gscratch/motley/shared/OpenFOAM231/OpenFOAM-2.3.1/etc/bashrc\n')
    output_file.write('finalTime=50\n')
    output_file.write('nprocessor=16\n')
    output_file.write('#If decomposed files exist, we should execute solver\n')
    output_file.write('if  [ ! -d processor0 ]  \n')
    output_file.write('then\n')
    output_file.write('    echo "decomposed files not found. Pre-process the case."\n')
    output_file.write('    [ -d 0 ] && { rm -r ./0; echo "removed old 0 file";} || { echo "0 file does not exist";}\n')
    output_file.write('    cp ./0.org ./0 -r\n')
    output_file.write('    blockMesh\n')
    output_file.write('    surfaceFeatureExtract\n')
    output_file.write('    snappyHexMesh\n')
    output_file.write('    mkdir mesh\n')
    output_file.write('    cp ./constant ./mesh -r\n')
    output_file.write('    mv ./0.001 ./mesh\n')
    output_file.write('    mv ./0.002 ./mesh\n')
    output_file.write('    rm ./constant/polyMesh -r\n')
    output_file.write('    cp ./mesh/0.002/polyMesh ./constant -r\n')
    output_file.write('    setFields\n')
    output_file.write('    decomposePar -force\n')
    output_file.write('fi\n')
    output_file.write('#if final time file does not exist in processor*, we should run solver\n')
    output_file.write('if [ ! -d processor0/$finalTime ]\n')
    output_file.write('then\n')
    output_file.write('    echo "Run interFoam."\n')
    output_file.write('    mpirun -np $nprocessor interFoam -parallel\n')
    output_file.write('fi\n')
    output_file.write('#if final time exist in processor* but does not exist in ./, run reconstructPar\n')
    output_file.write('if [ -d processor0/$finalTime ] && [ ! -d $finalTime ]\n')
    output_file.write('then\n')
    output_file.write('    echo "final time computed. Run reconstructPar."\n')
    output_file.write('    reconstructPar -newTimes\n')
    output_file.write('fi\n')
    output_file.write('#if final time exist in ./ but ./postProcessing/sets does not, run sample\n')
    output_file.write('#if the scripts is interupted during this part, sample may not be completed\n')
    output_file.write('if [ -d $finalTime ] && [ ! -d ./postProcessing/sets ]\n')
    output_file.write('then\n')
    output_file.write('    echo "final time reconstructed. Run sample."\n')
    output_file.write('    sample\n')
    output_file.write('fi\n')
    output_file.write('myfoam_getforcesHistory.py\n')
    output_file.write('myfoam_getAveragedForce.py\n')

#--------------------------------------------------------------------#
#                 write_boundaryData_scalar                          #
#--------------------------------------------------------------------#
#write a scalar-type data into boundaryData/inlet_patch_name/t
def write_boundaryData_scalar(scalar,t,name,para,dir='./constant'):
    #para is a python dictionary containing the parameters
    #scalar is a numpy array, containing value to be written
    #for each cell
    import os
    if not('boundaryData' in os.listdir(dir)):
        os.mkdir(dir+'/boundaryData')
    patch_dir = dir+'/boundaryData/'+para['inlet_patch_name']
    if not(para['inlet_patch_name'] in os.listdir(dir+'/boundaryData')):
        os.mkdir(patch_dir)
    if not( str(t) in os.listdir(patch_dir)):
        os.mkdir(patch_dir+'/'+str(t))
    dict_file = open(patch_dir+'/'+str(t)+'/'+name, 'w')
    log_file = open(patch_dir+'/write_boundaryData_on_'+para['inlet_patch_name']+'.log', 'a')
    log_file.write('Writing '+name+' at t='+str(t)+'\n')
    dict_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    dict_file.write('FoamFile\n')
    dict_file.write('{\n')
    dict_file.write('  version 2.0;\n')
    dict_file.write('  format  ascii;\n')
    dict_file.write('  class   scalarAverageField;\n')
    dict_file.write('  object  values;\n')
    dict_file.write('}\n')

    dict_file.write('// Average\n')
    dict_file.write('0.0\n')
    dict_file.write('// Data on points\n')
    dict_file.write(str(scalar.size)+'\n')
    dict_file.write('(\n')
    for i in range(scalar.size):
        dict_file.write(str(scalar[i])+'\n')
    dict_file.write(')\n')

#--------------------------------------------------------------------#
#                    write_boundaryData_vector                       #
#--------------------------------------------------------------------#
#write a vector-type data into boundaryData/inlet_patch_name/t
def write_boundaryData_vector(vector,t,name,para,dir='./constant',foam_class='vectorAverageField',foam_object='values'):
    #para is a python dictionary containing the parameters
    #vector is a numpy array, containing value of vectors to be written 
    #for each cell
    import os
    if not('boundaryData' in os.listdir(dir)):
        os.mkdir(dir+'/boundaryData')
    patch_dir = dir+'/boundaryData/'+para['inlet_patch_name']
    if not(para['inlet_patch_name'] in os.listdir(dir+'/boundaryData')):
        os.mkdir(patch_dir)
    if len(str(t)) > 0:#write into patch_dir/time/
        if not( str(t) in os.listdir(patch_dir)):
            os.mkdir(patch_dir+'/'+str(t))
        dict_file = open(patch_dir+'/'+str(t)+'/'+name, 'w')
        write_average=True
    else:#len(t)=0, write into patch_dir/
        write_average=False
        dict_file = open(patch_dir+'/'+name, 'w')

    log_file = open(patch_dir+'/write_boundaryData_on_'+para['inlet_patch_name']+'.log', 'a')
    log_file.write('Writing '+name+' at t='+str(t)+'\n')
    dict_file.write('/*--------------------------------*- C++ -*----------------------------------*/\n')
    dict_file.write('FoamFile\n')
    dict_file.write('{\n')
    dict_file.write('  version 2.0;\n')
    dict_file.write('  format  ascii;\n')
    dict_file.write('  class   '+foam_class+';\n')
    dict_file.write('  object  '+foam_object+';\n')
    dict_file.write('}\n')

    if write_average:
        dict_file.write('// Average\n')
        dict_file.write('(0 0 0)\n')
    dict_file.write('// Data on points\n')
    nrow=vector.shape[0]
    dict_file.write(str(nrow)+'\n')
    dict_file.write('(\n')
    for i in range(nrow):
        #todo change output format of the float numbers
        line = '( '+str(vector[i,:]).lstrip('[').rstrip(']') +' )'
        dict_file.write(line+'\n')
    dict_file.write(')\n')
