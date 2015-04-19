#!/usr/bin/python
from mylib_DictWriter import write_blockMeshDict
################################################################################
#input

#x_pts should be a list, specifying x coordinates of each vertices along x axis
#y_pts should be a list, specifying y coordinates of each vertices along y axis
#z_pts should be a list, specifying z coordinates of each vertices along z axis
x_pts=[-4.5,-0.75,0.75,12.75]
y_pts=[-6.75,-0.75,0.75,6.75]
z_pts=[0.,0.7,1.0]
#x_size[[deltax for 1st cell in 1st edge, deltax for last cell in 1st edge],
#       [deltax for 1st cell in 2nd edge, deltax for last cell in 2nd edge],
#       ...
#      ]
x_size=[[0.2,0.02],[0.02,0.02],[0.02,0.5]]
y_size=[[0.2,0.02],[0.02,0.02],[0.02,0.2]]
z_size=[[0.02,0.02],[0.02,0.06]]

#input end
################################################################################


#don't modify this
write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size)
