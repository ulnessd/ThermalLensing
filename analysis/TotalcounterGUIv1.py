import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import cv2
import numpy as np
import glob
import os
import csv
import re

# Video processing functions
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    avg_frame = np.zeros((frame_height, frame_width), np.float32)

    for i in range(100):
        ret, frame = cap.read()
        if not ret:
            break
        avg_frame += frame[:, :, 2] / 100  # Using the red channel

    cap.set(cv2.CAP_PROP_POS_FRAMES, 300)
    total_sum_of_squares = 0

    for i in range(100):
        ret, frame = cap.read()
        if not ret:
            break

        diff_frame = frame[:, :,2] - avg_frame
        diff_frame[np.abs(diff_frame) < 20] = 0
        sum_of_squares = np.sum(np.square(diff_frame))
        total_sum_of_squares += sum_of_squares

    cap.release()

    # Calculate the mean of the squared differences for each frame
    num_pixels = frame_width * frame_height
    mean_squared_value = total_sum_of_squares / (
                num_pixels * 100)  # Divided by the number of pixels and the number of frames
    root_mean_squared_value=mean_squared_value**0.5
    return root_mean_squared_value


def process_sample_directory(directory):
    video_files = glob.glob(os.path.join(directory, "*.h264"))
    sample_names = set(re.match(r'(.+?)Red\d+\.h264', os.path.basename(file)).group(1) for file in video_files)
    results = {}


    for sample_name in sample_names:
        file_pattern = os.path.join(directory, f"{sample_name}Red*.h264")
        sample_video_files = glob.glob(file_pattern)
        averages = []

        for video_file in sample_video_files:
            avg = process_video(video_file)
            if avg is not None:
                averages.append(avg)

        if averages:
            results[sample_name] = np.mean(averages)

    return results

def write_to_csv(results, directory, output_file_name):
    output_file_path = os.path.join(directory, output_file_name)
    with open(output_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Sample Name', 'Average Value'])
        for sample_name, avg_value in results.items():
            writer.writerow([sample_name, avg_value])


# Tkinter GUI Application
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Video Processing Application")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        # Folder Selection
        self.folder_button = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(pady=10)

        # Output File Name
        tk.Label(self, text="Output CSV File Name:").pack()
        self.output_file_name = tk.Entry(self)
        self.output_file_name.pack()

        # Process Folder Button
        self.process_button = tk.Button(self, text="Process Folder", command=self.process_folder)
        self.process_button.pack(pady=10)

        # Console/Progress Area
        self.console = scrolledtext.ScrolledText(self, state='disabled', height=10)
        self.console.pack(pady=10)

        # Quit Button
        self.quit_button = tk.Button(self, text="Quit", command=self.destroy)
        self.quit_button.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.console_insert(f"Selected Folder: {self.folder_path}\n")

    def console_insert(self, text):
        self.console.configure(state='normal')
        self.console.insert(tk.END, text)
        self.console.configure(state='disabled')

    def process_folder(self):
        output_file = self.output_file_name.get()
        if not output_file:
            messagebox.showerror("Error", "Please enter a name for the output CSV file.")
            return

        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        # Run the processing in a separate thread to prevent UI freezing
        threading.Thread(target=self.run_processing, args=(self.folder_path, output_file), daemon=True).start()

    def run_processing(self, folder_path, output_file_name):
        try:
            self.console_insert("Processing started...\n")
            results = process_sample_directory(folder_path)
            if results:
                write_to_csv(results, folder_path, output_file_name)
                self.console_insert(
                    f"Processing completed.\nResults saved to {os.path.join(folder_path, output_file_name)}\n")
            else:
                self.console_insert("No results to save.\n")
        except Exception as e:
            self.console_insert(f"An error occurred: {e}\n")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
