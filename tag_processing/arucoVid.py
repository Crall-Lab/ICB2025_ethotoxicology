'''
Author: Anupreksha Jain
Date: June 22, 2023
This script reads aruco tags in all videos in a folder and outputs a csv with date, time, tagIDs, and filename, as well as a txt file with erroneous videos.
'''

import os
import cv2
import cv2.aruco as aruco
import csv
import datetime

def read_aruco_tags_from_videos(video_folder, output_path, error_output_path):
    # Create a CSV file and write the header
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Time', 'Video', 'Tag IDs'])
    
    # Create a list to store erroneous videos
    erroneous_videos = []
    
    # Define the dictionary for ArUco tags (100 tag dictionary)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
    
    # Iterate over all files in the video folder and its subfolders
    for root, dirs, files in os.walk(video_folder):
        for filename in files:
            if filename.endswith('.mp4') or filename.endswith('.avi'):
                print(filename)
                # Load the video
                video_path = os.path.join(root, filename)
                video = cv2.VideoCapture(video_path)
                
                # Check if the video opened successfully
                if not video.isOpened():
                    print(f"Error opening video: {video_path}")
                    erroneous_videos.append(video_path)
                    continue
                
                # Retrieve the creation timestamp of the video file
                creation_timestamp = os.path.getctime(video_path)
                creation_datetime = datetime.datetime.fromtimestamp(creation_timestamp)
                creation_date = creation_datetime.date()
                creation_time = creation_datetime.time()
                
                # Create a list to store detected tag IDs in the current video
                tag_ids = []
                
                try:
                    # Read frames from the video
                    while True:
                        ret, frame = video.read()
                        if not ret:
                            break
                        
                        # Convert the frame to grayscale
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Detect ArUco tags in the frame
                        corners, ids, _ = aruco.detectMarkers(gray, aruco_dict)
                        
                        if ids is not None:
                            # Append detected tag IDs to the list
                            tag_ids.extend(ids.flatten().tolist())
                
                except cv2.error as e:
                    print(f"Error processing video: {video_path} - {str(e)}")
                    erroneous_videos.append(video_path)
                    continue
                
                with open(output_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([creation_date, creation_time, video_path, tag_ids])
                
                # Release the video capture object
                video.release()
    
    # Write the list of erroneous videos to a text file
    with open(error_output_path, mode='w') as file:
        file.write('\n'.join(erroneous_videos))

# Provide the path to your video folder
video_folder = "/Volumes/HH-2/videos/001f543e42c0/230609"

# Provide the output CSV file path
output_path = "/Users/anupreksha/Desktop/output/flowerVidTEST.csv"

# Provide the output file path for erroneous videos
error_output_path = "/Users/anupreksha/Desktop/output/flowerVidERROR.txt"

# Call the function to read ArUco tags from videos in the folder, write the output to a CSV file,
# and generate a list of erroneous videos
read_aruco_tags_from_videos(video_folder, output_path, error_output_path)
