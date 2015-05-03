#!/bin/bash

#PBS -N run_testShell
#PBS -l walltime=3:00:00:00,nodes=1:ppn=16


##This must be specified before running the case!!!!!!!!!!!!!
#PBS -d /civil/shared/motley/xsqin/open_water_tank/no_object/testBC17


#PBS -o run.log
#PBS -j oe
#PBS -m abe
#PBS -W group_list=hyak-motley
##PBS -W group_list=hyak-lehman
module load icc_14.0-impi_4.1.1
source /gscratch/motley/shared/OpenFOAM231/OpenFOAM-2.3.1/etc/bashrc

finalTime=10
nprocessor=16

#If decomposed files exist, we should execute solver 
if  [ ! -d processor0 ]  
then
    echo "decomposed files not found. Pre-process the case."
    [ -d 0 ] && { rm -r ./0; echo "removed old 0 file";} || { echo "0 file does not exist";}
    cp ./0.org ./0 -r
    blockMesh
    surfaceFeatureExtract
    SnappyHexMesh
    setFields
    decomposePar -force
fi

#if final time file does not exist in processor*, we should run solver
if [ ! -d processor0/$finalTime ]
then
    echo "Run interFoam."
    mpirun -np $nprocessor interFoam -parallel
fi

#if final time exist in processor* but does not exist in ./, run reconstructPar
if [ -d processor0/$finalTime ] && [ ! -d $finalTime ]
then
    echo "final time computed. Run reconstructPar."
    reconstructPar -newTimes
fi

#if final time exist in ./ but ./postProcessing/sets does not, run sample
#if the scripts is interupted during this part, sample may not be completed
if [ -d $finalTime ] && [ ! -d ./postProcessing/sets ]
then
    echo "final time reconstructed. Run sample."
    sample
fi

