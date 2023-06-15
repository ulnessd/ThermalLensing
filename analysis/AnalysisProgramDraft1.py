import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from numpy import savetxt

sample='Benzene'

# Directory paths
video_directory = sample  # Replace with your video directory
timestamps_directory = sample  # Replace with your timestamps directory

# Get the list of all video files
video_files = [f for f in os.listdir(video_directory) if f.endswith('.avi')]

# Process each video file
for video_file in video_files:

    # Parse the file name
    base_name, run = os.path.splitext(video_file)[0].split('Red')
    run = int(run)

    # Create the output directories if they don't exist
    output_directory = os.path.join(video_directory, base_name, f'{base_name}{run}')
    os.makedirs(output_directory, exist_ok=True)

    # Load the video
    cap = cv2.VideoCapture(os.path.join(video_directory, video_file))

    # Get frame rate and frame size for video writer
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # Define the codec and create VideoWriter objects
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_flipped = cv2.VideoWriter(os.path.join(output_directory, f'{base_name}{run}_flipped.avi'), fourcc, frame_rate, frame_size, isColor=False)
    out_subtracted = cv2.VideoWriter(os.path.join(output_directory, f'{base_name}{run}_subtract.avi'), fourcc, frame_rate, frame_size, isColor=False)

    # Load the timestamps
    timestamps = pd.read_csv(os.path.join(timestamps_directory, f'{base_name}Red_timestamps_run{run}.csv'))

    # Frame counter and lists to store frames and valid timestamps
    frame_counter = 0
    frame_list = []
    valid_timestamps = []

    # Read video frame by frame
    while True:
        ret, frame = cap.read()

        # Break the loop if the frame cannot be read (end of video)
        if not ret:
            break

        # Convert the frame to grayscale and flip vertically
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.flip(frame, 0)

        # Write the flipped frame to the new video
        out_flipped.write(frame)

        # Check if frame contains a row filled with zeros
        if np.any(np.all(frame == 0, axis=1)):
            continue  # skip this frame

        # Append the frame to the frame list and corresponding timestamp
        frame_list.append(frame)
        valid_timestamps.append(timestamps.loc[frame_counter])

        # Update frame counter
        frame_counter += 1

    # Close the video file and the flipped video
    cap.release()
    out_flipped.release()

    # Convert frame list into numpy array for easier manipulation
    frame_array = np.array(frame_list)

    # Convert valid_timestamps into a DataFrame
    valid_timestamps = pd.DataFrame(valid_timestamps)

    # Identify frames which have timestamps less than 2 seconds
    frames_before_2s = frame_array[valid_timestamps['timestamp'] < 2]

    # Average these frames
    average_frame = np.mean(frames_before_2s, axis=0)

    # Subtract the average frame from each frame and normalize
    subtract_frame_array = np.abs(frame_array.astype(np.int32) - average_frame.astype(np.int32))
    global_min = np.min(subtract_frame_array)
    global_max = np.max(subtract_frame_array)
    subtract_frame_array = ((subtract_frame_array - global_min) * (255 / (global_max - global_min))).astype(np.uint8)

    # Write the subtracted frames to the new video and generate marginal histograms
    for i, subtract_frame in enumerate(subtract_frame_array):
        out_subtracted.write(subtract_frame)

        # Generate and save row and column marginal histograms
        for ax, prefix in zip([0, 1], ['column', 'row']):
            mean_intensities = np.mean(subtract_frame, axis=ax).astype(float)

            plt.figure(figsize=(6, 4))
            plt.plot(mean_intensities, 'k-')
            plt.xlabel('Column number' if ax == 0 else 'Row number')
            plt.ylabel('Mean intensity')

            timestamp = valid_timestamps.iloc[i]['timestamp']
            plt.text(0.95, 0.95, f'Time: {timestamp}', horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)

            plt.tight_layout()
            plt.savefig(os.path.join(output_directory, f'{prefix}marginal_{i}.png'))
            plt.close()

            savetxt(os.path.join(output_directory, f'{prefix}marginal_{i}.csv'), mean_intensities)

    # Close the subtracted video
    out_subtracted.release()

    print(f"Processed {base_name} run {run}")
