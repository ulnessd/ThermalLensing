import cv2
import numpy as np
import glob
import csv
import os

def process_video_to_heatmap(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return None

    # Get the number of frames and frame dimensions
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Check if row 315 is within the frame height
    if frame_height <= 310:
        print(f"Error: Row 310 is out of bounds for the video {video_path}.")
        return None

    # Initialize a matrix to hold the averaged data
    heatmap_data = np.zeros((frame_height, frame_count))

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            print(f"Can't receive frame {i} from video {video_path}. Exiting ...")
            break

        # Convert to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute the average along the columns
        avg_intensity = np.mean(frame_gray, axis=1)

        # Store the average data
        heatmap_data[:, i] = avg_intensity

    cap.release()

    rows_data = heatmap_data[356:368, :]  # Slices rows 305 to 315 (Python slicing excludes the upper bound)
    row_data_avg = np.mean(rows_data, axis=0)  # Compute the average across the selected rows for each column/frame
    return row_data_avg

# Ask the user for the directory
directory = input("Enter the directory path: ")

# Dictionary to hold all data
all_data = {}

# Process each video file
for video_file in glob.glob(os.path.join(directory, "*Red_average_subtract.avi")):
    file_name = os.path.splitext(os.path.basename(video_file))[0]
    data = process_video_to_heatmap(video_file)
    if data is not None:
        all_data[file_name] = data
        print(f"Processed {video_file}")

# Writing all data to a single CSV file
output_csv = os.path.join(directory, "KineticsConduction.csv")
with open(output_csv, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Frame Number'] + list(all_data.keys()))

    # Transpose data for CSV writing
    for i in range(len(data)):
        row = [i] + [all_data[key][i] if i < len(all_data[key]) else '' for key in all_data]
        writer.writerow(row)

print(f"All data saved to {output_csv}")
