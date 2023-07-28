import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import cv2
import csv
from glob import glob
import numpy as np
import warnings

# Ignore RankWarning
warnings.simplefilter('ignore', np.RankWarning)

class App:
    def __init__(self, root):
        self.root = root
        root.title("Photothermal Imaging Analysis")
        #self.root.iconbitmap('Centroid42.ico')

        # Create tabs
        self.tab_parent = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_parent)
        self.tab2 = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.tab1, text="Video Conversion")
        self.tab_parent.add(self.tab2, text="Wavefront Calculation")
        self.tab_parent.pack(expand=1, fill='both')

        # Video Conversion Tab
        self.folder_label1 = ttk.Label(self.tab1, text="Raw Data Folder:")
        self.folder_label1.grid(row=0, column=0, sticky='W', padx=25, pady=5)
        self.folder_entry1 = ttk.Entry(self.tab1)
        self.folder_entry1.grid(row=0, column=1, padx=5, pady=5)
        self.browse_button1 = ttk.Button(self.tab1, text="Browse...",
                                         command=lambda: self.browse_input(self.folder_entry1))
        self.browse_button1.grid(row=0, column=2, padx=5, pady=5)
        self.frame_number_label = ttk.Label(self.tab1, text="Background frames: ")
        self.frame_number_label.grid(row=1, column=0, sticky='W', padx=25, pady=5)
        self.frame_number_entry = ttk.Entry(self.tab1)
        self.frame_number_entry.grid(row=1, column=1, padx=5, pady=5)
        self.frame_number_entry.insert(0, "120")  # default value
        self.convert_button = ttk.Button(self.tab1, text="Convert Videos", command=self.convert_videos)
        self.convert_button.grid(row=2, column=0, columnspan=3, pady=5)
        self.quit_button1 = ttk.Button(self.tab1, text="Quit", command=self.root.destroy)
        self.quit_button1.grid(row=3, column=0, columnspan=3, pady=5)
        self.console1 = tk.Text(self.tab1, width=50, height=10)
        self.console1.grid(row=4, column=0, columnspan=3, padx=25, pady=5)

        # Centroid Calculation Tab
        self.folder_label2 = ttk.Label(self.tab2, text="Processed Data Folder:")
        self.folder_label2.grid(row=0, column=0, sticky='W', padx=25, pady=5)
        self.folder_entry2 = ttk.Entry(self.tab2)
        self.folder_entry2.grid(row=0, column=1, padx=5, pady=5)
        self.browse_button2 = ttk.Button(self.tab2, text="Browse...",
                                         command=lambda: self.browse_input(self.folder_entry2))
        self.browse_button2.grid(row=0, column=2, padx=5, pady=5)

        self.threshold_label2 = ttk.Label(self.tab2, text="Threshold:")  # New label for threshold
        self.threshold_label2.grid(row=1, column=0, sticky='W', padx=25, pady=5)  # Add to row=1
        self.threshold_entry2 = ttk.Entry(self.tab2)
        self.threshold_entry2.insert(0, '20')  # Default threshold value
        self.threshold_entry2.grid(row=1, column=1, padx=5, pady=5)  # Add to row=1

        self.column_min_label2 = ttk.Label(self.tab2, text="Min Column Selection:")  # New label for column selection
        self.column_min_label2.grid(row=2, column=0, sticky='W', padx=25, pady=5)  # Add to row=2
        self.column_min_entry2 = ttk.Entry(self.tab2)
        self.column_min_entry2.insert(0, '0')  # Default column selection value
        self.column_min_entry2.grid(row=2, column=1, padx=5, pady=5)  # Add to row=2

        self.column_max_label2 = ttk.Label(self.tab2, text="Max Column Selection:")  # New label for column selection
        self.column_max_label2.grid(row=3, column=0, sticky='W', padx=25, pady=5)  # Add to row=2
        self.column_max_entry2 = ttk.Entry(self.tab2)
        self.column_max_entry2.insert(0, '719')  # Default column selection value
        self.column_max_entry2.grid(row=3, column=1, padx=5, pady=5)  # Add to row=2

        self.calculate_button = ttk.Button(self.tab2, text="Calculate Wavefront", command=self.calculate_centroids)
        self.calculate_button.grid(row=4, column=0, columnspan=3, pady=5)
        self.quit_button2 = ttk.Button(self.tab2, text="Quit", command=self.root.destroy)
        self.quit_button2.grid(row=5, column=0, columnspan=3, pady=5)
        self.console2 = tk.Text(self.tab2, width=50, height=10)
        self.console2.grid(row=6, column=0, columnspan=3, padx=25, pady=5)

    def browse_input(self, entry_field):
        folder_path = filedialog.askdirectory()
        entry_field.delete(0, tk.END)  # delete any previous input
        entry_field.insert(0, folder_path)

    def convert_videos(self):
        # Get the directory and frame number from the GUI inputs
        directory = self.folder_entry1.get()
        frame_num = int(self.frame_number_entry.get())

        # Video processing and subtraction operation
        self.console1.insert(tk.END, "Finding all raw data files...\n")
        self.root.update_idletasks()

        # Use glob to get a list of all .h264 files in the directory
        input_files = glob(f"{directory}/*.h264")
        self.console1.insert(tk.END, "Starting to process raw data files...\n")
        self.root.update_idletasks()
        self.console1.insert(tk.END, "This could take a long time...\n")
        self.root.update_idletasks()

        # Process each file
        for input_file in input_files:
            # Parse the base file name
            base_name = os.path.splitext(os.path.basename(input_file))[0]

            # Construct the output file names
            grey_file = f"{directory}/{base_name}_flipped.avi"
            subtract_file = f"{directory}/{base_name}_subtract.avi"

            # Open the video file
            cap = cv2.VideoCapture(input_file)

            # Get the frame size and frame rate
            frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            frame_rate = cap.get(cv2.CAP_PROP_FPS)

            # Define the codec
            fourcc = cv2.VideoWriter_fourcc(*'XVID')

            # Create VideoWriter objects for the greyscale and subtracted videos
            out_grey = cv2.VideoWriter(grey_file, fourcc, frame_rate, frame_size, isColor=False)

            # Frame counter and list to store the first 120 frames
            frame_counter = 0
            first_frames = []

            subtract_frames = []
            global_min_subtract = np.inf
            global_max_subtract = -np.inf

            # Read video frame by frame
            while True:
                ret, frame = cap.read()

                # Break the loop if the frame cannot be read (end of video)
                if not ret:
                    break

                # Convert the frame to grayscale using the red channel, flip vertically, and save
                frame_grey = frame[:, :, 2]
                frame_grey = cv2.flip(frame_grey, 0)
                out_grey.write(frame_grey)

                # If it's one of the first 120 frames, add it to the list
                if frame_counter < 120:
                    first_frames.append(frame_grey)
                else:
                    # Calculate the average of the first 120 frames
                    average_frame = np.mean(first_frames, axis=0)

                    # Subtract the average frame from the current frame
                    subtract_frame = np.abs(frame_grey.astype(np.int32) - average_frame.astype(np.int32))
                    min_val = np.min(subtract_frame)
                    max_val = np.max(subtract_frame)
                    if min_val < global_min_subtract:
                        global_min_subtract = min_val
                    if max_val > global_max_subtract:
                        global_max_subtract = max_val

                    subtract_frames.append(subtract_frame)

                # Update frame counter
                frame_counter += 1

            # Create VideoWriter object for the subtracted video
            out_subtract = cv2.VideoWriter(subtract_file, fourcc, frame_rate, frame_size, isColor=False)

            # Normalize and write the subtracted frames
            for frame in subtract_frames:
                frame = ((frame - global_min_subtract) * (255 / (global_max_subtract - global_min_subtract))).astype(
                    np.uint8)
                out_subtract.write(frame)

            # Release everything when done
            cap.release()
            out_grey.release()
            out_subtract.release()
            self.console1.insert(tk.END, f"{base_name} processed...\n")
            self.root.update_idletasks()

        self.console1.insert(tk.END, "All raw data files processed.\n")
        self.root.update_idletasks()

        self.console1.insert(tk.END, "Averaging processed videos...\n")
        self.root.update_idletasks()
        # Video averaging

        input_files = glob(f"{directory}/*Red*_subtract.avi")

        # Group files by base name (without the run number)
        grouped_files = {}
        for input_file in input_files:
            base_name = os.path.basename(input_file).split('Red')[0]
            if base_name not in grouped_files:
                grouped_files[base_name] = []
            grouped_files[base_name].append(input_file)

        # Process each group of files
        for base_name, files in grouped_files.items():
            self.console1.insert(tk.END, f"Processing {base_name}...\n")
            self.root.update_idletasks()

            # Initialize a list to hold the frames
            sum_frames = []

            for file in files:
                # Open the video file
                cap = cv2.VideoCapture(file)

                # Get the frame size and frame rate
                frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                frame_rate = cap.get(cv2.CAP_PROP_FPS)

                # Read video frame by frame
                frame_counter = 0
                while True:
                    ret, frame = cap.read()

                    # Break the loop if the frame cannot be read (end of video)
                    if not ret:
                        break

                    # Convert the frame to grayscale
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # If we need to add a new frame to sum_frames, do so
                    if frame_counter >= len(sum_frames):
                        sum_frames.append(np.zeros((frame_size[1], frame_size[0]), dtype=np.float64))

                    # Add the current frame to the appropriate frame in sum_frames
                    sum_frames[frame_counter] += frame

                    # Update frame counter
                    frame_counter += 1

                # If the current video had less frames than others, add black frames
                while frame_counter < len(sum_frames):
                    sum_frames[frame_counter] += np.zeros((frame_size[1], frame_size[0]), dtype=np.float64)
                    frame_counter += 1

                # Release the VideoCapture
                cap.release()

            # Calculate the average frames
            avg_frames = [(frame / len(files)).astype(np.uint8) for frame in sum_frames]

            # Define the codec and create a VideoWriter object
            out_file = f"{directory}/{base_name}Red_average_subtract.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(out_file, fourcc, frame_rate, frame_size, isColor=False)

            # Write the average frames to the new video file
            for frame in avg_frames:
                out.write(frame)

            # Release the VideoWriter
            out.release()

            self.console1.insert(tk.END, f"{base_name} processed...\n")
            self.root.update_idletasks()

        self.console1.insert(tk.END, "All subtract data files processed.\n")
        self.root.update_idletasks()


        # Time calibration
        self.console1.insert(tk.END, "Getting time information.\n")
        self.root.update_idletasks()

        input_files = glob(f"{directory}/**/*Red*_flipped.avi", recursive=True)

        for input_file in input_files:
            # Parse the base file name
            base_name = os.path.splitext(os.path.basename(input_file))[0]

            # Construct the information file name
            info_file = f"{directory}/{base_name.split('Red')[0]}Red_info.txt"

            # Open the info file and get experiment parameters
            with open(info_file, 'r') as f:
                lines = f.readlines()
                background_time = float(lines[-3].split(": ")[1])
                laser_on_time = float(lines[-2].split(": ")[1])
                recovery_time = float(lines[-1].split(": ")[1])

            # Calculate the total experiment time
            total_experiment_time = background_time + laser_on_time + recovery_time

            # Count the frames in the video
            cap = cv2.VideoCapture(input_file)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()

            # Calculate the time per frame
            time_per_frame = total_experiment_time / total_frames

            # Prepare the time calibration csv file
            time_calibration_file = f"{directory}/{base_name}_timecal.csv"


            # Write frame and time data to the csv file
            with open(time_calibration_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["frame", "time"])
                for i in range(total_frames):
                    writer.writerow([i, i * time_per_frame])

            # Update console instead of printing
            self.console1.insert(tk.END, f"Done with {input_file}\n")
            self.console1.see(tk.END)  # scroll to the end

        self.console1.insert(tk.END, "Time calibration files generated.\n")
        self.root.update_idletasks()
        self.console1.see(tk.END)  # scroll to the end


    # Polynomial function for curve fitting
    def polynomial(x, a, b, c):
        return a * x ** 2 + b * x + c

    def calculate_centroids(self):
        # Get the directory from the GUI inputs
        directory = self.folder_entry2.get()

        # Get the threshold from the GUI inputs
        try:
            threshold = int(self.threshold_entry2.get())
        except ValueError:
            self.console2.insert(tk.END, "Threshold should be an integer value.\n")
            self.root.update_idletasks()
            return

        # Get the column min and max values
        try:
            col_min = int(self.column_min_entry2.get())
            col_max = int(self.column_max_entry2.get())
        except ValueError:
            self.console2.insert(tk.END, "Column selection should be integer values.\n")
            self.root.update_idletasks()
            return

        # Centroid calculation
        self.console2.insert(tk.END, "Finding all processed data files...\n")
        self.root.update_idletasks()

        # Use glob to get a list of all subtracted .avi files in the directory
        input_files = glob(f"{directory}/*subtract.avi")
        self.console2.insert(tk.END, "Starting to calculate wavefront...\n")
        self.root.update_idletasks()
        self.console2.insert(tk.END, "This can take a long time...\n")
        self.root.update_idletasks()

        # Process each file
        for input_file in input_files:
            # Parse the base file name
            base_name = os.path.splitext(os.path.basename(input_file))[0]

            # Construct the centroid file name
            centroid_file = f"{directory}/{base_name}_wavefront.csv"

            # Open the video file
            cap = cv2.VideoCapture(input_file)

            # Get video dimensions for the output video
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Prepare the output video file
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(f'{directory}/{base_name}_wavefront.avi', fourcc, fps, (frame_width, frame_height))

            # Prepare the centroid csv file
            with open(centroid_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["frame", "pixel"])  # write the header

                frame_number = 0
                while True:
                    # Read the frame
                    ret, frame = cap.read()

                    # Break the loop if the frame cannot be read (end of video)
                    if not ret:
                        break

                    # Convert the frame to grayscale
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # Crop the frame to the selected column range
                    cropped_frame = gray_frame[:, col_min:col_max]

                    # Find the first pixel in each column that is above the threshold, coming down from the top
                    x_positions = []
                    y_positions = []
                    for col in range(col_min, col_max):
                        for row in range(cropped_frame.shape[0]):
                            if cropped_frame[row, col - col_min] > threshold:
                                x_positions.append(col)
                                y_positions.append(row)  # Save the y coordinate
                                break  # Stop the loop after finding the first one

                    # If positions are found, calculate the average, write to the file, and fit polynomial to points and plot on the frame
                    if x_positions and y_positions:
                        avg_y_position = np.mean(y_positions)
                        avg_y_position_top = 720-avg_y_position
                        writer.writerow([frame_number, avg_y_position_top])

                        # Fit the points to a 2nd order polynomial
                        coeffs = np.polyfit(x_positions, y_positions, 2)  # Fit a 2nd degree polynomial
                        poly = np.poly1d(coeffs)

                        # Create a range of x values to plot
                        x_range = np.arange(col_min, col_max)

                        # Calculate the corresponding y values from the polynomial
                        y_poly = poly(x_range)

                        # Plot the polynomial line onto the video frame
                        for x, y in zip(x_range, y_poly):
                            if 0 <= int(y) < frame.shape[0]:  # To ensure the point lies within the frame
                                frame[int(y), int(x)] = [0, 255, 255]  # Yellow line

                    # Write the frame to the output video
                    out.write(frame)

                    frame_number += 1

            # Release the video capture and writer
            cap.release()
            out.release()

            # Update console instead of printing
            self.console2.insert(tk.END, f"Done with {input_file}\n")
            self.console2.see(tk.END)  # scroll to the end

        self.console2.insert(tk.END, "Centroids calculated for all files.\n")
        self.root.update_idletasks()
        self.console2.see(tk.END)  # scroll to the end


# Insert centroid calculation code here

root = tk.Tk()
root.geometry("475x475")
app = App(root)
root.mainloop()
