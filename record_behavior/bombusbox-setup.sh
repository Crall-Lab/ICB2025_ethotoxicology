#!/bin/bash

VIDEO_LENGTH=20000 #Length in milliseconds (20000 = 20 seconds)
VIDEO_FREQUENCY=2 #Record a video every X minutes
SHUTTERSPEED=2500 #Also in milliseconds - smaller value means less blurring but also less light!
FRAMES_PER_SECOND=4 #This is the fastest framerate we can get using the full resolution of the Raspberry Pi camera
VIDEO_DIRECTORY=/mnt/bombusbox

BOMBUS_NETWORK=OFF #Do you have multiple bombus-boxes connected via ethernet cables (ie a Local Access Network or LAN)? If yes and if you want the settings
					#on this computer to be sent to the others, rather than configuring each of them, turn this ON


UPTIME_SECONDS=300 #The recording script checks if the most recent video command created a video, and if it hasn't, it will reboot the computer
				   #after a specified amount of time of the computer being on, in seconds - ex. 300 seconds reboots the computer after five minutes
				   #If you don't want the computer to reboot at all, set UPTIME_SECONDS=OFF
VIDEO_CODEC=mjpeg 			#Tells the computer which type of codec you want to use - mjpeg can use the full camera resolution

INFRARED_IMAGING=ON #Removes pink hue to recordings imaged in IR light from cameras with the IR filter removed, returns greyscale image

TEMP_RECORDING=ON #Temp recording is currently set up for the DAQHATS XXXX recording device

#Region of interest (ROI) allows you to only collect data from a certain portion of the camera sensor.
#If you want to focus on only a certain portion of your frame, or cut out glare that is disrupting
#white balancing, you can try this out. Respective numbers between 0.0 and 1.0 correspond to (x,y,w,h), where x and y correspond 
#to the new top left corner coordinate of your image (x=how far right you move, y=how far down you move), and w,h correspond to 
#the new width and height of your image, as proportions of the original sensor size (4056x3040)
#If your new ratio of width and height differs from 4:3, you will need to adjust the width and height variables accordingly to avoid distortion. 
#For example, if my new ROI sets (x=0.1,y=0.0) so I'm just shifting my frame to the right a bit, and sets (w=0.5,h=1.0), 
#I will need to adjust my width value accordingly (4056x0.5), WIDTH=2028

ROI=0.0,0.0,1.0,1.0 		
WIDTH=4056					
HEIGHT=3040

if ["$VIDEO_DIRECTORY"==/mnt/bombusbox]; then #if they want to use the standard video directory folder, make it!
	
	mkdir -p /mnt/bombusbox

export VIDEO_LENGTH
export VIDEO_FREQUENCY
export SHUTTERSPEED
export FRAMES_PER_SECOND
export VIDEO_DIRECTORY
export UPTIME_SECONDS
export VIDEO_CODEC
export INFRARED_IMAGING
export TEMP_RECORDING
export ROI
export WIDTH
export HEIGHT

#then run the set_crontab.sh script
#if you have list of hostnames, can grab them from here, use them to transmit the crontab to the other boxes, send bombusbox-setup script to them too
#still need to add functionality to the record temp script - could adjust script to take args, then set the recording frequency with a variable, add it as arg to crontab

#for 
