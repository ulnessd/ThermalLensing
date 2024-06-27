import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import pandas as pd
import os

class HeatmapGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Plume Volume Tracker')
        self.geometry('400x200')

        # Variables
        self.threshold = tk.DoubleVar(value=60)  # Default threshold
        self.file_directory = ''
        self.input_files = []

        # Widgets
        self.setup_widgets()

    def setup_widgets(self):
        # File selection
        tk.Button(self, text='Load Files', command=self.load_files).pack(fill='x')

        # Threshold entry
        tk.Label(self, text="Threshold value:").pack()
        tk.Entry(self, textvariable=self.threshold).pack(fill='x')

        # Process video button
        tk.Button(self, text='Process Files', command=self.process_files).pack(fill='x')

        # Quit button
        tk.Button(self, text='Quit', command=self.quit).pack(fill='x')

    def load_files(self):
        self.input_files = filedialog.askopenfilenames(filetypes=[("H264 files", "*.h264"), ("All files", "*.*")])
        if self.input_files:
            self.file_directory = os.path.dirname(self.input_files[0])
            messagebox.showinfo("Info", f"Loaded files: {len(self.input_files)}")

    def process_files(self):
        if not self.input_files:
            messagebox.showwarning("Warning", "No files loaded. Please load files first.")
            return

        threshold = self.threshold.get()
        area_data = {}
        max_frames = 0

        for input_file in self.input_files:
            base_filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(self.file_directory, f"{base_filename}_vol.avi")
            file_area_data = process_video(input_file, output_file, threshold)

            if 'Frame' not in area_data:
                # Initialize the frame list the first time
                area_data['Frame'] = [frame for frame, _ in file_area_data]
                max_frames = len(file_area_data)
            elif len(file_area_data) > max_frames:
                # Extend the frame list if the current video is longer
                area_data['Frame'].extend(range(max_frames + 1, len(file_area_data) + 1))
                max_frames = len(file_area_data)

            # Add area data for the current file
            area_data[base_filename] = [area for _, area in file_area_data]

        # Pad shorter area data lists with NaNs
        for key, values in area_data.items():
            if len(values) < max_frames:
                area_data[key] += [float('nan')] * (max_frames - len(values))

        save_area_data_csv(area_data, self.file_directory)
        messagebox.showinfo("Info", "Processing complete and data saved.")


def process_video(input_file, output_file, threshold=40, num_frames_to_average=120, min_area=100):
    cap = cv2.VideoCapture(input_file)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video file.")
        return []

    frame_sum = None
    frame_count = 0
    area_data = []

    frame_sum = None
    frame_count = 0
    target_pixel = None
    area_data = []

    # Read and accumulate the first 120 frames
    while frame_count < num_frames_to_average:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Could not read frame.")
            return
        frame_grey = frame[:, :, 2]
        frame_grey = cv2.flip(frame_grey, 0)
        if frame_sum is None:
            frame_sum = np.zeros_like(frame_grey, dtype=np.float64)
        frame_sum += frame_grey
        frame_count += 1

    # Calculate the average frame
    avg_frame = (frame_sum / frame_count).astype(np.float64)

    # Reset the video capture to the beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (frame_grey.shape[1], frame_grey.shape[0]), isColor=False)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_grey = frame[:, :, 2]
        frame_grey = cv2.flip(frame_grey, 0)

        # Subtract the average frame
        diff_frame = frame_grey.astype(np.float64) - avg_frame

        # Apply threshold
        binary_frame = np.where(np.abs(diff_frame) > threshold, 1, 0).astype(np.uint8) * 255

        # Apply morphological operations to remove noise
        kernel = np.ones((3, 3), np.uint8)
        binary_frame = cv2.morphologyEx(binary_frame, cv2.MORPH_OPEN, kernel)
        binary_frame = cv2.morphologyEx(binary_frame, cv2.MORPH_CLOSE, kernel)

        # Identify and fill the largest connected component
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_frame, connectivity=8)

        if num_labels > 1:
            valid_regions = []
            for i in range(1, num_labels):
                if stats[i, cv2.CC_STAT_AREA] >= min_area:
                    valid_regions.append(i)

            if valid_regions:
                if target_pixel is None:
                    # Find the largest component in the first frame with valid components
                    largest_component = max(valid_regions, key=lambda i: stats[i, cv2.CC_STAT_AREA])
                    target_pixel = centroids[largest_component].astype(int)
                else:
                    # Find the component containing the target pixel
                    target_label = labels[target_pixel[1], target_pixel[0]]
                    if target_label == 0 or target_label not in valid_regions:
                        # If the target pixel is not within any component, fallback to the largest valid component
                        largest_component = max(valid_regions, key=lambda i: stats[i, cv2.CC_STAT_AREA])
                    else:
                        largest_component = target_label

                # Create an output image where only the tracked component is white
                filled_frame = np.zeros_like(binary_frame)
                filled_frame[labels == largest_component] = 255

                # Calculate the area of the tracked component
                area = stats[largest_component, cv2.CC_STAT_AREA]
            else:
                filled_frame = binary_frame
                area = 0
        else:
            filled_frame = binary_frame
            area = 0

        area_data.append([frame_count, area])

        # Write the frame to the output file
        out.write(filled_frame)
        frame_count += 1

    # Release everything when done
    cap.release()
    out.release()

    return area_data


def save_area_data_csv(area_data, directory):
    # Find the maximum length of the frame data
    max_length = max(len(v) for v in area_data.values())

    # Pad shorter lists with NaN to match the maximum length
    padded_area_data = {key: value + [float('nan')] * (max_length - len(value)) if len(value) < max_length else value
                        for key, value in area_data.items()}

    # Create DataFrame from padded data
    df = pd.DataFrame(padded_area_data)
    output_csv_file = os.path.join(directory, "compiled_area_data.csv")
    df.to_csv(output_csv_file, index=False)


if __name__ == "__main__":
    app = HeatmapGUI()
    app.mainloop()
