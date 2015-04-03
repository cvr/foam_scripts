#!/bin/bash
[ -d timeFilesToBeRemoved ] || { mkdir timeFilesToBeRemoved;}
ls | grep -P "^\d+\.*\d*$" | xargs -I{} mv {} timeFilesToBeRemoved/ #move all time files into a file named trash

