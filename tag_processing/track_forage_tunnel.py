import os
import cv2
import pandas as pd
from datetime import datetime
from natsort import natsorted
import sys  # For command-line argument handling

# Parameters
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
ARUCO_PARAMS = cv2.aruco.DetectorParameters()#cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMS)
FRAME_RATE = 30  # Adjust as needed

# Reference date: January 1, 2024
START_DATE = datetime(2023, 1, 1)

def extract_timestamp(filename):
    """Extracts datetime from filename like '04102024_090509_012625.jpg'."""
    if not os.path.basename(filename).startswith("._"):
        try:
            # Remove '.jpg' or any other file extension
            filename = os.path.splitext(filename)[0]
            date_str, time_str, ms_str = filename.split('_')
            date = datetime.strptime(date_str + time_str, '%d%m%Y%H%M%S')
            timestamp = date.replace(microsecond=int(ms_str))
            print(timestamp)
            return timestamp
        except Exception as e:
            print(f"Error parsing timestamp from filename '{filename}': {e}")
            return None
    else:
        print(f"Skipping hidden file: {filename}")
        return None

def find_all_images(parent_dir):
    """Recursively finds all .jpg files in the parent directory."""
    images = []
    for root, _, files in os.walk(parent_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                images.append(os.path.join(root, file))
    
    # Handle cases with 0 or 1 file
    if len(images) <= 1:
        return images
    
    # Filter and log problematic files
    valid_images = []
    for file in images:
        if extract_timestamp(os.path.basename(file)) is not None:
            valid_images.append(file)
        else:
            print(f"Skipping invalid or problematic file: {file}")
    
    # Sort valid images with error handling
    try:
        return natsorted(valid_images, key=lambda x: extract_timestamp(os.path.basename(x)))
    except Exception as e:
        print(f"Error during sorting: {e}")
        return valid_images  # Return unsorted valid images

def days_since_start(timestamp):
    """Calculates the days since January 1, 2023."""
    delta = timestamp - START_DATE
    return delta.days + delta.seconds / 86400  # Include fractional days

def detect_and_draw_aruco(image, filename, timestamp):
    """Detects ArUco markers, draws bounding boxes, and returns tag centroids."""
    
    # Ensure the input image is valid
    if image is None or image.size == 0:
        print("Error: Input image is empty or invalid.")
        return None, None, None

    try:
        # Convert to grayscale for ArUco detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect ArUco markers
        print(cv2.aruco.DetectorParameters())
        corners, ids, _ = DETECTOR.detectMarkers(gray)

        centroids = []
        if ids is not None:
            # Draw markers with red labels (color: (0, 0, 255)) and thicker lines
            for corner, tag_id in zip(corners, ids.flatten()):
                # Draw bounding box
                cv2.polylines(image, [corner.astype(int)], True, (0, 0, 255), 4)

                # Calculate centroid
                cx = int(corner[0][:, 0].mean())
                cy = int(corner[0][:, 1].mean())
                centroids.append((cx, cy))

                # Draw the tag ID label near the centroid, with larger text size
                cv2.putText(
                    image, str(tag_id), (cx, cy - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4, cv2.LINE_AA
                )

        cv2.putText(
            image, str(timestamp), (10, image.shape[0] - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
        )

        cv2.putText(
                image, str(filename), (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
            )

        return image, ids, centroids

    except cv2.error as e:
        print(f"OpenCV Error: {e}")
        return None, None, None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None, None, None

def main(parent_dir, visualize):
    """Processes images in the given directory with optional visualization."""
    images = find_all_images(parent_dir)
    if not images:
        print("No images found.")
        return

    # Extract folder name to use in output filenames
    folder_name = os.path.basename(os.path.normpath(parent_dir))
    output_video = os.path.join(parent_dir, f"{folder_name}_aruco_detection_video.mp4")
    output_csv = os.path.join(parent_dir, f"{folder_name}_aruco_detections.csv")

    # Prepare CSV output
    csv_data = []

    # Get the first image to determine frame size for video writer
    first_image = cv2.imread(images[0])
    height, width, _ = first_image.shape
    video_writer = cv2.VideoWriter(
        output_video, cv2.VideoWriter_fourcc(*'mp4v'), FRAME_RATE, (width, height)
    )

    for image_path in images:
        filename = os.path.basename(image_path)
        timestamp = extract_timestamp(filename)
        if timestamp is None:
            continue

        days_numeric = days_since_start(timestamp)

        image = cv2.imread(image_path)
        annotated_image, ids, centroids = detect_and_draw_aruco(image, filename, timestamp)

        # Display the annotated image if visualization is enabled
        if visualize:
            if annotated_image is not None and annotated_image.size > 0:
                cv2.imshow('ArUco Detection', annotated_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit early
                    break
            else:
                print("Error: Annotated image is empty or invalid, skipping visualization.")


        # Write frame to video
        video_writer.write(annotated_image)

        # Log detections to CSV
        if ids is not None:
            for tag_id, (cx, cy) in zip(ids.flatten(), centroids):
                csv_data.append([timestamp, days_numeric, filename, tag_id, cx, cy])

    # Release video writer and close any open windows
    video_writer.release()
    if visualize:
        cv2.destroyAllWindows()

    # Save CSV
    df = pd.DataFrame(csv_data, columns=['timestamp', 'days_since_start', 'filename', 'tag_id', 'x', 'y'])
    df.sort_values(by='timestamp', inplace=True)
    df.to_csv(output_csv, index=False)

    print(f"Processing complete. Video saved as '{output_video}' and CSV saved as '{output_csv}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aruco_tracking_with_option.py <folder_path> [--no-visualize]")
        sys.exit(1)

    parent_directory = sys.argv[1]
    visualize = '--no-visualize' not in sys.argv  # Enable visualization unless '--no-visualize' is specified

    main(parent_directory, visualize)
