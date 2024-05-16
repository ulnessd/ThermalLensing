import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scale, Canvas, Checkbutton, IntVar, Entry
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np

class FrameRipperGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Frame Ripper H264")
        self.geometry("600x675")
        self.file_directory = ''
        self.normalize_var = IntVar()  # Variable to store the state of the checkbox
        self.cap = None
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="Open .h264 File", command=self.open_file).pack(pady=10)
        self.slider = Scale(self, from_=0, to=100, orient=tk.HORIZONTAL, command=self.update_frame)
        self.slider.pack(pady=10, fill=tk.X)
        self.canvas = Canvas(self, width=400, height=300)
        self.canvas.pack()
        self.filename_entry = Entry(self)
        self.filename_entry.pack(pady=10)
        self.filename_entry.insert(0, "Filename")
        Checkbutton(self, text="Normalize Frame", variable=self.normalize_var).pack(pady=10)
        #tk.Button(self, text="Save Frame as PNG", command=self.save_frame).pack(pady=10)
        tk.Button(self, text="Save Frame as PNG", command=self.save_frame).pack(pady=10)
        tk.Button(self, text="Quit", command=self.quit).pack(pady=10)
        self.console = Text(self, height=4, state='disabled')
        self.console.pack(fill=tk.X)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("H264 files", "*.h264")])
        if file_path:
            converted_path = self.convert_to_avi(file_path)
            self.file_directory = os.path.dirname(converted_path)
            self.cap = cv2.VideoCapture(converted_path)
            if self.cap.isOpened():
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.slider.configure(to=self.total_frames - 2)
                self.update_console(f"Video successfully imported. Total frames: {self.total_frames}")
            else:
                messagebox.showerror("Error", "Failed to open the video file.")

    def convert_to_avi(self, input_path):
        output_path = os.path.splitext(input_path)[0] + ".avi"
        if not os.path.exists(output_path):  # Check if conversion is needed
            command = ['ffmpeg', '-f', 'h264', '-i', input_path, '-c:v', 'copy', '-fflags', '+genpts', output_path]
            subprocess.run(command, shell=True)
        return output_path

    def update_frame(self, event=None):
        frame_number = self.slider.get()
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if ret:
                frame_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_display, (400, 300))
                frame_photo = ImageTk.PhotoImage(image=Image.fromarray(frame_resized))
                self.canvas.create_image(0, 0, image=frame_photo, anchor=tk.NW)
                self.canvas.image = frame_photo
            else:
                self.update_console("Failed to retrieve the frame.")


    def save_frame(self):
        if self.cap is None or not self.cap.isOpened():
            messagebox.showerror("Error", "No video file is open")
            return

        try:
            frame_number = self.slider.get()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
        except ValueError:
            messagebox.showerror("Error", "Invalid frame number")
            return

        if not ret:
            messagebox.showerror("Error", "Could not read the frame")
            return

        # Process frame
        frame_grey = frame[:, :, 2]
        frame_grey = cv2.flip(frame_grey, 0)

        # Normalize frame if checkbox is checked
        if self.normalize_var.get() == 1:
            frame_grey = cv2.normalize(frame_grey, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Save frame as a PNG
        filename = self.filename_entry.get() + f"_{frame_number}.png"
        save_path = os.path.join(self.file_directory, filename)
        cv2.imwrite(save_path, frame_grey)
        messagebox.showinfo("Success", f"Frame saved as {save_path}")

    def save_png(self, scale_factor):
        frame_number = self.slider.get()
        if self.cap is None or not self.cap.isOpened():
            messagebox.showerror("Error", "No video file is open")
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Could not read the frame")
            return

        if self.normalize_var.get() == 1:
            frame = cv2.normalize(frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        frame_high_res = cv2.resize(frame, (frame.shape[1] * scale_factor, frame.shape[0] * scale_factor), interpolation=cv2.INTER_CUBIC)
        filename = self.filename_entry.get() + f"_{frame_number}_highres.png"
        save_path = os.path.join(self.file_directory, filename)
        cv2.imwrite(save_path, frame_high_res)
        messagebox.showinfo("Success", f"High-Resolution Frame saved as {save_path}")

    def update_console(self, message):
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, message)
        self.console.config(state='disabled')

if __name__ == "__main__":
    app = FrameRipperGUI()
    app.mainloop()
