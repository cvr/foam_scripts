#!/bin/bash
[ -d timeFilesToBeRemoved ] || { mkdir timeFilesToBeRemoved;}
#ls | grep -P "^\d+\.*\d*$" | xargs -I{} mv {} timeFilesToBeRemoved/ #move all time files into a file named timeFilesToBeRemoved
ls | grep -P "^\d+\.*\d*$" | sort -g | sed 's/^0$//'| xargs -I{} mv {} timeFilesToBeRemoved/ #move all time files into a file named timeFilesToBeRemoved, excluding 0 file
touch $(echo "timeFilesWereRemovedOn_"$(date +%Y-%m-%d:%H:%M:%S))

