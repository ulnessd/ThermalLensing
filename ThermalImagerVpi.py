import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import serial
import serial.tools.list_ports
import time
from time import sleep
import csv
from PIL import Image
from PIL import ImageTk
from picamera import PiCamera
from picamera.array import PiRGBArray



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
               # Create a label to display the video frames
        self.video_label = tk.Label(self)
        self.video_label.pack()
        
                # Create a variable to control the live view thread
        self.live_view_running = False
        
        self.new_window = None  

        #self.new_window_open = True
        #self.new_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        
    def create_widgets(self):
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
        self.com_port.set('Choose')  # default value

        # COM Port Frame
        com_port_frame = tk.LabelFrame(parameters_frame, text="Select COM port")
        com_port_frame.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')
        tk.Label(com_port_frame, text='COM Port:').grid(row=0, column=0, sticky='e')
        com_port_menu = tk.OptionMenu(com_port_frame, self.com_port, *com_ports)
        com_port_menu.grid(row=0, column=1, sticky='w')

        # Experiment Setup Frame
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
        
        # Sleep Time
        self.sleep_time_var = tk.StringVar(value='4')
        tk.Label(setup_frame, text="Sleep Time").grid(row=4, column=0)
        tk.Entry(setup_frame, textvariable=self.sleep_time_var).grid(row=4, column=1)



       
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
        self.toggle_shutter_button = tk.Button(self, text="Laser/Toggle Shutter", command=self.toggle_shutter)
        self.toggle_shutter_button.pack(fill="x", padx=10, pady=5)

        self.live_camera_button = tk.Button(self, text="Live Camera", command=self.live_camera)
        self.live_camera_button.pack(fill="x", padx=10, pady=5)




        self.run_experiment_button = tk.Button(self, text="Run Experiment", command=self.run_experiment)
        self.run_experiment_button.pack(fill="x", padx=10, pady=5)


        self.quit_button = tk.Button(self, text="QUIT", command=self.master.destroy)
        self.quit_button.pack(fill="x", padx=10, pady=5)

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    #def open_file(self):
    #    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.avi")])
    #    if file_path:
    #        self.console_text.insert(tk.END, "Opening file: " + file_path + "\n")
            # Open the video file here
    #        self.cap = cv2.VideoCapture(file_path)

    def valid_com_port(self):
        if self.com_port.get() == 'Choose':
            #self.update_console("Error: No COM port selected.","red")
            self.console_text.insert(tk.END,"Error: No COM port selected.\n","red")
            return False
        else:
            return True


    def toggle_shutter(self):
        if self.valid_com_port():
            ser = serial.Serial(port=self.com_port.get(), baudrate=10000, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
            ser.write(b'\xFF')
            self.update_console("Laser/Shutter toggled")
        
    
    def live_camera(self):
        if self.valid_com_port():
            self.live_view_running = not self.live_view_running  # toggle live view state
            if self.live_view_running:
                # Start live view
                self.camera = PiCamera()
                self.camera.resolution = (320, 240)
                self.camera.framerate = 60
                self.rawCapture = PiRGBArray(self.camera)  # Create an array for the captured frames
                # Create a new window
                self.new_window = tk.Toplevel(self.master)
                self.new_window.title("Live Camera Feed")
                self.new_window.geometry("320x240")  # Set the size of the window
                self.new_window.configure(bg='black')
                # Create a label for the video feed
                self.video_label = tk.Label(self.new_window)
                self.video_label.pack(padx=10, pady=10)
                self.new_window.protocol("WM_DELETE_WINDOW", self.close_live_view)  # Define what happens when the window is closed
                threading.Thread(target=self.update_frame).start()  # Start updating the frame in the new window in a new thread
            else:
                # Stop live view
                self.close_live_view()

    def close_live_view(self):
        # Function to close live view
        self.live_view_running = False
        self.camera.close()
        self.new_window.destroy()

    def on_closing(self):
        # Check if the live view is running
        if self.live_view_running:
            self.live_view_running = False
            self.camera.close()
            self.new_window.destroy()
        self.master.destroy()

    #def on_closing(self):
    #    self.new_window_open = False
    #    self.new_window.destroy()

    def update_frame(self):
        while self.live_view_running and self.new_window:
            # Capture frame
            self.camera.capture(self.rawCapture, format="bgr")
            frame = self.rawCapture.array
            # Convert the image from OpenCV BGR format to Tkinter PhotoImage format
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.rawCapture.truncate(0)  # clear the stream in preparation for the next frame
            sleep(0.01)  # Pause for a bit before capturing the next frame
            
    def run_experiment(self):
        if self.valid_com_port():
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
               

            for run in range(num_runs):
                # Open the camera
                camera = PiCamera()
                camera.resolution = (1240, 1080)
                #camera.framerate = 10

                self.console_text.insert(tk.END, f"Beginning run {run + 1}\n","green")
                self.update()

                # Begin recording
                camera.start_recording(self.file_name_var.get() + str(run) + '.h264')  # Using h264 codec

                start_time = time.time()  # To get the start time
                toggle_count = 0

                while True:
                    current_time = time.time()

                    if current_time - start_time > float(self.bg_time_var.get()) and toggle_count == 0:
                        toggle_count += 1
                        self.toggle_shutter()
                        self.console_text.insert(tk.END, "Laser on sample now\n")
                        self.console_text.see(tk.END)
                        self.update()

                    if current_time - start_time > float(self.laser_time_var.get())+float(self.bg_time_var.get()) and toggle_count == 1:
                        toggle_count += 1
                        self.toggle_shutter()
                        self.console_text.insert(tk.END, "Resting phase\n")
                        self.console_text.see(tk.END)
                        self.update()

                    if current_time - start_time > float(self.recovery_time_var.get())+ float(self.laser_time_var.get())+int(self.bg_time_var.get()) and toggle_count == 2:
                        self.console_text.insert(tk.END, f"Run {run + 1} is complete.\n","red")
                        self.console_text.see(tk.END)
                        self.update()
                        end_time = time.time()
                        break  # End the current run

                # Stop recording
                camera.stop_recording()

                # Close the camera
                camera.close()

                self.console_text.insert(tk.END, f"Writing video file for run {run + 1}\n")
                self.console_text.see(tk.END)
                self.update()

                # Time for the camera to reset
                sleep(float(self.sleep_time_var.get()))

            self.console_text.insert(tk.END,"Experiment finished.\n","blue")
            self.console_text.see(tk.END)
            self.update()


  #  def video_viewer(self):
        # This method should handle Open Video Viewer functionality
   #     pass
    
    def update_console(self, text):
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)  # Scroll the Text widget to the bottom

def main():
    root = tk.Tk()
    root.geometry('800x800')  # Set the size of your window here.
    root.title("Thermal Imaging Acquisition Program")  # Set the title of your window here.
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
