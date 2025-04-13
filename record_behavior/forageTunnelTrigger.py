#modified by AJ, AEC, AT from motionCamTest by realActorMattSmith

import cv2 as cv
import numpy as np
import os
import time
from datetime import datetime
from matplotlib import pyplot as plt


startT1 = time.time()
bt1 = time.time()
vid1 = cv.VideoCapture(0)
vid1.set(cv.CAP_PROP_EXPOSURE,-4)
# Setting exposure to (50 * 100uS)
# May need to turn off any auto exposure / priority settings before function
#attr = getattr(cv, cv.CAP_PROP_EXPOSURE)
#vid1.set(attr, 50)
'''
def updateBackground(background1,newFrame):
    background1.append(newFrame)
    background1.pop(0)
    b1 = np.zeros((np.shape(background1[0])))
    for ele in range(0,10):
        b1+=background1[ele]
    b1 = b1/10
    background2 = b1
    return initialBackground,background2

'''
initialBackground = []
for ele in range(0,10):
    temp = vid1.read()
    initialBackground.append(temp[1])
b1 = np.zeros((np.shape(initialBackground[0])))
for ele in range(0,10):
    b1+=initialBackground[ele]
b1 = b1/10
background = b1

recD1 = True
print('beginning')
qwkBack = vid1.read()[1]
#imageBinB = np.zeros((np.shape(qwkBack)[0],np.shape(qwkBack)[1],3,100))
nameBinB = []
cntt = 0
while recD1 == True:
    if time.time()-startT1 > 0.25:
        getFrame = vid1.read()[1]
        #print(np.nansum(np.nanmean(getFrame,2)-np.nanmean(qwkBack,2)))
        if np.nansum(np.abs(np.nanmean(getFrame,2)-np.nanmean(qwkBack,2))) > 300000:
            #print('record')
            outF = datetime.now()
            outF = outF.strftime("%d%m%Y_%H%M%S_%f")
            outF2 = datetime.now()
            outF2 = outF2.strftime("%Y-%m-%d_%H")
            if not os.path.exists('/mnt/bombusbox/forage_tunnel/'+ str(outF2)):
                os.mkdir('/mnt/bombusbox/forage_tunnel/'+ str(outF2))
            cv.imwrite('/mnt/bombusbox/forage_tunnel/'+str(outF2)+'/'+str(outF)+'.jpg',getFrame)
            #imageBinB[:,:,:,cntt] = getFrame
            #nameBinB.append(outF)
            #cv.imwrite('/home/pi/foragerExit/'+str(outF)+'.jpg',getFrame)
            #initialBackground,background = updateBackground(initialBackground,getFrame)
            cntt+=1
        startT2 = time.time()
    qwkBack = vid1.read()[1]
   # if startT2-startT1 > 290:
       # recD1 = False

vid1.release()

'''
ll1 = []
for ele in range(0,100):
    if np.nansum(imageBinB[:,:,:,ele])>0:
        ll1.append(ele)
for ele in ll1:
    tempName = '/media/pi/Samsung USB1/foragingExit/'+str(nameBinB[ele])+'.jpg'
    cv.imwrite(tempName,imageBinB[:,:,:,ele])
'''

#def take_jpeg():
    
#    vid1 = cv.VideoCapture(0)
#    image = vid1.read()[1]
#    cv.imwrite('/mnt/bombusbox/forage_tunnel/testjpg.jpg',image)
