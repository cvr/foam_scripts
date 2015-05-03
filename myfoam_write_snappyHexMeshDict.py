#!/usr/bin/python
from mylib_DictWriter import write_snappyHexMeshDict

para={}
para['stl_name']='yellow_block_0deg.stl'
para['patch_name']='house'
para['eMesh_name']='yellow_block_0deg.eMesh'


write_snappyHexMeshDict(para)
