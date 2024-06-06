import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2


class VideoFrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Frame Selector")

        # Main layout
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.LEFT)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT)

        # Frame display setup
        self.canvas = tk.Canvas(self.main_frame, width=640, height=480)
        self.canvas.pack()

        # File open button
        self.open_button = tk.Button(self.control_frame, text="Open Video", command=self.load_video)
        self.open_button.pack()

        # Frame number entry
        self.frame_label = tk.Label(self.control_frame, text="Enter Frame Number:")
        self.frame_label.pack()
        self.frame_entry = tk.Entry(self.control_frame)
        self.frame_entry.pack()

        # Button to load frame
        self.load_frame_button = tk.Button(self.control_frame, text="Load Frame", command=self.display_frame)
        self.load_frame_button.pack()

        # Console for displaying coordinates
        self.console = tk.Listbox(self.control_frame, height=4)
        self.console.pack()

        # Quit button
        self.quit_button = tk.Button(self.control_frame, text="Quit", command=root.quit)
        self.quit_button.pack()

        # Bind mouse click to canvas
        self.canvas.bind("<Button-1>", self.get_coords)

        # Video capture object and file path
        self.cap = None
        self.cap_file_path = None

    def load_video(self):
        self.cap_file_path = filedialog.askopenfilename(filetypes=[("H264 files", "*.h264"), ("All files", "*.*")])
        if self.cap_file_path:
            self.cap = cv2.VideoCapture(self.cap_file_path)

    def display_frame(self):
        frame_number = int(self.frame_entry.get())
        if self.cap_file_path:  # Make sure there's a file path
            self.cap.release()  # Release the current capture object
            self.cap = cv2.VideoCapture(self.cap_file_path)  # Reopen the video file to reset

            current_frame = 0
            while current_frame <= frame_number:
                ret, frame = self.cap.read()
                if not ret:
                    break  # Break if no frame is returned
                if current_frame == frame_number:
                    self.show_frame(frame)
                    break
                current_frame += 1

    def show_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

    def get_coords(self, event):
        self.console.insert(tk.END, f"X: {event.x}, Y: {event.y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoFrameExtractor(root)
    root.mainloop()
