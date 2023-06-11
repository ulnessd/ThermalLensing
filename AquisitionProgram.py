import tkinter as tk
from tkinter import filedialog
import cv2
from pylablib.devices import uc480
import serial
import serial.tools.list_ports
import time
import csv

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thermal Lensing Experiment")

        # get available COM ports
        com_ports = self.get_com_ports()


        # Use a single frame to contain three frames
        parameters_frame = tk.Frame(self)
        parameters_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Experiment Setup Frame
        setup_frame = tk.LabelFrame(parameters_frame, text="Experiment Setup")
        setup_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')  # Use grid instead of pack here


        # Camera Parameters Frame
        camera_frame = tk.LabelFrame(parameters_frame, text="Camera Parameters")
        camera_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')  # Use grid instead of pack here

        # COM Port Selection
        self.com_port = tk.StringVar(self)
        self.com_port.set('COM3')  # default value

        # COM Port Frame
        com_port_frame = tk.LabelFrame(parameters_frame, text="Select COM port")
        com_port_frame.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')
        tk.Label(com_port_frame, text='COM Port:').grid(row=0, column=0, sticky='e')
        com_port_menu = tk.OptionMenu(com_port_frame, self.com_port, *com_ports)
        com_port_menu.grid(row=2, column=3, sticky='w')


        # Experiment Setup Frame
        #setup_frame = tk.LabelFrame(root, text="Experiment Setup")
        #setup_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Number of Runs
        self.num_runs_var = tk.StringVar(value='1')
        tk.Label(setup_frame, text="Number of Runs").grid(row=0, column=0)
        tk.Entry(setup_frame, textvariable=self.num_runs_var).grid(row=0, column=1)

        # Background Collection Time
        self.bg_time_var = tk.StringVar(value='2')
        tk.Label(setup_frame, text="Background Collection Time").grid(row=1, column=0)
        tk.Entry(setup_frame, textvariable=self.bg_time_var).grid(row=1, column=1)

        # Laser On Time
        self.laser_time_var = tk.StringVar(value='4')
        tk.Label(setup_frame, text="Laser On Time").grid(row=2, column=0)
        tk.Entry(setup_frame, textvariable=self.laser_time_var).grid(row=2, column=1)

        # System Recovery Time
        self.recovery_time_var = tk.StringVar(value='2')
        tk.Label(setup_frame, text="System Recovery Time").grid(row=3, column=0)
        tk.Entry(setup_frame, textvariable=self.recovery_time_var).grid(row=3, column=1)

        # Camera Parameters Frame
        #camera_frame = tk.LabelFrame(root, text="Camera Parameters")
        #camera_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # FPS
        self.fps_var = tk.StringVar(value='10.0')
        tk.Label(camera_frame, text="FPS").grid(row=0, column=0)
        tk.Entry(camera_frame, textvariable=self.fps_var).grid(row=0, column=1)

        # Exposure Time
        self.exposure_time_var = tk.StringVar(value='100')
        tk.Label(camera_frame, text="Exposure Time").grid(row=1, column=0)
        tk.Entry(camera_frame, textvariable=self.exposure_time_var).grid(row=1, column=1)

        # Experiment Information Frame
        info_frame = tk.LabelFrame(self, text="Experiment Information")
        info_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Information Text Box
        self.info_text = tk.Text(info_frame, height=5)
        self.info_text.pack(fill="both", expand="yes")
        default_text = "Sample: \nInvestigator: \nComments: "
        self.info_text.insert('1.0', default_text)

        # File Name Entry
        self.file_name_var = tk.StringVar(value='')
        tk.Label(self, text="File Name").pack(padx=10, pady=5)
        tk.Entry(self, textvariable=self.file_name_var).pack(fill="x", padx=10, pady=5)

        # Console Output Frame
        console_frame = tk.LabelFrame(self, text="Console Output")
        console_frame.pack(fill="both", expand="yes", padx=10, pady=10)

        # Console Text Box
        self.console_text = tk.Text(console_frame, height=10)
        self.console_text.pack(fill="both", expand="yes")

        self.console_text.tag_config("red", foreground="red")
        self.console_text.tag_config("green", foreground="green")
        self.console_text.tag_config("blue", foreground="blue")

        # Control Buttons
        self.toggle_shutter_button = tk.Button(self, text="Toggle Shutter", command=self.toggle_shutter)
        self.toggle_shutter_button.pack(fill="x", padx=10, pady=5)

        self.live_camera_button = tk.Button(self, text="Live Camera", command=self.live_camera)
        self.live_camera_button.pack(fill="x", padx=10, pady=5)

        self.run_experiment_button=tk.Button(self, text="Run Experiment",command=self.run_experiment)
        self.run_experiment_button.pack(fill="x", padx=10, pady=5)

        tk.Button(self, text="Open Video Viewer", command=self.video_viewer).pack(fill="x", padx=10, pady=5)
        tk.Button(self, text="Quit", command=self.quit).pack(fill="x", padx=10, pady=5)

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.avi")])
        if file_path:
            self.console_text.insert(tk.END, "Opening file: " + file_path + "\n")
            # Open the video file here
            self.cap = cv2.VideoCapture(file_path)


    def toggle_shutter(self):

        ser = serial.Serial(port=self.com_port.get(), baudrate=10000, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        ser.write(b'\xFF')
        self.console_text.insert(tk.END, "Shutter toggled\n")
        self.update()

    def live_camera(self):


        # List all cameras for the uc480 backend
        camera_list = uc480.list_cameras(backend="uc480")

        # Insert camera list into console text box
        self.console_text.insert(tk.END, str(camera_list) + "\n")
        self.console_text.see(tk.END)
        self.update()

        # Connect to the first available camera
        cam = uc480.UC480Camera(backend="uc480")

        # Set up the camera (configure exposure time, gain, etc.)
        exposure_time = int(self.exposure_time_var.get())  # Get the entered exposure time
        cam.set_exposure(exposure_time)  # Set exposure time in microseconds
        cam.set_gains(1.0)  # Set gain

        # Start the acquisition
        cam.start_acquisition()

        # Create a named window to display the images
        window_name = 'Thorlabs Camera'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # Continuously capture and display images until the 'ESC' key is pressed
        while True:
            image_data = cam.snap()

            # Convert the grayscale image to BGR
            image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)

            # Add the text to the image
            cv2.putText(image_data, 'Hit ESC to exit', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.imshow(window_name, image_data)

            # Break the loop if the 'ESC' key is pressed
            if cv2.waitKey(1) == 27:
                break

        # Release resources and close the window
        cam.stop_acquisition()
        cam.close()
        cv2.destroyAllWindows()

    def update_console(self, text):
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)  # Scroll the Text widget to the bottom


    def run_experiment(self):
        num_runs = int(self.num_runs_var.get())
        experiment_info = self.info_text.get('1.0', tk.END)

        # File to store the user's input and parameters
        with open(self.file_name_var.get() + '_info.txt', 'w') as f:
            f.write('Experiment Information:\n' + experiment_info)
            f.write('\nExperiment Parameters:\n')
            f.write('Number of Runs: ' + self.num_runs_var.get() + '\n')
            f.write('Background Collection Time: ' + self.bg_time_var.get() + '\n')
            f.write('Laser On Time: ' + self.laser_time_var.get() + '\n')
            f.write('System Recovery Time: ' + self.recovery_time_var.get() + '\n')
            f.write('FPS: ' + self.fps_var.get() + '\n')
            f.write('Exposure Time: ' + self.exposure_time_var.get() + '\n')

        for run in range(num_runs):
            # Open the camera
            cam = uc480.UC480Camera(backend="uc480")
            exposure_time = int(self.exposure_time_var.get())  # Get the entered exposure time
            cam.set_exposure(exposure_time)  # Set exposure time in microseconds
            cam.set_gains(1.0)  # Set gain

            # Start the acquisition
            cam.start_acquisition()

            # Define the codec and create a VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(self.file_name_var.get() + str(run) + '.avi', fourcc, float(self.fps_var.get()),
                                  (1280, 1024), isColor=False)

            self.console_text.insert(tk.END, f"Beginning run {run + 1}\n","green")
            #self.update_console(f"Beginning run {run + 1}\n")
            self.update()

            start_time = time.time()  # To get the start time
            timestamps = []
            toggle_count = 0

            while True:
                image_data = cam.snap()
                out.write(image_data)

                current_time = time.time()
                timestamps.append(current_time - start_time)

                if current_time - start_time > int(self.bg_time_var.get()) and toggle_count == 0:
                    toggle_count += 1
                    self.toggle_shutter()
                    self.console_text.insert(tk.END, "Laser on sample now\n")
                    self.console_text.see(tk.END)
                    self.update()

                if current_time - start_time > int(self.laser_time_var.get())+int(self.bg_time_var.get()) and toggle_count == 1:
                    toggle_count += 1
                    self.toggle_shutter()
                    #self.console_text.insert(tk.END, f"Video capture complete for run {run + 1}\n")
                    #self.console_text.see(tk.END)
                    #self.update()
                    self.console_text.insert(tk.END, "Resting phase\n")
                    self.console_text.see(tk.END)
                    self.update()

                if current_time - start_time > int(self.recovery_time_var.get())+ int(self.laser_time_var.get())+int(self.bg_time_var.get()) and toggle_count == 2:

                    self.console_text.insert(tk.END, f"Run {run + 1} is complete.\n","red")
                    self.console_text.see(tk.END)
                    self.update()
                    end_time = time.time()

                    break  # End the current run

            # Close resources after the run
            cam.stop_acquisition()
            cam.close()

            self.console_text.insert(tk.END, f"Writing video file for run {run + 1}\n")
            self.console_text.see(tk.END)
            self.update()
            out.release()

            # Write timestamps to a CSV file
            self.console_text.insert(tk.END, f"Writing time file for run {run + 1}\n")
            self.console_text.see(tk.END)
            self.update()
            with open(self.file_name_var.get() + '_timestamps_run' + str(run) + '.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['frame', 'timestamp'])
                for i, timestamp in enumerate(timestamps):
                    writer.writerow([i, timestamp])

            # Time for the camera to reset
            time.sleep(1.5)

        self.console_text.insert(tk.END,"Experiment finished.\n","blue")
        self.console_text.see(tk.END)
        self.update()

    def video_viewer(self):
        # Open a video file
        self.open_file()

        # If a file is not selected, don't proceed
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return

        # Get the total frames
        frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create a named window
        cv2.namedWindow('Video Viewer', cv2.WINDOW_NORMAL)

        # Create trackbar/slider
        cv2.createTrackbar('Frame', 'Video Viewer', 0, frames - 1, self.on_trackbar)

        # State variable for play/pause functionality
        play = True

        while True:
            if play:
                ret, frame = self.cap.read()

                if not ret:
                    break

                # Display the frame
                cv2.imshow('Video Viewer', frame)

                # Update the position of the trackbar
                position = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                cv2.setTrackbarPos('Frame', 'Video Viewer', position)

            # Check for user input
            key = cv2.waitKey(1)
            if key & 0xFF == 27:  # Exit if ESC key is pressed
                break
            elif key == ord('p'):  # Play/Pause toggle
                play = not play

        # Release everything and destroy window
        self.cap.release()
        cv2.destroyAllWindows()

    def on_trackbar(self, val):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, val)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()