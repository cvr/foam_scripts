#!/bin/bash
#clean all time files in multiple case directories returned by "ls ./"
for i in $(ls);
do
    echo ${i};
    cd ${i} && myfoam_remove_timefiles.sh && (rm -r timeFilesToBeRemoved &) && cd ../ ;
done
