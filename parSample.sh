#!/bin/bash
echo "
      By Xinsheng Qin - July 2015
      Adapted from K. Wardle 6/22/09
      bash script to run #sample# in pseudo-parallel mode
      by breaking time directories into multiple ranges
     "
     
USAGE="
      USAGE: $0 -n <Number of processors> -t <startTime,stopTime>
      -t (times) is optional, times given in the form tstart,tstop
      Example:
      ./parSample.sh -n 4 -t 20,25 

      Notice:
      1.If -t option is not specified, first time directory is ommited since it's probably 0 directory. 
"

################################################################################
######################//Parse input options//###################################
################################################################################
# At first check whether any flag is set at all, if not exit with error message
if [ $# == 0 ]; then
    echo "$USAGE"
    exit 1
fi

#Use getopts to pass the flags to variables
while getopts "n:t:" opt; do
  case $opt in
    n) if [ -n $OPTARG ]; then
          NJOBS=$OPTARG
       fi
       ;;
    t) if [ -n $OPTARG ]; then
          TLOW=$(echo $OPTARG | cut -d ',' -f1)
          THIGH=$(echo $OPTARG | cut -d ',' -f2)
          echo "From input:"
          echo "Lower time = $TLOW"
          echo "Higher time  = $THIGH"
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


APPNAME="sample"
echo "running $APPNAME in pseudo-parallel mode on $NJOBS processors"

#count the number of time directories
NSTEPS=$(($(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | wc -l)-1)) ##1.list directories in current folder and 
#delete all those containing characters. 2.Then count (how many time directories there are) - 1 

P=p
#find min and max time
TMIN=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n 2$P ) #get minimum time in current folder (exclude 1st one)
TMAX=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -gr | sed -n 1$P ) #get maximum time in current folder

################################################################################
####//Adjust min and max time according to specified -t options passed over//###
################################################################################
if [ -n "$TLOW" ]
#set -x
#trap read debug
  then
    TMIN=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n 1$P ) 
    NLOW=2
    NHIGH=$NSTEPS
    # At first check whether the times are given are within the times in the directory
    if [ $(echo "$TLOW > $TMAX" | bc) == 1 ]; then
        echo "
      TSTART ($TLOW) > TMAX ($TMAX)
      Adjust times to be sampled!
      "
        echo "$USAGE"
        exit 1
    fi
    if [ $(echo "$THIGH < $TMIN" | bc) == 1 ]; then
        echo "
      TSTOP ($THIGH) < TMIN ($TMIN)
      Adjust times to be sampled!
      "
        echo "$USAGE"
        exit 1
    fi

  
    # Then set Min-Time
    #NSTART is index of beginning time directory processed by a certain processor 
    #make sure NSTART is assigned once even if the loop below is never executed for once
    NSTART=$(($NLOW-1))
    until [[ $(echo "$TMIN >= $TLOW" | bc) == 1 ]]; do
      TMIN=$(ls -1v | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n $NLOW$P) #Actually -1v is not needed since there is sort
      NSTART=$(($NLOW))
      let NLOW=NLOW+1
    done

    # And then set Max-Time
    until [[ $(echo "$TMAX <= $THIGH" | bc) == 1 ]]; do
      TMAX=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n $NHIGH$P)
      let NHIGH=NHIGH-1
    done

    #at this stage, 
    #NLOW is index of the time directory after TMIN,
    #NHIGH is index of the time directory before TMAX, 
    #NSTART is NLOW-1
    #e.g. time directories are 0,1,2,3,4,4.5,6, TMIN = 2, TMAX =4.5 
    #then NLOW = 4, NHIGH  = 5. NSTART = 3
    #NHIGH and NLOW are ONLY used to compute NSTEPS in this block
    # Finally adjust the number of directories to be sampled
    NSTEPS=$(($NHIGH-$NLOW+3))

  else #if -t option is not specified

      NSTART=2 #skip first time directory 

fi
#The block above output ONLY: NSTART and NSTEPS

echo "sampling $NSTEPS time directories"
NCHUNK=$(($NSTEPS/$NJOBS))
NREST=$(($NSTEPS%$NJOBS))
TSTART=$TMIN

LOGDIR="log.parSample"
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
#trap read debug
PIDS=""
for i in $(seq $NJOBS)
do
  if [ $NREST -ge 1 ] #ge is greater than or equal to
    then
      #NSTOP is index of ending time directory processed by this processor
      NSTOP=$(($NSTART+$NCHUNK))
      let NREST=$NREST-1
    else
      NSTOP=$(($NSTART+$NCHUNK-1))
  fi
  TSTOP=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n $NSTOP$P)



  #TODO don't really need this?
  if [ $i == $NJOBS ] 
  then
  TSTOP=$TMAX
  fi

  
  if [ $NSTOP -ge $NSTART ]
  then  
    echo "Starting Job $i - sampling time = $TSTART through $TSTOP"
    $($APPNAME -time $TSTART:$TSTOP > $LOGDIR/output-$TSTART-$TSTOP &)
    sleep 2 #wait for PID appearing in ps
  echo "Job started with PID $(pgrep -n -x $APPNAME)"
  #-n: will select only the newest (most recently started) of the matching processes.
  #-x: only match processes whose name (or command line if -f is specified) exactly match the pattern.
  PIDS="$PIDS $(pgrep -n -x $APPNAME)"
  #PIDS contains PID for all running $APPNAME
  fi

  let NSTART=$NSTOP+1
  TSTART=$(ls | sed '/^[0-9]*[\.]*[0-9]*$/!d' | sort -g | sed -n $NSTART$P)
done
echo "PIDS for all the process are: $PIDS"
if [[ ! -d postProcessing/sets ]]
then 
    mkdir postProcessing/sets -p
fi

#set -x
#trap read debug
#sleep until jobs finish
#if number of running jobs > 0, hold loop until job finishes
NMORE_OLD=$(echo 0)
until [ $(ps -p $PIDS | wc -l) -eq 1 ]; # check for PIDS instead of $APPNAME because other instances might also be running 
  do 
    sleep 10
    NNOW=$(ls postProcessing/sets | wc -l) ##count time directories in postProcessing/sets
    NMORE=$(echo $NSTEPS-$NNOW | bc) ##calculate number left to be sampled 
    if [ $NMORE != $NMORE_OLD ]
      then
      echo "number of time directories finished: $NNOW"
      echo "$NMORE directories remaining..."
    fi
    NMORE_OLD=$NMORE
  done


echo "finished"

