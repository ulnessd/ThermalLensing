import tkinter as tk
from tkinter import filedialog, Entry, Button, Text
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import os


class DataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Interpolation and Derivative Plot")

        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        self.open_button = tk.Button(frame, text="Open File", command=self.load_file)
        self.open_button.pack(side=tk.LEFT, padx=10)

        self.filename_entry = Entry(frame, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=10)

        self.start_time_entry = Entry(frame, width=10)
        self.start_time_entry.pack(side=tk.LEFT, padx=10)
        self.end_time_entry = Entry(frame, width=10)
        self.end_time_entry.pack(side=tk.LEFT, padx=10)

        calculate_baseline_button = Button(frame, text="Calculate Baseline", command=self.calculate_baseline)
        calculate_baseline_button.pack(side=tk.LEFT, padx=10)

        export_button = Button(frame, text="Export Peaks", command=self.export_peaks)
        export_button.pack(side=tk.LEFT, padx=10)

        quit_button = tk.Button(frame, text="Quit", command=self.root.quit)
        quit_button.pack(side=tk.LEFT)

        self.console = Text(self.root, height=4, width=50)
        self.console.pack(pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.rect = None  # Rectangle for selection
        self.start_x = None
        self.start_y = None
        self.original_data = None
        self.time_data = None
        self.file_directory = ""
        self.extrema_data = {}
        self.extrema_plots = []

        # Connect the canvas with the mouse click and release events
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            data = pd.read_csv(file_path)
            self.time_data = data['Time']
            self.original_data = {}  # This will now store derivatives

            self.ax.clear()
            for column in data.columns[1:]:  # Skip the time column
                spline = UnivariateSpline(self.time_data, data[column], s=0)
                derivative = spline.derivative()
                self.original_data[column] = derivative(self.time_data)  # Store derivative
                self.ax.plot(self.time_data, self.original_data[column], label=f'Derivative of {column}')

            self.ax.set_title('Derivative Plots')
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Derivative')
            self.canvas.draw()

            # Filename and directory handling
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            new_filename = f"{base_name}_extrema.csv"
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, new_filename)
            self.file_directory = os.path.dirname(file_path)

            # Set default values for start and end time entries
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(0, '0.5')
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(0, f'{self.time_data.iloc[-1]}')

    def calculate_baseline(self):
        try:
            start_time = float(self.start_time_entry.get())
            end_time = float(self.end_time_entry.get())
            mask = (self.time_data >= start_time) & (self.time_data <= end_time)

            # Initialize variable to accumulate mean values and count them
            total_mean = 0
            count = 0

            # Iterate through each derivative dataset
            for key, derivative_data in self.original_data.items():
                # Apply mask and calculate mean for the current derivative dataset
                data_within = derivative_data[mask]
                if data_within.size > 0:  # Ensure there is data within the selected range
                    total_mean += np.mean(data_within)
                    count += 1

            if count > 0:
                overall_mean = total_mean / count
                self.console.insert(tk.END, f"Baseline average from {start_time}s to {end_time}s: {overall_mean}\n")
            else:
                self.console.insert(tk.END, "No data within selected time range.\n")
        except ValueError as e:
            self.console.insert(tk.END, "Invalid input for times. Please enter valid numbers.\n")

    def on_press(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.start_x = event.xdata
            self.start_y = event.ydata
            self.rect = Rectangle((self.start_x, self.start_y), 0, 0, linewidth=1, edgecolor='r', facecolor='none')
            self.ax.add_patch(self.rect)
        else:
            self.start_x = None
            self.start_y = None
            self.rect = None

    def export_peaks(self):
        filename = self.filename_entry.get()
        full_path = os.path.join(self.file_directory, filename)  # Combine directory path with filename
        with open(full_path, 'w') as f:
            for key, peaks in self.extrema_data.items():
                line = f"{key}"
                for time, value in peaks:
                    line += f", {time}, {value}"
                f.write(line + "\n")

    def on_release(self, event):
        if event.xdata is not None and event.ydata is not None and self.rect is not None:
            end_x = event.xdata
            end_y = event.ydata
            self.rect.set_width(end_x - self.start_x)
            self.rect.set_height(end_y - self.start_y)
            self.canvas.draw()

            time_array = np.array(self.time_data)
            indices = (time_array >= min(self.start_x, end_x)) & (time_array <= max(self.start_x, end_x))

            for plot_obj in self.extrema_plots:
                plot_obj.remove()
            self.extrema_plots.clear()

            self.extrema_data.clear()  # Clear existing extrema data

            for key, derivative_data in self.original_data.items():
                data_within = derivative_data[indices]

                if len(data_within) > 0:
                    local_max_indices = argrelextrema(data_within, np.greater)[0]
                    local_min_indices = argrelextrema(data_within, np.less)[0]

                    global_max_indices = np.where(indices)[0][local_max_indices]
                    global_min_indices = np.where(indices)[0][local_min_indices]

                    # Plot maxima and minima
                    max_plots = self.ax.plot(time_array[global_max_indices], data_within[local_max_indices], 'go')
                    min_plots = self.ax.plot(time_array[global_min_indices], data_within[local_min_indices], 'ro')

                    self.extrema_plots.extend(max_plots + min_plots)

                    # Store the extrema data for export
                    self.extrema_data[key] = [(time_array[idx], derivative_data[idx]) for idx in global_max_indices]
                    self.extrema_data[key].extend(
                        [(time_array[idx], derivative_data[idx]) for idx in global_min_indices])

            self.canvas.draw()


# Create the main window and pass it to the DataApp class
root = tk.Tk()
app = DataApp(root)
root.mainloop()
