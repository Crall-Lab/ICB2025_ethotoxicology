#import numpy as np
import cv2
#import skvideo.io
import os
#import zarr
import dask.array as da
import glob
import random
import datetime
from datetime import date
import setup
import socket
import argparse
import sys
import logging
import time
import gc
import subprocess
import shutil

def create_todays_folder(dirpath):
	
	todays_folder_path = dirpath
	print(todays_folder_path)
	
	if not os.path.exists(todays_folder_path):
		
		try:
			os.makedirs(todays_folder_path)
			return 0, todays_folder_path
		
		except Exception as e:
			print(e)
			print(e.args)
			print("Couldn't make today's folder for some reason... trying subprocess!")
			try:
				subprocess.call(['sudo', 'mkdir', '-p', todays_folder_path])
				return 0, todays_folder_path
			except:
				print(e)
				print(e.args)
				print("That didn't work either! Huh...")
				return 1, todays_folder_path
	
	else:
		return 0, todays_folder_path


#generate Nest Images folder
def make_nest_images_dir():
    if not os.path.isdir(f'{setup.data_folder_path}/Nest Images'):
        print("Need to make nest folder!")
        try:
            os.makedirs(f'{setup.data_folder_path}/Nest Images')
            return 0, f'{setup.data_folder_path}/Nest Images'
		
        except Exception as e:
            print(e)
            print(e.args)
            print("Couldn't make today's folder for some reason... trying subprocess!")
            try:
                nest_folder_path = f'{setup.data_folder_path}/Nest Images'
                subprocess.call(['sudo', 'mkdir', '-p', nest_folder_path])
                return 0, nest_folder_path
            except:
                print(e)
                print(e.args)
                print("That didn't work either! Huh...")
                return 1, nest_folder_path
    else:
        return 0, f'{setup.data_folder_path}/Nest Images'


def extract_frame_from_video(filepath, nestpath):

    vid = cv2.VideoCapture(filepath)
    print("extract1")
    frame_num = 0
    name, ext = os.path.splitext(filepath)

    while(vid.isOpened()):

        ret,frame = vid.read()
        if ret == True:
            if frame_num == 30:
                print("Frame = 30, should save png")
                try:
                    frame_to_write = frame.copy()
                    cv2.imwrite(name + '.png', frame_to_write)
                    return 0

                except:
                    return 1

            else:
                frame_num += 1

                continue

        else:
            break

    return 1
             

#alternative code for compiling pngs
def generate_nest_image(todays_folder_path, today, number_of_images, hostname, no_pictures_saved=True, codec='mjpeg', shuffle=True):
    
    ret, nestpath = make_nest_images_dir()
    files = []

    if no_pictures_saved == False:

        for file in glob.glob(f"{todays_folder_path}/*.png"):
            print(file)
            files.append(file)
        if shuffle==True:
            random.shuffle(files)

        total_frames = len(files)
        print('total frames: ' + str(total_frames))
        
        if total_frames > number_of_images:
            total_frames = number_of_images
            files = files[:total_frames]
            
        file_dimensions = []
        index = 0
        print("Trying to read image file!")
        imgdata = cv2.imread(files[0])
        gray_img = cv2.cvtColor(imgdata, cv2.COLOR_RGB2GRAY)
        
        try:
            h,w,d = gray_img.shape
            print("Image is 3d")
            x = da.zeros((total_frames,h,w,d)).astype('uint8')
            print(f"empty image array shape: {x.shape}")
        except:
            h,w = gray_img.shape
            x = da.zeros((total_frames,h,w)).astype('uint8')
            print(f"empty image array shape: {x.shape}")
        #for file in first_set:
        
        
        for file in files:
            #filename = os.path.basename(filename)
            #fname, ext = os.path.splitext(filename)
            print(file)
            imgdata = cv2.imread(file)
            gray_img = cv2.cvtColor(imgdata, cv2.COLOR_RGB2GRAY)
            gray_img = gray_img.astype('uint8')
            #videodata = skvideo.io.vread(file)
            #f,h,w,d = videodata.shape
            try:
                h,w,d = gray_img.shape
                dims = (h,w,d)
                print(h,w,d)
                file_dimensions.append(dims)
                print(f"file dimensions: {file_dimensions[0]}")
                if dims != file_dimensions[0]:
                    print('resizing')
                    imgdata = cv2.resize(gray_img, (file_dimensions[0][1], file_dimensions[0][0]))
                print(gray_img.shape)
                x[index] = gray_img
                print("Got here")
                index += 1
            except Exception as e:
                print(e)
                #print('had a dimension issue, image not 3d')
                h,w = gray_img.shape
                file_dimensions.append((h,w))
                if h != file_dimensions[0][0] and w != file_dimensions[0][1]:
                    gray_img = cv2.resize(gray_img, (file_dimensions[0][1], file_dimensions[0][0]))
                print(f'gray image shape: {gray_img.shape}. Empty frame shape: {x[index].shape}')
                try:
                    x[index] = gray_img
                except:
                    print("Skipping image, its dimensions arent the same as that of the first image in this randomized list")
                index += 1


    elif no_pictures_saved == True:
        
        if codec == 'mjpeg':
            print("here2")
            
            for file in glob.glob(f"{todays_folder_path}/*.mjpeg"):
                print(file)
                val = extract_frame_from_video(file, nestpath)
                print("here3")
                if val == 1:
                    print(f"OH NO! SOMETHING TERRIBLE HAPPENED  IN VIDEO {file}") #make this more informative

            for file in glob.glob(f"{todays_folder_path}/*.png"):
                print(file)
                print('here4')
                files.append(file)
            if shuffle==True:
                random.shuffle(files)

        total_frames = len(files)
        print('total frames: ' + str(total_frames))
        
        if total_frames == 0:
            print('skipping'+str(todays_folder_path))

        
        elif total_frames > 0:
    
            if total_frames > number_of_images:
                total_frames = number_of_images
                files = files[:total_frames]
                
            file_dimensions = []
            index = 0
            print("Trying to read image file!")
            imgdata = cv2.imread(files[0])
            gray_img = cv2.cvtColor(imgdata, cv2.COLOR_RGB2GRAY)
            
            try:
                h,w,d = gray_img.shape
                print("Image is 3d")
                x = da.zeros((total_frames,h,w,d)).astype('uint8')
                print(f"empty image array shape: {x.shape}")
            except:
                h,w = gray_img.shape
                x = da.zeros((total_frames,h,w)).astype('uint8')
                print(f"empty image array shape: {x.shape}")
            #for file in first_set:
            
            
            for file in files:
                #filename = os.path.basename(filename)
                #fname, ext = os.path.splitext(filename)
                print(file)
                imgdata = cv2.imread(file)
                gray_img = cv2.cvtColor(imgdata, cv2.COLOR_RGB2GRAY)
                gray_img = gray_img.astype('uint8')
                #videodata = skvideo.io.vread(file)
                #f,h,w,d = videodata.shape
                try:
                    h,w,d = gray_img.shape
                    dims = (h,w,d)
                    print(h,w,d)
                    file_dimensions.append(dims)
                    print(f"file dimensions: {file_dimensions[0]}")
                    if dims != file_dimensions[0]:
                        print('resizing')
                        imgdata = cv2.resize(gray_img, (file_dimensions[0][1], file_dimensions[0][0]))
                    print(gray_img.shape)
                    x[index] = gray_img
                    print("Got here")
                    index += 1
                except Exception as e:
                    print(e)
                    #print('had a dimension issue, image not 3d')
                    h,w = gray_img.shape
                    file_dimensions.append((h,w))
                    if h != file_dimensions[0][0] and w != file_dimensions[0][1]:
                        gray_img = cv2.resize(gray_img, (file_dimensions[0][1], file_dimensions[0][0]))
                    print(f'gray image shape: {gray_img.shape}. Empty frame shape: {x[index].shape}')
                    try:
                        x[index] = gray_img
                    except:
                        print("Skipping image, its dimensions arent the same as that of the first image in this randomized list")
                    index += 1
                
            print("Computing image")
            a = da.median(x, axis=0)
            a1 = a.compute()
            
            print("Writing image")
            #cv2.imwrite(f'{todays_folder_path}/{hostname}-{today}-nest_image.png', final_image)
            cv2.imwrite(f'{todays_folder_path}/nest_image.png', a1)
            print(f'{todays_folder_path}/nest_image.png')
            cv2.imwrite(f'{nestpath}/nest_image.png', a1)
            print(f'{nestpath}/nest_image.png')
            print("Image written!")
            
        return total_frames

def main(path):
    
    start = time.time()
    
    #parser = argparse.ArgumentParser(prog='Generate a composite nest image (from the images in todays folder) without bees in it! ')
    #parser.add_argument('-p', '--data_folder_path', type=str, default=setup.data_folder_path, help='a path to the folder you want to collect data in. Default path is: /mnt/bumblebox/data/')
    #parser.add_argument('-i', '--number_of_images', type=int, default=setup.number_of_images, help='the number of images you want to use to create your composite nest labelling image from todays images. The more you use, the longer this takes!')
    #parser.add_argument('-sh', '--shuffle', type=bool, default=True, help='if shuffle is True, all the images from todays folder will be randomized so that this script isnt choosing just the earliest images from today. If you want images from a shorter timespan, choose this and a lower number of frames (youll have to do the time calculations yourself, based on how frequently recordings and images are generated and how many frames youve chosen. Default is True.')
    #parser.add_argument('-np', '--no_pictures_saved', type=bool, default=False, help='if you do not have a .png image saved associated with each of your videos, set this to true so that the script extracts an image from each video')
    #parser.add_argument('-c', '--codec', type=str, default='mp4', help='if no_pictures_saved is set to True, we need to extract frames from videos to generate the image. We will need to know what kind of file the videos are in, either mp4 or mjpeg')
    #args = parser.parse_args()
    
    hostname = socket.gethostname()
    print('hostname')
    today = datetime.date.today()
    print('today')

    ret, todays_folder_path = create_todays_folder(path)
    if ret == 1:
        print("Couldn't create todays folder to store data in. Exiting program. Sad!")
        return 1
    
    #run_via_cron = None
    
    if sys.stdout.isatty():
        print("Running from terminal")
        
        #run_via_cron = False
        
        print(f"This is the generate_nest_images script! Im looking for images in:\n\n{todays_folder_path}\n\nThis is todays data folder.")   
        print("\n")
        
        print(f"Filename will look like this: (todays_folder_path)/nest_image.png. Example: bumblebox-03-trial2_hr10-hr18-nest_image.png")
        print(f"Filename: {todays_folder_path}/nest_image.png")

    else:
        
        print("Running nest image generation script via crontab")
        #run_via_cron = True
    
    total_frames = generate_nest_image(todays_folder_path, today, setup.number_of_images, hostname, no_pictures_saved=True, codec='mjpeg', shuffle=True)
    
    end = time.time()
    
    print(f"Creation of composite image took {round(end - start,2)} seconds for {total_frames} images.")

root_dir = '/media/bombus/Expansion/2024_outdoorBB_AJ'
output_dir = "/media/bombus/Expansion/2024_outdoorBB_AJ/cuke_2024_nest_images"

for round_name in os.listdir(root_dir):
    round_path = os.path.join(root_dir, round_name)
    if os.path.isdir(round_path):
        for location_name in os.listdir(round_path):
            location_path = os.path.join(round_path, location_name)
            if os.path.isdir(location_path):
                for date_name in os.listdir(location_path):
                    date_path = os.path.join(location_path, date_name)
                    if os.path.isdir(date_path):
                        if os.path.exists(os.path.join(date_path, 'nest_image.png')):
                            nest_image_path = os.path.join(date_path, 'nest_image.png')
                            descriptive_name = f"{round_name}_{location_name}_{date_name}_nest_image.png"
                            shutil.copy(nest_image_path, os.path.join(output_dir, descriptive_name))
                        else:
                            main(date_path)