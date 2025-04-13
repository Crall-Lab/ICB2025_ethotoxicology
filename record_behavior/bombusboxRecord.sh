#!/bin/bash

#source ~/Desktop/bombusbox-setup.sh #this command pulls all the environmental variables that we set in setup.sh into this script

DATE=$(date +"%Y-%m-%d") #This record the current date with format YYYY-MM-DD
DATETIME=$(date +"%Y-%m-%d_%H-%M-%S") #Records current date and time with format YYYY-MM-DD_HH-mm-SS
OUTPUT=/mnt/bombusbox/"$HOSTNAME"_"$DATE"/"$HOSTNAME"_"$DATETIME".mjpeg
#OUTPUT="$VIDEO_DIRECTORY"/"$HOSTNAME"_"$DATE"/"$HOSTNAME"_"$DATETIME"."$CODEC"

sudo mkdir -p /mnt/bombusbox/"$HOSTNAME"_"$DATE"

libcamera-vid --width 4056 --height 3040 --codec mjpeg --save-pts mjpeg -o "$OUTPUT" --nopreview -t 30000 --framerate 4 --shutter 2500 --tuning-file /usr/share/libcamera/ipa/raspberrypi/imx219_noir.json 
echo video recorded!