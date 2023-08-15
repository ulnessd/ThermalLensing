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
        self.tab3 = ttk.Frame(self.tab_parent)
        self.tab4 = ttk.Frame(self.tab_parent)
        self.tab5 = ttk.Frame(self.tab_parent)
        self.tab_parent.add(self.tab1, text="Video Conversion")
        self.tab_parent.add(self.tab2, text="Wavefront Calculation")
        self.tab_parent.add(self.tab3, text="Averager")
        self.tab_parent.add(self.tab4, text="Filter")
        self.tab_parent.add(self.tab5, text="Difference")
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
        self.quit_button2.grid(row=6, column=0, columnspan=3, pady=5)
        self.console2 = tk.Text(self.tab2, width=50, height=10)
        self.console2.grid(row=5, column=0, columnspan=3, padx=25, pady=5)

        #averager tab
        self.folder_label3 = ttk.Label(self.tab3, text="Files to average:")
        self.folder_label3.grid(row=0, column=0, sticky='W', padx=25, pady=5)
        self.folder_entry3= ttk.Entry(self.tab3)
        self.folder_entry3.grid(row=0, column=1, padx=5, pady=5)
        self.browse_button3 = ttk.Button(self.tab3, text="Browse...",
                                         command=lambda: self.browse_input(self.folder_entry3))
        self.browse_button3.grid(row=0, column=2, padx=5, pady=5)

        self.calculate_button3=ttk.Button(self.tab3, text="Average Videos", command=self.execute_averaging).grid(row=1, columnspan=2, pady=10)
        self.outputfile_label3=ttk.Label(self.tab3,text="Output File Name:")
        self.outputfile_label3.grid(row=2, column=0, sticky='W', padx=25, pady=5)
        self.outputfile_label3= ttk.Entry(self.tab3)
        self.outputfile_label3.insert(0,"filename.avi")
        self.outputfile_label3.grid(row=2, column=1, padx=5, pady=5)


        self.quit_button3 = ttk.Button(self.tab3, text="Quit", command=self.root.destroy)
        self.quit_button3.grid(row=5, column=0, columnspan=3, pady=5)
        self.console3 = tk.Text(self.tab3, width=50, height=10)
        self.console3.grid(row=3, column=0, columnspan=3, padx=25, pady=5)

        #Gaussian filter tab
        self.folder_label4 = ttk.Label(self.tab4, text="Files to filter:")
        self.folder_label4.grid(row=0, column=0, sticky='W', padx=25, pady=5)
        self.folder_entry4= ttk.Entry(self.tab4)
        self.folder_entry4.grid(row=0, column=1, padx=5, pady=5)
        self.browse_button4 = ttk.Button(self.tab4, text="Browse...",
                                         command=lambda: self.browse_input(self.folder_entry4))
        self.browse_button4.grid(row=0, column=2, padx=5, pady=5)

        self.win_size4_label4 = ttk.Label(self.tab4, text="Window size")
        self.win_size4_label4.grid(row=1, column=0, padx=5, pady=5)
        self.win_size4_entry4 = ttk.Entry(self.tab4)
        self.win_size4_entry4.insert(0,"5")
        self.win_size4_entry4.grid(row=1, column=1, padx=5, pady=5)

        self.calculate_filter4=ttk.Button(self.tab4, text="Filter Videos", command=self.apply_gaussian_filter_from_gui).grid(row=2, columnspan=2, pady=10)

        self.quit_button4 = ttk.Button(self.tab4, text="Quit", command=self.root.destroy)
        self.quit_button4.grid(row=5, column=0, columnspan=3, pady=5)
        self.console4 = tk.Text(self.tab4, width=50, height=10)
        self.console4.grid(row=3, column=0, columnspan=3, padx=25, pady=5)


        #Difference tab
        self.positive_label5 = ttk.Label(self.tab5, text="Positive avi file:")
        self.positive_label5.grid(row=0, column=0, sticky='W', padx=25, pady=5)
        self.positive_entry5= ttk.Entry(self.tab5)
        self.positive_entry5.grid(row=0, column=1, padx=5, pady=5)
        self.browse_positive5 = ttk.Button(self.tab5, text="Browse file",
                                         command=lambda: self.browse_file(self.positive_entry5))
        self.browse_positive5.grid(row=0, column=2, padx=5, pady=5)

        self.negative_label5 = ttk.Label(self.tab5, text="Negative avi file:")
        self.negative_label5.grid(row=2, column=0, sticky='W', padx=25, pady=5)
        self.negative_entry5= ttk.Entry(self.tab5)
        self.negative_entry5.grid(row=2, column=1, padx=5, pady=5)
        self.browse_negative5 = ttk.Button(self.tab5, text="Browse file",
                                         command=lambda: self.browse_file(self.negative_entry5))
        self.browse_negative5.grid(row=2, column=2, padx=5, pady=5)

        self.difference_label5 = ttk.Label(self.tab5, text="Difference file name:")
        self.difference_label5.grid(row=3, column=0, sticky='W', padx=25, pady=5)
        self.difference_entry5= ttk.Entry(self.tab5)
        self.difference_entry5.grid(row=3, column=1, padx=5, pady=5)
        self.difference_entry5.insert(0,"difference.avi")

        self.calculate_filter5 = ttk.Button(self.tab5, text="Subtract Videos", command=self.compute_difference).grid(row=4, columnspan=2, pady=10)


        self.quit_button5 = ttk.Button(self.tab5, text="Quit", command=self.root.destroy)
        self.quit_button5.grid(row=6, column=0, columnspan=3, pady=5)
        self.console5 = tk.Text(self.tab5, width=50, height=10)
        self.console5.grid(row=5, column=0, columnspan=3, padx=25, pady=5)

    def compute_difference(self):
        self.console5.insert(tk.END, "Computing difference video\n")
        self.root.update_idletasks()
        # Create the red to white color transition
        red_white = np.zeros((128, 1, 3), dtype=np.uint8)
        red_white[:, 0, 2] = 255  # R channel is always 255
        red_white[:, 0, 1] = np.linspace(0, 255, 128)  # G channel goes from 0 to 255
        red_white[:, 0, 0] = np.linspace(0, 255, 128)  # B channel goes from 0 to 255

        # Create the white to blue color transition
        white_blue = np.zeros((128, 1, 3), dtype=np.uint8)
        white_blue[:, 0, 2] = np.linspace(255, 0, 128)  # R channel goes from 255 to 0
        white_blue[:, 0, 1] = np.linspace(255, 0, 128)  # G channel goes from 255 to 0
        white_blue[:, 0, 0] = 255  # B channel is always 255

        # Combine the two transitions to get the final colormap
        custom_cmap = np.vstack((red_white, white_blue))

        # Paths from the GUI
        positive_video_path = self.positive_entry5.get()
        negative_video_path = self.negative_entry5.get()
        output_directory = os.path.dirname(positive_video_path)

        output_filename = self.difference_entry5.get()
        if not output_filename.lower().endswith('.avi'):
            output_filename += '.avi'
        full_output_path = f"{output_directory}\\{output_filename}"

        # Load videos
        cap1 = cv2.VideoCapture(positive_video_path)
        cap2 = cv2.VideoCapture(negative_video_path)

        # Check if videos opened successfully
        if not cap1.isOpened() or not cap2.isOpened():
            self.console5.insert(tk.END, "Error opening video stream or file\n")
            self.root.update_idletasks()
            return

        # Get video properties
        frame_width = int(cap1.get(3))
        frame_height = int(cap1.get(4))
        fps = cap1.get(cv2.CAP_PROP_FPS)

        # VideoWriter object
        # Define the codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(full_output_path, fourcc, fps,
                              (frame_width, frame_height))

        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            #Padding logic
            if not ret1 and ret2:
                frame1 = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)  # Note the ,3 for 3 channels
            elif ret1 and not ret2:
                frame2 = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)  # Note the ,3 for 3 channels
            elif not ret1 and not ret2:
                break

            # Convert frames to grayscale
            #frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            #frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            frame1_gray = frame1
            frame2_gray = frame2

            # Subtract frames
            difference = frame1_gray.astype(np.int16) - frame2_gray.astype(np.int16)

            # Normalize
            normalized_difference = cv2.normalize(difference, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Apply color map
            color_mapped_difference = cv2.applyColorMap(normalized_difference, custom_cmap)

            # Write to output
            out.write(color_mapped_difference)

        # Release resources
        cap1.release()
        cap2.release()
        out.release()

        self.console5.insert(tk.END,  f"Output saved to: {full_output_path}\n")
        self.root.update_idletasks()

    def browse_file(self, entry_widget):
        file_path = filedialog.askopenfilename(filetypes=[("AVI files", "*.avi")])
        entry_widget.delete(0, tk.END)  # clear current content
        entry_widget.insert(0, file_path)

    def apply_gaussian_filter_from_gui(self):
        self.console4.insert(tk.END, "Beginning Gaussian Filtering\n")
        self.root.update_idletasks()
        directory = self.folder_entry4.get()

        ksize_value = int(self.win_size4_entry4.get())

        if ksize_value % 2 == 0:
            ksize_value = ksize_value+1

        files = glob(f"{directory}/*.avi")

        for file in files:
            output_filename = os.path.splitext(file)[0] + "_GF.avi"

            self.apply_gaussian_filter(file, output_filename, ksize=(ksize_value, ksize_value))
        self.console4.insert(tk.END, "Gaussian Filtering Complete\n")
        self.root.update_idletasks()
    def apply_gaussian_filter(self, input_filename, output_filename, ksize=(5, 5), sigmaX=0):
        """
        Apply Gaussian filter to a video.

        :param input_filename: path to the input video
        :param output_filename: path to the output video
        :param ksize: Gaussian kernel size; must be odd and positive.
                      ksize.width and ksize.height can differ but they both must be positive and odd.
        :param sigmaX: Gaussian kernel standard deviation in X direction.
        """
        if not os.path.exists(input_filename):
            self.console4.insert(tk.END, f"Error: {input_filename} does not exist!")
            self.root.update_idletasks()
            return

        # Capture the input video
        cap = cv2.VideoCapture(input_filename)

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        # Check if the video capture was successful
        if not cap.isOpened():
            self.console4.insert(tk.END, f"Error: Cannot open video {input_filename}")
            self.root.update_idletasks()
            return

        # Video writer
        out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height), True)  # Assuming the video is colored

        # Process the video
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply Gaussian filter
            blurred = cv2.GaussianBlur(frame, ksize, sigmaX)

            # Write to output
            out.write(blurred)

        # Release resources
        cap.release()
        out.release()

        self.console4.insert(tk.END,f"Video saved successfully to {output_filename}\n")
        self.root.update_idletasks()

    def execute_averaging(self):
        #output_filename = self.averaged_file_entry.get()
        #if hasattr(self, 'files_for_averaging') and self.files_for_averaging and output_filename:
        #    self.avg_files(self.files_for_averaging, output_filename)
        # Get the directory and frame number from the GUI inputs
        directory = self.folder_entry3.get()
        #frame_num = int(self.frame_number_entry.get())

        # Video processing and subtraction operation
        self.console3.insert(tk.END, "Finding all raw data files...\n")
        self.root.update_idletasks()

        # Use glob to get a list of all .h264 files in the directory
        files = glob(f"{directory}/*.avi")
        self.console3.insert(tk.END, "Starting to average avi data files\n")
        self.root.update_idletasks()

        # Read the first video to get dimensions
        vid = cv2.VideoCapture(files[0])
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = vid.get(cv2.CAP_PROP_FPS)
        size = (width, height)
        self.console3.insert(tk.END, "Video dimensions obtained\n")
        self.root.update_idletasks()


        # Determine if the videos are grayscale
        ret, frame = vid.read()
        vid.release()
        is_gray = True if len(frame.shape) == 2 else False

        # Calculate the maximum frame count
        self.console3.insert(tk.END, "Determining maximum frame count\n")
        self.root.update_idletasks()

        max_frame_count = 0
        for file in files:
            vid = cv2.VideoCapture(file)
            frame_count = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
            if frame_count > max_frame_count:
                max_frame_count = frame_count
            vid.release()
            self.root.update_idletasks()

        # Initialize a zero array for the accumulated frames
        if is_gray:
            accumulated = np.zeros((height, width, max_frame_count), np.float32)
        else:
            accumulated = np.zeros((height, width, 3, max_frame_count), np.float32)



        # Accumulate frames from all videos
        self.console3.insert(tk.END, "Accumulating frames from all videos\n")
        self.root.update_idletasks()
        self.console3.insert(tk.END, "This could take a long time...\n")
        self.root.update_idletasks()

        for file in files:
            vid = cv2.VideoCapture(file)
            frame_count = 0
            while frame_count < max_frame_count:
                ret, frame = vid.read()
                if not ret:
                    # If video ended, pad with a black frame
                    if is_gray:
                        frame = np.zeros((height, width), np.uint8)
                    else:
                        frame = np.zeros((height, width, 3), np.uint8)
                # Indexing by frame_count accumulates each frame at its proper position
                accumulated[..., frame_count] += frame
                frame_count += 1
            vid.release()

        # Calculate the average for each frame
        average_frames = (accumulated / len(files)).astype(np.uint8)


        output_filename=directory+"//"+self.outputfile_label3.get()

        # Write the averaged video
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_filename, fourcc, fps, size, isColor=not is_gray)

        if not out.isOpened():
            print("Error: VideoWriter couldn't be opened. Check file path and codec.")
            return

        for frame_count in range(max_frame_count):
            out.write(average_frames[..., frame_count])
        out.release()
        self.console3.insert(tk.END, f"Video saved successfully to {output_filename}\n")
        self.root.update_idletasks()

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
        input_files = glob(f"{directory}/*subtract*.avi")
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
root.iconbitmap("Centroid42.ico")
app = App(root)
root.mainloop()
