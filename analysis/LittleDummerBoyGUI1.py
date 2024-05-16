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
        self.title('Little Dummer Boy')
        self.geometry('400x200')

        # Variables
        self.filename = tk.StringVar(value="filename")
        self.threshold = tk.DoubleVar(value=10)  # Default threshold

        # Widgets
        self.setup_widgets()

        #directoy to save to
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
            cropped_frame = frame_grey[:, 100:600]
            averaged_column = np.mean(cropped_frame, axis=1)
            self.averaged_columns.append(averaged_column)

            for i, val in enumerate(averaged_column):
                if i > 100 and val > self.threshold.get():
                    self.points_to_mark.append((i, len(self.averaged_columns) - 1))
                    break
        cap.release()
        messagebox.showinfo("Info", "Video processed successfully!")


    def save_heatmap(self):
        if not self.averaged_columns:
            messagebox.showwarning("Warning", "No data to save. Please load and process a video first.")
            return

        heatmap_data = np.array(self.averaged_columns).T
        plt.imshow(heatmap_data, aspect='auto', cmap='inferno')
        plt.colorbar()
        plt.title("Heatmap of Averaged Columns")
        plt.xlabel("Time (frames)")
        plt.ylabel("Spatial Dimension")

        if self.points_to_mark:
            x, y = zip(*self.points_to_mark)
            plt.scatter(y, x, color='blue', s=2, marker='o')

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
