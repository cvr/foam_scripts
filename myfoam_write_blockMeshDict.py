#!/usr/bin/python
from mylib_DictWriter import write_blockMeshDict
################################################################################
# user input starts here

#x_pts should be a python list, specifying x coordinates of each vertices along x axis 
#y_pts should be a python list, specifying y coordinates of each vertices along y axis
#z_pts should be a python list, specifying z coordinates of each vertices along z axis
#Below is an example with 3*3*2 blocks 
x_pts=[-4.5,-0.75,0.75,12.75]
y_pts=[-6.75,-0.75,0.75,6.75]
z_pts=[0.,0.7,1.0]
#x_size = [[deltax for 1st cell in 1st edge, deltax for last cell in 1st edge],
#         [deltax for 1st cell in 2nd edge, deltax for last cell in 2nd edge],
#          ...
#         ]
#similar for y_size and z_size
#We define a 3*3*2-block mesh before, thus here we need to specify mesh size on: 
#3 edges in x direction, 3 edges in y direction and 2 edges in z direction
x_size=[[0.2,0.02],[0.02,0.02],[0.02,0.5]]
y_size=[[0.2,0.02],[0.02,0.02],[0.02,0.2]]
z_size=[[0.02,0.02],[0.02,0.06]]

#user input ends here
################################################################################


#DO NOT modify code below
write_blockMeshDict(x_pts,y_pts,z_pts,x_size,y_size,z_size)
