#!/bin/bash
echo "
      K. Wardle 6/22/09, modified by H. Stadler Dec. 2013, minor fix Will Bateman Sep 2014.
      Modified by Xinsheng Qin July 2015.
      bash script to run reconstructPar in pseudo-parallel mode
      by breaking time directories into multiple ranges
     "
     
USAGE="
      USAGE: myfoam_parallelReconstructPar -n <Number of processors> -t <startTime,stopTime> -l <log_directory> -f <fields to be reconstructed> -o <OUTPUTFILE> 
        -f (fields) is optional, fields given in the form T,U,p; option is passed on to reconstructPar
  -t (times) is optional, times given in the form tstart,tstop
        -o (output) is optional (currently disable)

    Example:
    ./parReconstructPar.sh -n 4 -t 20,25 -f p_rgh,U,alpha.water
"


# At first check whether any flag is set at all, if not exit with error message
if [ $# == 0 ]; then
    echo "$USAGE"
    exit 1
fi

#Use getopts to pass the flags to variables
while getopts "f:n:o:t:l:" opt; do
  case $opt in
    f) if [ -n $OPTARG ]; then
  FIELDS=$(echo $OPTARG | sed 's/,/ /g')
  fi
      ;;
    n) if [ -n $OPTARG ]; then
  NJOBS=$OPTARG
  fi
      ;;
    o) if [ -n $OPTARG ]; then
  OUTPUTFILE=$OPTARG
       fi
      ;;
    t) if [ -n $OPTARG ]; then
  TLOW=$(echo $OPTARG | cut -d ',' -f1)
  THIGH=$(echo $OPTARG | cut -d ',' -f2)
  fi
      ;;
    l) if [ -n $OPTARG ]; then
          LOGDIR=$OPTARG
       fi
       ;;
    \?)
      echo "$USAGE" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# check whether the number of jobs has been passed over, if not exit with error message
if [[ -z $NJOBS ]]
then
    echo "
      the flag -n <NP> is required!
       "
    echo "$USAGE"
    exit 1
fi

APPNAME="reconstructPar"

echo "running $APPNAME in pseudo-parallel mode on $NJOBS processors"

#count the number of time directories
NSTEPS=$(($(ls -d processor0/[0-9]*/ | wc -l)-1))
NINITAL=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | wc -l) ##count time directories in case root dir, this will include 0
#NINITAL=$(ls -d [0-9]*/ | wc -l) ##count time directories in case root dir, this will include 0

P=p
#find min and max time
TMIN=$(ls processor0 -1v | sed '/constant/d' | sort -g | sed -n 2$P) # modified to omit constant  directory
TMAX=$(ls processor0 -1v | sed '/constant/d' | sort -gr | head -1) # modified to omit constant directory

################################################################################
####//Adjust min and max time according to specified -t options passed over//###
################################################################################
if [ -n "$TLOW" ]
  then
    TMIN=$(ls processor0 -1v | sed '/constant/d' | sort -g | sed -n 1$P) # now allow the first directory
    NLOW=2
    NHIGH=$NSTEPS
    # At first check whether the times are given are within the times in the directory
    if [ $(echo "$TLOW > $TMAX" | bc) == 1 ]; then
        echo "
      TSTART ($TLOW) > TMAX ($TMAX)
      Adjust times to be reconstructed!
      "
        echo "$USAGE"
        exit 1
    fi
    if [ $(echo "$THIGH < $TMIN" | bc) == 1 ]; then
        echo "
      TSTOP ($THIGH) < TMIN ($TMIN)
      Adjust times to be reconstructed!
      "
        echo "$USAGE"
        exit 1
    fi

  
    #set -x
    #trap read debug
    # Then set Min-Time
    #NSTART is index of beginning time directory processed by a certain processor 
    #make sure NSTART is assigned once even if the loop below is never executed for once
    NSTART=$(($NLOW-1))
    until [[ $(echo "$TMIN >= $TLOW" | bc) == 1 ]]; do
      TMIN=$(ls processor0 -1v | sed '/constant/d' | sed -n $NLOW$P)
      NSTART=$(($NLOW))
      let NLOW=NLOW+1
    done
    #set +x

    # And then set Max-Time
    until [ $(echo "$TMAX <= $THIGH" | bc) == 1 ]; do
      TMAX=$(ls processor0 -1v | sed '/constant/d' | sed -n $NHIGH$P)
      let NHIGH=NHIGH-1
    done

    #at this stage, 
    #NLOW is index of the time directory after TMIN,
    #NHIGH is index of the time directory before TMAX, 
    #NSTART is NLOW-1
    #e.g. time directories are 0,1,2,3,4,4.5,6, TMIN = 2, TMAX =4.5 
    #then NLOW = 4, NHIGH  = 5. NSTART = 3
    #NHIGH and NLOW are ONLY used to compute NSTEPS in this block
    # Finally adjust the number of directories to be reconstructed
    NSTEPS=$(($NHIGH-$NLOW+3))

  else #if -t option is not specified

      NSTART=2 #skip first time directory 

fi
#The block above output ONLY: NSTART and NSTEPS

echo "reconstructing $NSTEPS time directories"

NCHUNK=$(($NSTEPS/$NJOBS))
NREST=$(($NSTEPS%$NJOBS))
TSTART=$TMIN

if [ -z $LOGDIR ]
then
    LOGDIR="log.parReconstructPar"
fi
if [[ -d $LOGDIR ]]
then 
    echo "removing old log dir"
    rm $LOGDIR -r
fi
echo "making log dir"
mkdir $LOGDIR

################################################################################
#############################//Start assigning jobs//###########################
################################################################################
PIDS=""
for i in $(seq $NJOBS)
do
  if [ $NREST -ge 1 ]
    then
      NSTOP=$(($NSTART+$NCHUNK))
      let NREST=$NREST-1
    else
      NSTOP=$(($NSTART+$NCHUNK-1))
  fi
  TSTOP=$(ls processor0 -1v | sed '/constant/d' | sed -n $NSTOP$P)


  #TODO don't really need this?
  if [ $i == $NJOBS ] 
  then
  TSTOP=$TMAX
  fi

  
  if [ $NSTOP -ge $NSTART ]
    then  
    echo "Starting Job $i - reconstructing time = $TSTART through $TSTOP"
    if [ -n "$FIELDS" ]
      then
        $($APPNAME -fields "($FIELDS)" -time $TSTART:$TSTOP > $LOGDIR/output-$TSTART-$TSTOP &)
        sleep 2
        echo "Job started with PID $(pgrep -n -x $APPNAME)"
        PIDS="$PIDS $(pgrep -n -x $APPNAME)" # get the PID of the latest (-n) job exactly matching (-x) $APPNAME
      else
        $($APPNAME -time $TSTART:$TSTOP > $LOGDIR/output-$TSTART-$TSTOP &)
        sleep 2
        echo "Job started with PID $(pgrep -n -x $APPNAME)"
  PIDS="$PIDS $(pgrep -n -x $APPNAME)"
    fi
   fi

  let NSTART=$NSTOP+1
  TSTART=$(ls processor0 -1v | sed '/constant/d' | sed -n $NSTART$P)
done
echo "PIDS for all the processes are: $PIDS"
echo "Running...This may take a long time."

#sleep until jobs finish
#if number of running jobs > 0, hold loop until job finishes
NMORE_OLD=$(echo 0)
until [ $(ps -p $PIDS | wc -l) -eq 1 ]; # check for PIDS instead of $APPNAME because other instances might also be running 
  do 
    sleep 10
    NNOW=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | wc -l) ##count time directories in case root dir, this will include 0
    #NNOW=$(ls -d [0-9]*/ | wc -l) ##count time directories in case root dir, this will include 0
    NMORE=$(echo $NSTEPS-$NNOW+$NINITAL | bc) ##calculate number left to reconstruct and subtract 0 dir
    if [ $NMORE != $NMORE_OLD ]
      then
      echo "$NMORE directories remaining..."
    fi
    NMORE_OLD=$NMORE
  done

##combine and cleanup
#if [ -n "$OUTPUTFILE" ] 
#  then
##check if output file already exists
#  if [ -e "$OUTPUTFILE" ] 
#  then
#    echo "output file $OUTPUTFILE exists, moving to $OUTPUTFILE.bak"
#    mv $OUTPUTFILE $OUTPUTFILE.bak
#  fi
#
#  echo "cleaning up temp files"
#  for i in $(ls $LOGDIR)
#  do
#    cat $LOGDIR/$i >> $OUTPUTFILE
#  done
#fi
#
#rm -rf $LOGDIR

echo "finished"

