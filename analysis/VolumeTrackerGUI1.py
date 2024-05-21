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
        self.filename = tk.StringVar(value="filename")
        self.threshold = tk.DoubleVar(value=60)  # Default threshold
        self.file_directory = ''
        self.input_file = ''

        # Widgets
        self.setup_widgets()

    def setup_widgets(self):
        # File selection
        tk.Button(self, text='Load File', command=self.load_file).pack(fill='x')

        # Threshold entry
        tk.Label(self, text="Threshold value:").pack()
        tk.Entry(self, textvariable=self.threshold).pack(fill='x')

        # Filename entry
        tk.Label(self, text="Base Filename:").pack()
        tk.Entry(self, textvariable=self.filename).pack(fill='x')

        # Process video button
        tk.Button(self, text='Dump AVI and CSV', command=self.dump_files).pack(fill='x')

        # Quit button
        tk.Button(self, text='Quit', command=self.quit).pack(fill='x')

    def load_file(self):
        self.input_file = filedialog.askopenfilename(filetypes=[("H264 files", "*.h264"), ("All files", "*.*")])
        if self.input_file:
            self.file_directory = os.path.dirname(self.input_file)
            messagebox.showinfo("Info", f"Loaded file: {self.input_file}")

    def dump_files(self):
        if not self.input_file:
            messagebox.showwarning("Warning", "No file loaded. Please load a file first.")
            return

        base_filename = self.filename.get()
        threshold = self.threshold.get()
        output_file = os.path.join(self.file_directory, f"{base_filename}.avi")
        csv_file = os.path.join(self.file_directory, f"{base_filename}_area_data.csv")

        process_video(self.input_file, output_file, csv_file, threshold)
        messagebox.showinfo("Info", f"Files saved as {output_file} and {csv_file}")

def process_video(input_file, output_file, csv_file, threshold=40, num_frames_to_average=120, min_area=100):
    cap = cv2.VideoCapture(input_file)

    # Check if video opened successfully
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video file.")
        return

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

    # Save the frame and area data to a CSV file
    df = pd.DataFrame(area_data, columns=['Frame', 'Area'])
    df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    app = HeatmapGUI()
    app.mainloop()
