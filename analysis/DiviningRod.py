import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import glob
import os
import cv2
import numpy as np
import csv

class DiviningRod:

    def __init__(self, master):
        self.master = master
        master.title("Divining Rod")

        # Configure rows and columns
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)
        master.grid_rowconfigure(3, weight=0)
        master.grid_rowconfigure(4, weight=0)
        master.grid_rowconfigure(5, weight=0)
        master.grid_rowconfigure(6, weight=1)
        master.grid_rowconfigure(7, weight=1)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)

        # Load and display image
        img_path = "Divining.jpg"  # Replace with your image path
        self.image = Image.open(img_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.img_label = tk.Label(master, image=self.photo)
        self.img_label.grid(row=0, column=0, columnspan=3, pady=10,padx=10)

        # Folder selection
        self.folder_label = tk.Label(master, text="Folder:")
        self.folder_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
        self.folder_entry = tk.Entry(master, width=30)
        self.folder_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5)
        self.browse_button = tk.Button(master, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=3, padx=10, pady=5)

        # Starting Column and End Column
        self.start_col_label = tk.Label(master, text="Start Col:")
        self.start_col_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
        self.start_col_entry = tk.Entry(master, width=10)
        self.start_col_entry.insert(0, "0")
        self.start_col_entry.grid(row=2, column=1, padx=10, pady=5)

        self.end_col_label = tk.Label(master, text="End Col:")
        self.end_col_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
        self.end_col_entry = tk.Entry(master, width=10)
        self.end_col_entry.insert(0, "719")
        self.end_col_entry.grid(row=3, column=1, padx=10, pady=5)

        # Starting Pixel, Backlash, and Threshold
        self.start_pixel_label = tk.Label(master, text="Start Pix:")
        self.start_pixel_label.grid(row=2, column=2, padx=10, pady=5, sticky=tk.E)
        self.start_pixel_entry = tk.Entry(master, width=10)
        self.start_pixel_entry.insert(0, "0")
        self.start_pixel_entry.grid(row=2, column=3, padx=10, pady=5)

        self.backlash_label = tk.Label(master, text="Backlash:")
        self.backlash_label.grid(row=3, column=2, padx=10, pady=5, sticky=tk.E)
        self.backlash_entry = tk.Entry(master, width=10)
        self.backlash_entry.insert(0, "30")
        self.backlash_entry.grid(row=3, column=3, padx=10, pady=5)

        self.threshold_label = tk.Label(master, text="Threshold:")
        self.threshold_label.grid(row=4, column=2, padx=10, pady=5, sticky=tk.E)
        self.threshold_entry = tk.Entry(master, width=10)
        self.threshold_entry.insert(0, "16")
        self.threshold_entry.grid(row=4, column=3, padx=10, pady=5)

        # Analyze button
        self.analyze_button = tk.Button(master, text="Calculate Wavefront", command=self.analyze)
        self.analyze_button.grid(row=5, column=1, pady=10)

        # Console output
        self.console = tk.Text(master, wrap=tk.WORD, width=50, height=10)
        self.console.grid(row=6, column=0, columnspan=4, padx=10, pady=5)

        # Quit button
        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.grid(row=7, column=1, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)

    def analyze(self):
        folder_path = self.folder_entry.get()
        starting_pixel = int(self.start_pixel_entry.get())
        backlash = int(self.backlash_entry.get())
        threshold = int(self.threshold_entry.get())
        start_col = int(self.start_col_entry.get())
        end_col = int(self.end_col_entry.get())

        # Getting all relevant files from the directory
        input_files = glob.glob(f"{folder_path}/*_subtract*.avi")

        for input_file in input_files:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            wavefront_file = f"{folder_path}/{base_name}_wavefront.csv"

            cap = cv2.VideoCapture(input_file)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(f'{folder_path}/{base_name}_wavefront.avi', fourcc, fps, (frame_width, frame_height))

            previous_y_positions = [starting_pixel] * (end_col - start_col + 1)

            with open(wavefront_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["frame", "pixel"])

                frame_number = 0

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    x_positions = []
                    y_positions = []

                    for col in range(start_col, end_col + 1):
                        adjusted_col = col - start_col  # Adjust the index for previous_y_positions
                        found_pixel = False
                        start_row = max(0, previous_y_positions[adjusted_col] - backlash)

                        for row in range(start_row, frame_height):
                            if gray_frame[row, col] > threshold:
                                x_positions.append(col)
                                y_positions.append(row)
                                found_pixel = True
                                break

                        # If no pixel was found for this column, use the last known y-position for this column
                        if not found_pixel:
                            x_positions.append(col)
                            y_positions.append(previous_y_positions[adjusted_col])

                    # Update previous_y_positions for the next frame
                    if y_positions:
                        previous_y_positions = y_positions

                    if x_positions and y_positions:
                        avg_y_position = np.mean(y_positions)
                        avg_y_position_top = 720 - avg_y_position
                        writer.writerow([frame_number, avg_y_position_top])

                        coeffs = np.polyfit(x_positions, y_positions, 2)
                        poly = np.poly1d(coeffs)
                        x_range = np.arange(start_col, end_col + 1)
                        y_poly = poly(x_range)

                        for x, y in zip(x_range, y_poly):
                            if 0 <= int(y) < frame_height:
                                frame[int(y), int(x)] = [0, 255, 255]  # Yellow line

                    out.write(frame)
                    frame_number += 1

                cap.release()
                out.release()

        self.console.insert(tk.END, f"Wavefront analysis completed for all files in {folder_path}.\n")

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DiviningRod(root)
    root.iconbitmap("Divining.ico")
    app.run()
