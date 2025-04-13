# nestPi
## Overview
nestPi is an imaging set-up designed to automatically monitor both in-nest behaviour and entrance/exits of one colony. This repository contains code for this system.

Once set up, it will automate video recording of the nest at specific intervals and images of a foraging tunnel when motion within the tunnel is detected. Resulting data is deposited onto specific folders on a USB drive.

<br><br>
## Requirements
### Raspberry Pi
Tested on Raspberry Pi 4 Model B, running Raspbian GNU/Linux 11 (bullseye), python 3.9.2
- libcamera (pre-installed with bullseye)
- python modules: pip, opencv-python, numpy, matplotlib

If libcamera is not installed, follow [these instructions](https://www.raspberrypi.com/documentation/computers/camera_software.html#building-libcamera-and-libcamera-apps) to install it. 

Python modules can be downloaded as follows:
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
pip install numpy matplotlib
sudo apt-get install python3-opencv
```

<br><br>
## Set-up
### Manual set-up
1. Download requirements following intructions above.
2. Download the code in this repository onto the Desktop. The scripts should be located in the Desktop, not in a sub-directory within ~/Desktop.
3. The USB drive used for data storage must be mounted at /dev/sba. For Raspberry Pi 4 Model B, insert USB drive onto top blue port. For other models of pis, check that the USB drive is inserted in the correct position using the following command:
   ```
   sudo fdisk -l
   ```
   A device corresponding to your USB drive should be found at /dev/sda1.
4. Connect cameras
5. Run this command: 
    ```
    crontab -e
    ```
    Then, append the contents of ```crontab.txt``` to the end of the file.
6. Following [this guide](https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/overview), set up a real time clock. This step can be omited if Raspberry Pi will have internet connection.

### Disk Image
1. Flash ```nestPi.img``` to an SD card. This can be done using [Etcher](https://etcher.balena.io/#download-etcher), or any similar software.
2. Insert SD card into Raspberry Pi
3. An internet connection is required for this step. Run 
    ```
    sudo hwclock -w
    sudo hwclock -r
    ```
    The output should be the time of your current location.
    Run
    ```
    sudo nano /boot/config.txt
    ```
    Comment out the last line. Then, save your changes and restart the Raspberry Pi.

<br><br>
## Running nestPi
Restart the Raspberry Pi. The code should start running automatically.

Check ```~/Desktop/log.txt``` for a log of the progress of the code, as well as any errors.

Check ```/mnt/bombusbox``` and ```/mnt/foragingtunnel``` for video and image output.

<br><br>
## Maintainers
Anupreksha Jain -- [anupreksha.jain@wisc.edu](mailto:anupreksha.jain@wisc.edu)

Acacia Tang --  [ttang53@wisc.edu](mailto:ttang53@wisc.edu)