import cv2
import numpy as np
import glob
import csv
import os

def integrate_video_frames(video_path, start_frame, end_frame):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Check if the frame range is valid
    if start_frame < 0 or end_frame >= frame_count or start_frame >= end_frame:
        print(f"Invalid frame range for integration in video {video_path}.")
        return None

    # Initialize a matrix to hold the averaged data
    heatmap_data = np.zeros((frame_height, frame_count))

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_intensity = np.mean(frame_gray, axis=1)
        heatmap_data[:, i] = avg_intensity

    cap.release()

    # Integrate the data over the specified frame range
    integrated_data = np.sum(heatmap_data[:, start_frame:end_frame], axis=1)
    return integrated_data

# Ask the user for the directory
directory = input("Enter the directory path: ")

# Dictionary to hold all integrated data
all_data = {}

# Process each video file
for video_file in glob.glob(os.path.join(directory, "*Red_average_subtract.avi")):
    file_name = os.path.splitext(os.path.basename(video_file))[0]
    integrated_data = integrate_video_frames(video_file, 475, 625)
    if integrated_data is not None:
        all_data[file_name] = integrated_data
        print(f"Processed {video_file}")

# Writing all integrated data to a single CSV file
output_csv = os.path.join(directory, "Integrated_Data.csv")
with open(output_csv, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Row Number'] + list(all_data.keys()))

    for i in range(len(integrated_data)):
        row = [i] + [all_data[key][i] if i < len(all_data[key]) else '' for key in all_data]
        writer.writerow(row)

print(f"All integrated data saved to {output_csv}")

