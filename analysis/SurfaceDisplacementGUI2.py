import tkinter as tk
import os
from tkinter import filedialog, messagebox, Label, Entry, DoubleVar, Button, Menu
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CSVExplorerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Data Explorer")
        self.geometry("800x600")
        self.space_calibration = DoubleVar(value=0.006983)
        self.time_calibration = DoubleVar(value=0.010288)
        self.constant_offset = DoubleVar(value=0.0)
        self.start_time = DoubleVar(value=20.0)
        self.stop_time = DoubleVar(value=120.0)
        self.average_value = DoubleVar(value=0.0)
        self.filename_entry = tk.StringVar(value="filename")
        self.current_csv_path = None  # Initialize to None
        self.create_widgets()
        self.data = None


    def create_widgets(self):
        menu = Menu(self)
        self.config(menu=menu)
        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV", command=self.open_csv)

        # Layout adjustments using grid
        Label(self, text="Space Calibration (mm/pixel):").grid(row=0, column=0, sticky='e')
        Entry(self, textvariable=self.space_calibration).grid(row=0, column=1, sticky='w')
        Label(self, text="Time Calibration (s/frame):").grid(row=1, column=0, sticky='e')
        Entry(self, textvariable=self.time_calibration).grid(row=1, column=1, sticky='w')
        Label(self, text="Constant Offset (mm):").grid(row=2, column=0, sticky='e')
        Entry(self, textvariable=self.constant_offset).grid(row=2, column=1, sticky='w')

        Label(self, text="Start Time (s):").grid(row=3, column=0, sticky='e')
        Entry(self, textvariable=self.start_time).grid(row=3, column=1, sticky='w')
        Label(self, text="Stop Time (s):").grid(row=4, column=0, sticky='e')
        Entry(self, textvariable=self.stop_time).grid(row=4, column=1, sticky='w')

        Button(self, text="Analyze Selected Range", command=self.process_selected_range).grid(row=5, column=0)
        Button(self, text="Refresh Data", command=self.plot_data).grid(row=5, column=1)

        # Button and Entry for average calculation
        Button(self, text="Calculate Average", command=self.calculate_average).grid(row=1, column=2)
        Label(self, text="Average Value:").grid(row=2, column=2, sticky='e')
        Entry(self, textvariable=self.average_value).grid(row=2, column=3, sticky='w')

        Label(self, text="Filename:").grid(row=6, column=0, sticky='e')
        Entry(self, textvariable=self.filename_entry).grid(row=6, column=1, sticky='w')
        Button(self, text="Export Data", command=self.export_data).grid(row=6, column=2)


        # Plotting canvas
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=9, column=0, columnspan=4, sticky='nsew')
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def open_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path)
            self.current_csv_path = file_path  # Set the current CSV path
            self.plot_data()

    def plot_data(self):
        if self.data is not None:
            self.ax.clear()
            adjusted_data = self.data.copy()
            adjusted_data.iloc[:, 0] *= self.time_calibration.get()
            adjusted_data.iloc[:, 1] = self.constant_offset.get() - (adjusted_data.iloc[:, 1] * self.space_calibration.get())
            self.ax.plot(adjusted_data.iloc[:, 0], adjusted_data.iloc[:, 1], label='Calibrated Data')
            self.ax.set_title('CSV Data (Calibrated)')
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Position (mm)')
            self.ax.legend()
            self.canvas.draw()

    def process_selected_range(self):
        self.calculate_selected_data()

    def calculate_average(self):
        selected_data = self.calculate_selected_data(plot=False)
        if selected_data is not None:
            average = selected_data.iloc[:, 1].mean()
            self.average_value.set(average)

    def calculate_selected_data(self, plot=True):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded")
            return None

        # Apply calibrations
        adjusted_data = self.data.copy()
        adjusted_data.iloc[:, 0] *= self.time_calibration.get()
        adjusted_data.iloc[:, 1] = self.constant_offset.get() - (adjusted_data.iloc[:, 1] * self.space_calibration.get())

        # Filter data by time range
        mask = (adjusted_data.iloc[:, 0] >= self.start_time.get()) & (adjusted_data.iloc[:, 0] <= self.stop_time.get())
        selected_data = adjusted_data.loc[mask]

        if selected_data.empty:
            messagebox.showerror("Error", "No data found in the specified range")
            return None

        # Plotting selected region and Fourier Transform
        fig, (ax1, ax2) = plt.subplots(2, 1)
        ax1.plot(selected_data.iloc[:, 0], selected_data.iloc[:, 1], color='r', label='Selected Calibrated Data')
        ax1.set_title('Selected Data (Calibrated)')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Position (mm)')
        ax1.legend()

        # Fourier Transform
        fft_result = np.fft.fft(selected_data.iloc[:, 1])
        fft_magnitude = np.abs(fft_result)
        frequencies = np.fft.fftfreq(len(selected_data), d=self.time_calibration.get())
        ax2.plot(frequencies[:len(frequencies) // 2], fft_magnitude[:len(frequencies) // 2],
                 label='Fourier Transform')
        ax2.set_title('Fourier Transform of Selected Data')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.legend()

        plt.tight_layout()
        plt.show()

        return selected_data

    def export_data(self):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded")
            return

        if not self.current_csv_path:
            messagebox.showerror("Error", "No CSV file has been loaded.")
            return

        selected_data = self.calculate_selected_data(plot=False)
        if selected_data is not None:
            filename = self.filename_entry.get()
            if not filename:
                messagebox.showerror("Error", "Please enter a filename")
                return

            directory = os.path.dirname(self.current_csv_path)
            kin_path = os.path.join(directory, f"{filename}.kin.csv")
            selected_data.to_csv(kin_path, index=False)
            messagebox.showinfo("Export Successful", f"Kinematic data saved as {kin_path}")

            fft_result = np.fft.fft(selected_data.iloc[:, 1])
            fft_magnitude = np.abs(fft_result)
            frequencies = np.fft.fftfreq(len(selected_data), d=self.time_calibration.get())
            fft_data = pd.DataFrame(
                {'Frequency': frequencies[:len(frequencies) // 2], 'Magnitude': fft_magnitude[:len(frequencies) // 2]})
            fft_path = os.path.join(directory, f"{filename}.fft.csv")
            fft_data.to_csv(fft_path, index=False)
            messagebox.showinfo("Export Successful", f"Fourier Transform data saved as {fft_path}")


if __name__ == "__main__":
    app = CSVExplorerGUI()
    app.mainloop()
