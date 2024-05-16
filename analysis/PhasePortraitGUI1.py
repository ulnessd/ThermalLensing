port numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from tkinter import Tk, Button, Entry, Label, Checkbutton, IntVar, Canvas, filedialog, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class PhaseSpacePlotter:
    def __init__(self, master):
        self.master = master
        self.master.title("Phase Space Plotter")

        self.file_path = None

        self.file_label = Label(master, text="Select KIN.CSV File:")
        self.file_label.grid(row=0, column=0, padx=5, pady=5)

        self.file_button = Button(master, text="Open File", command=self.load_file)
        self.file_button.grid(row=0, column=1, padx=5, pady=5)

        self.start_time_label = Label(master, text="Start Time:")
        self.start_time_label.grid(row=1, column=0, padx=5, pady=5)
        self.start_time_entry = Entry(master)
        self.start_time_entry.grid(row=1, column=1, padx=5, pady=5)
        self.start_time_entry.insert(0, "20")  # Default value

        self.stop_time_label = Label(master, text="Stop Time:")
        self.stop_time_label.grid(row=2, column=0, padx=5, pady=5)
        self.stop_time_entry = Entry(master)
        self.stop_time_entry.grid(row=2, column=1, padx=5, pady=5)
        self.stop_time_entry.insert(0, "120")  # Default value

        self.ymin_label = Label(master, text="Y Min:")
        self.ymin_label.grid(row=3, column=0, padx=5, pady=5)
        self.ymin_entry = Entry(master)
        self.ymin_entry.grid(row=3, column=1, padx=5, pady=5)
        self.ymin_entry.insert(0, "-1.2")  # Default value

        self.ymax_label = Label(master, text="Y Max:")
        self.ymax_label.grid(row=4, column=0, padx=5, pady=5)
        self.ymax_entry = Entry(master)
        self.ymax_entry.grid(row=4, column=1, padx=5, pady=5)
        self.ymax_entry.insert(0, "1.2")  # Default value

        self.xmin_label = Label(master, text="X Min:")
        self.xmin_label.grid(row=5, column=0, padx=5, pady=5)
        self.xmin_entry = Entry(master)
        self.xmin_entry.grid(row=5, column=1, padx=5, pady=5)
        self.xmin_entry.insert(0, "-0.4")  # Default value

        self.xmax_label = Label(master, text="X Max:")
        self.xmax_label.grid(row=6, column=0, padx=5, pady=5)
        self.xmax_entry = Entry(master)
        self.xmax_entry.grid(row=6, column=1, padx=5, pady=5)
        self.xmax_entry.insert(0, "0.4")  # Default value

        self.size_label = Label(master, text="Point Size:")
        self.size_label.grid(row=7, column=0, padx=5, pady=5)
        self.size_entry = Entry(master)
        self.size_entry.grid(row=7, column=1, padx=5, pady=5)
        self.size_entry.insert(0, "1")  # Default value

        self.rainbow_var = IntVar()
        self.rainbow_check = Checkbutton(master, text="Rainbow Mode", variable=self.rainbow_var)
        self.rainbow_check.grid(row=8, columnspan=2, padx=5, pady=5)

        self.basefile_label = Label(master, text="Base Filename:")
        self.basefile_label.grid(row=9, column=0, padx=5, pady=5)
        self.basefile_entry = Entry(master)
        self.basefile_entry.grid(row=9, column=1, padx=5, pady=5)
        self.basefile_entry.insert(0, "filename")  # Default value

        self.plot_button = Button(master, text="Plot", command=self.plot)
        self.plot_button.grid(row=10, column=0, padx=5, pady=5)

        self.save_button = Button(master, text="Save", command=self.save)
        self.save_button.grid(row=10, column=1, padx=5, pady=5)

        self.canvas = Canvas(master, width=800, height=600)
        self.canvas.grid(row=11, columnspan=2, padx=5, pady=5)

        self.figure = None

    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        self.data = pd.read_csv(self.file_path)
        self.data.rename(columns={'Frame Number': 'Time (s)', 'Pixel Index': 'Distance (mm)'}, inplace=True)

    def plot(self):
        start_time = float(self.start_time_entry.get())
        stop_time = float(self.stop_time_entry.get())
        ymin = float(self.ymin_entry.get())
        ymax = float(self.ymax_entry.get())
        xmin = float(self.xmin_entry.get())
        xmax = float(self.xmax_entry.get())
        point_size = int(self.size_entry.get())
        rainbow_mode = self.rainbow_var.get()

        spline = UnivariateSpline(self.data['Time (s)'], self.data['Distance (mm)'], s=0.5)
        sampling_rate = 100  # 100 Hz
        time_resampled = np.arange(start_time, stop_time, 1/sampling_rate)
        distance_resampled = spline(time_resampled)
        distance_derivative_resampled = spline.derivative()(time_resampled)

        self.figure = plt.figure(figsize=(8, 6))
        ax = self.figure.add_subplot(111)

        if rainbow_mode:
            sc = ax.scatter(distance_resampled, distance_derivative_resampled, c=(time_resampled - time_resampled.min()), cmap='rainbow', s=point_size)
            self.figure.colorbar(sc, label='Time (s)')
        else:
            ax.scatter(distance_resampled, distance_derivative_resampled, c='black', s=point_size)

        ax.set_xlabel('Distance (mm)')
        ax.set_ylabel('Derivative of Distance (mm/s)')
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_title(f'Phase Portrait')
        ax.grid(True)

        self.update_canvas()

    def update_canvas(self):
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.get_tk_widget().pack_forget()

        self.canvas_widget = FigureCanvasTkAgg(self.figure, self.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack()

    def save(self):
        base_filename = self.basefile_entry.get()
        save_path = os.path.join(os.path.dirname(self.file_path), f"{base_filename}.png")
        self.figure.savefig(save_path, dpi=600)

if __name__ == "__main__":
    root = Tk()
    app = PhaseSpacePlotter(root)
    root.mainloop()
