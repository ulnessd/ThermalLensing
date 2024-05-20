import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

class HeatmapGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Little Drummer Boy')
        self.geometry('400x550')  # Adjusted size to accommodate new widgets

        # Variables
        self.filename = tk.StringVar(value="filename")
        self.threshold = tk.DoubleVar(value=10)  # Default threshold
        self.min_pixel = tk.IntVar(value=100)  # Default min pixel
        self.max_pixel = tk.IntVar(value=600)  # Default max pixel
        self.index_threshold = tk.IntVar(value=100)  # Default index threshold
        self.show_points = tk.BooleanVar(value=True)  # Show points by default
        self.use_calibration = tk.BooleanVar(value=False)  # Use calibration
        self.space_calibration = tk.DoubleVar(value=0.0077017)  # Default space calibration
        self.time_calibration = tk.DoubleVar(value=0.010288)  # Default time calibration
        self.plot_range = tk.BooleanVar(value=False)  # Plot over a selected range
        self.min_frame = tk.IntVar(value=0)  # Default min frame
        self.max_frame = tk.IntVar(value=100)  # Default max frame

        # Widgets
        self.setup_widgets()

        # Directory to save to
        self.file_directory = ''

        # Data storage
        self.averaged_columns = []
        self.points_to_mark = []

    def setup_widgets(self):
        # File selection
        tk.Button(self, text='Open File', command=self.open_file).pack(fill='x')

        # Filename entry
        tk.Label(self, text="Filename for saving:").pack()
        tk.Entry(self, textvariable=self.filename).pack(fill='x')

        # Threshold entry
        tk.Label(self, text="Threshold value:").pack()
        tk.Entry(self, textvariable=self.threshold).pack(fill='x')

        # Min pixel entry
        tk.Label(self, text="Min pixel region:").pack()
        tk.Entry(self, textvariable=self.min_pixel).pack(fill='x')

        # Max pixel entry
        tk.Label(self, text="Max pixel region:").pack()
        tk.Entry(self, textvariable=self.max_pixel).pack(fill='x')

        # Index threshold entry
        tk.Label(self, text="Index threshold:").pack()
        tk.Entry(self, textvariable=self.index_threshold).pack(fill='x')

        # Show points checkbox
        tk.Checkbutton(self, text="Show Points", variable=self.show_points).pack()

        # Use calibration checkbox
        tk.Checkbutton(self, text="Use Calibration", variable=self.use_calibration).pack()

        # Space calibration entry
        tk.Label(self, text="Space calibration (mm/pixel):").pack()
        tk.Entry(self, textvariable=self.space_calibration).pack(fill='x')

        # Time calibration entry
        tk.Label(self, text="Time calibration (s/frame):").pack()
        tk.Entry(self, textvariable=self.time_calibration).pack(fill='x')

        # Plot range checkbox
        tk.Checkbutton(self, text="Plot over selected range", variable=self.plot_range).pack()

        # Min frame entry
        tk.Label(self, text="Min frame:").pack()
        tk.Entry(self, textvariable=self.min_frame).pack(fill='x')

        # Max frame entry
        tk.Label(self, text="Max frame:").pack()
        tk.Entry(self, textvariable=self.max_frame).pack(fill='x')

        # Save heatmap
        tk.Button(self, text='Save Heatmap', command=self.save_heatmap).pack(fill='x')

        # Save points
        tk.Button(self, text='Save Points', command=self.save_points).pack(fill='x')

        # Quit button
        tk.Button(self, text='Quit', command=self.quit).pack(fill='x')

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("H264 files", "*.h264"), ("All files", "*.*")])
        if file_path:
            self.file_directory = os.path.dirname(file_path)
            self.process_video(file_path)

    def process_video(self, input_file):
        cap = cv2.VideoCapture(input_file)
        self.averaged_columns = []
        self.points_to_mark = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_grey = frame[:, :, 2]
            frame_grey = cv2.flip(frame_grey, 0)
            cropped_frame = frame_grey[:, self.min_pixel.get():self.max_pixel.get()]
            averaged_column = np.mean(cropped_frame, axis=1)
            self.averaged_columns.append(averaged_column)

            for i, val in enumerate(averaged_column):
                if i > self.index_threshold.get() and val > self.threshold.get():
                    self.points_to_mark.append((i, len(self.averaged_columns) - 1))
                    break
        cap.release()
        messagebox.showinfo("Info", "Video processed successfully!")

    def save_heatmap(self):
        if not self.averaged_columns:
            messagebox.showwarning("Warning", "No data to save. Please load and process a video first.")
            return

        heatmap_data = np.array(self.averaged_columns).T

        # Apply selected frame range if checked
        if self.plot_range.get():
            min_frame = self.min_frame.get()
            max_frame = self.max_frame.get()
            heatmap_data = heatmap_data[:, min_frame:max_frame]

        # Apply calibration if checked
        if self.use_calibration.get():
            y_axis = np.arange(heatmap_data.shape[0]) * self.space_calibration.get()
            x_axis = np.arange(heatmap_data.shape[1]) * self.time_calibration.get()
            plt.imshow(heatmap_data, aspect='auto', cmap='inferno', extent=[x_axis.min(), x_axis.max(), y_axis.max(), y_axis.min()])
            plt.ylabel("Displacement (mm)")
            plt.xlabel("Time (s)")

            if self.show_points.get() and self.points_to_mark:
                points = list(zip(*self.points_to_mark))
                y_calibrated = [y * self.time_calibration.get() for y in points[1]]
                x_calibrated = [x * self.space_calibration.get() for x in points[0]]
                if self.plot_range.get():
                    y_calibrated = [y for y in y_calibrated if min_frame <= y <= max_frame]
                    x_calibrated = x_calibrated[:len(y_calibrated)]
                plt.scatter(y_calibrated, x_calibrated, color='blue', s=2, marker='o')

        else:
            plt.imshow(heatmap_data, aspect='auto', cmap='inferno')
            plt.xlabel("Time (frames)")
            plt.ylabel("Spatial Dimension (pixels)")

            if self.show_points.get() and self.points_to_mark:
                x, y = zip(*self.points_to_mark)
                if self.plot_range.get():
                    y = [frame for frame in y if min_frame <= frame <= max_frame]
                    x = x[:len(y)]
                plt.scatter(y, x, color='blue', s=2, marker='o')

        plt.title("Heatmap")

        file_path = os.path.join(self.file_directory, f'{self.filename.get()}.png')
        plt.savefig(file_path, dpi=600)
        plt.close()
        messagebox.showinfo("Info", f"Heatmap saved successfully in {file_path}!")

    def save_points(self):
        if not self.points_to_mark:
            messagebox.showwarning("Warning", "No points to save. Please load and process a video first.")
            return

        # Reordering the data within each tuple from (Pixel Index, Frame Number) to (Frame Number, Pixel Index)
        reordered_data = [(frame_number, pixel_index) for pixel_index, frame_number in self.points_to_mark]

        # Now creating the DataFrame with the reordered data
        df = pd.DataFrame(reordered_data, columns=['Frame Number', 'Pixel Index'])
        file_path = os.path.join(self.file_directory, f'{self.filename.get()}.csv')
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Info", f"Points saved successfully in {file_path}!")

if __name__ == "__main__":
    app = HeatmapGUI()
    app.mainloop()
