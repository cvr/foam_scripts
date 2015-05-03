#!/usr/bin/python

from mylib_DictWriter import write_myfoam_runCase

para={}
para['case_name']='d01'
para['case_dir'] = './'

#never change path to './', it will overwrite myfoam_runCase in current folder
path='./test'
write_myfoam_runCase(para,path)
