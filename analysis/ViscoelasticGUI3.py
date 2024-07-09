import tkinter as tk
from tkinter import filedialog, Entry, Button, Text, Label, Checkbutton, IntVar
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import os

class DataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Viscoelastic Analyzer")

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=20)

        file_frame = tk.Frame(top_frame)
        file_frame.pack(side=tk.TOP, pady=10)

        self.open_button = tk.Button(file_frame, text="Open File", command=self.load_file)
        self.open_button.pack(side=tk.LEFT, padx=10)

        self.filename_entry = Entry(file_frame, width=30)
        self.filename_entry.pack(side=tk.LEFT, padx=10)

        Label(file_frame, text="Enhanced Sampling:").pack(side=tk.LEFT, padx=5)
        self.enhanced_sampling_var = tk.StringVar()
        self.enhanced_sampling_var.set("50")  # Default value
        self.enhanced_sampling_var.trace("w", self.on_sampling_change)  # Add trace
        self.enhanced_sampling_entry = Entry(file_frame, width=10, textvariable=self.enhanced_sampling_var)
        self.enhanced_sampling_entry.pack(side=tk.LEFT, padx=5)

        self.avg_derivative_var = IntVar()
        self.avg_derivative_checkbox = Checkbutton(file_frame, text="Average Derivative", variable=self.avg_derivative_var, command=self.toggle_average_derivative)
        self.avg_derivative_checkbox.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a frame to hold the time entries and pack them above the buttons
        time_frame = tk.Frame(button_frame)
        time_frame.pack(side=tk.TOP, pady=5)

        self.start_time_entry = Entry(time_frame, width=10)
        self.start_time_entry.pack(side=tk.LEFT, padx=5)
        self.end_time_entry = Entry(time_frame, width=10)
        self.end_time_entry.pack(side=tk.LEFT, padx=5)

        calculate_baseline_button = Button(button_frame, text="Calculate Baseline", command=self.calculate_baseline)
        calculate_baseline_button.pack(pady=5)

        calculate_chirp_button = Button(button_frame, text="Calculate Chirp", command=self.calculate_chirp_button)
        calculate_chirp_button.pack(pady=5)

        # Create a frame for fitting parameters
        fit_params_frame = tk.Frame(button_frame)
        fit_params_frame.pack(side=tk.TOP, pady=5)

        Label(fit_params_frame, text="A:").pack(side=tk.LEFT)
        self.A_entry = Entry(fit_params_frame, width=5)
        self.A_entry.insert(0, "5")
        self.A_entry.pack(side=tk.LEFT, padx=5)

        Label(fit_params_frame, text="k:").pack(side=tk.LEFT)
        self.k_entry = Entry(fit_params_frame, width=5)
        self.k_entry.insert(0, "5")
        self.k_entry.pack(side=tk.LEFT, padx=5)

        Label(fit_params_frame, text="t0:").pack(side=tk.LEFT)
        self.t0_entry = Entry(fit_params_frame, width=5)
        self.t0_entry.insert(0, "0")
        self.t0_entry.pack(side=tk.LEFT, padx=5)

        Label(fit_params_frame, text="c:").pack(side=tk.LEFT)
        self.c_entry = Entry(fit_params_frame, width=5)
        self.c_entry.insert(0, "1.5")
        self.c_entry.pack(side=tk.LEFT, padx=5)

        fit_extrema_button = Button(button_frame, text="Fit Extrema", command=self.fit_extrema)
        fit_extrema_button.pack(pady=5)

        export_button = Button(file_frame, text="Export Peaks", command=self.export_peaks)
        export_button.pack(side=tk.LEFT, padx=10)

        export_graph_button = Button(button_frame, text="Export Graph", command=self.export_graph)
        export_graph_button.pack(pady=5)

        quit_button = tk.Button(file_frame, text="Quit", command=self.root.quit)
        quit_button.pack(side=tk.LEFT)

        self.console = Text(self.root, height=4, width=50)
        self.console.pack(pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.original_data = None
        self.time_data = None
        self.fine_time = None
        self.derivative_data = None  # Add a separate attribute for derivative data
        self.file_directory = ""
        self.extrema_data = {}
        self.extrema_plots = []
        self.max_times = []
        self.min_times = []




        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
    def on_sampling_change(self, *args):
        if self.original_data:
            try:
                enhanced_sampling = max(1, int(self.enhanced_sampling_var.get()))
            except ValueError:
                self.console.insert(tk.END, "Invalid sampling value. Please enter a valid integer.\n")
                return
            self.update_plot()

    def update_plot(self):
        enhanced_sampling = max(1, int(self.enhanced_sampling_var.get()))
        self.fine_time = np.linspace(self.time_data.min(), self.time_data.max(),
                                     len(self.time_data) * enhanced_sampling)

        self.derivative_data = {}  # Initialize the derivative data dictionary
        for column in self.original_data.keys():
            spline = UnivariateSpline(self.time_data, self.original_data[column], s=0)
            derivative = spline.derivative()
            self.derivative_data[column] = derivative(self.fine_time)

        self.plot_derivatives()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            data = pd.read_csv(file_path)
            self.time_data = data['Time'].values
            self.original_data = {}

            self.ax.clear()

            enhanced_sampling = max(1, int(self.enhanced_sampling_var.get()))

            self.fine_time = np.linspace(self.time_data.min(), self.time_data.max(),
                                         len(self.time_data) * enhanced_sampling)

            self.derivative_data = {}
            for column in data.columns[1:]:
                spline = UnivariateSpline(self.time_data, data[column], s=0)
                derivative = spline.derivative()
                self.original_data[column] = data[column]  # Store original data
                self.derivative_data[column] = derivative(self.fine_time)  # Store derivative data

            self.plot_derivatives()

            base_name = os.path.splitext(os.path.basename(file_path))[0]
            new_filename = f"{base_name}_extrema.csv"
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, new_filename)
            self.file_directory = os.path.dirname(file_path)

            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(0, f'{self.time_data[0]}')
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(0, f'{self.time_data[-1]}')

    def plot_derivatives(self):
        self.ax.clear()
        if self.avg_derivative_var.get():
            avg_derivative = np.mean(list(self.derivative_data.values()), axis=0)
            self.ax.plot(self.fine_time, avg_derivative)
        else:
            for column, derivative_data in self.derivative_data.items():
                self.ax.plot(self.fine_time, derivative_data, label=f'Derivative of {column}')

        #self.ax.set_title('Derivative Plots')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Interpolation Derivative')
        self.canvas.draw()

    def toggle_average_derivative(self):
        if self.original_data:
            self.update_plot()

    def calculate_baseline(self):
        try:
            start_time = float(self.start_time_entry.get())
            end_time = float(self.end_time_entry.get())
            mask = (self.fine_time >= start_time) & (self.fine_time <= end_time)  # Use self.fine_time for the mask

            # Initialize variable to accumulate mean values and count them
            total_mean = 0
            count = 0

            # Iterate through each derivative dataset
            for key, derivative_data in self.derivative_data.items():
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
        pass

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
        pass

    def find_and_plot_extrema(self, data_within, indices, key):
        if len(data_within) > 0:
            local_max_indices = argrelextrema(data_within, np.greater)[0]
            local_min_indices = argrelextrema(data_within, np.less)[0]

            max_times = self.fine_time[indices][local_max_indices]
            min_times = self.fine_time[indices][local_min_indices]

            max_plots = self.ax.plot(max_times, data_within[local_max_indices], 'go')
            min_plots = self.ax.plot(min_times, data_within[local_min_indices], 'ro')

            self.extrema_plots.extend(max_plots + min_plots)

            self.extrema_data[key] = {
                'maxima': list(zip(max_times, data_within[local_max_indices])),
                'minima': list(zip(min_times, data_within[local_min_indices]))
            }

    def on_release(self, event):
        if event.xdata is not None and event.ydata is not None and self.rect is not None and self.fine_time is not None:
            end_x = event.xdata
            end_y = event.ydata
            self.rect.set_width(end_x - self.start_x)
            self.rect.set_height(end_y - self.start_y)
            self.canvas.draw()

            indices = (self.fine_time >= min(self.start_x, end_x)) & (self.fine_time <= max(self.start_x, end_x))

            for plot_obj in self.extrema_plots:
                plot_obj.remove()
            self.extrema_plots.clear()

            self.extrema_data.clear()
            self.max_times = []
            self.min_times = []

            if self.avg_derivative_var.get():
                avg_derivative = np.mean(list(self.derivative_data.values()), axis=0)
                if len(avg_derivative) == len(self.fine_time):
                    data_within = avg_derivative[indices]
                    self.find_and_plot_extrema(data_within, indices, 'Average')
                else:
                    self.console.insert(tk.END, "Error: Data length mismatch. Please reload the data.\n")
            else:
                for key, derivative_data in self.derivative_data.items():
                    if len(derivative_data) == len(self.fine_time):
                        data_within = derivative_data[indices]
                        self.find_and_plot_extrema(data_within, indices, key)
                    else:
                        self.console.insert(tk.END, f"Error: Data length mismatch for {key}. Please reload the data.\n")

            for key in self.extrema_data:
                maxima = self.extrema_data[key]['maxima']
                minima = self.extrema_data[key]['minima']

                max_times = [time for time, value in maxima]
                min_times = [time for time, value in minima]

                #print(f"Key: {key}")
                #print(f"Max times: {max_times}")
                #print(f"Min times: {min_times}")

                self.max_times.extend(max_times)
                self.min_times.extend(min_times)

            self.max_times = sorted(self.max_times)
            self.min_times = sorted(self.min_times)

            self.canvas.draw()

    def calculate_chirp_button(self):
        self.calculate_chirp(self.max_times, self.min_times)

    def calculate_chirp(self, max_times, min_times, export=False):
        try:
            max_periods = []
            min_periods = []

            for i in range(len(max_times) - 1):
                period = max_times[i + 1] - max_times[i]
                avg_time = (max_times[i + 1] + max_times[i]) / 2
                if period > 0:  # Ensure valid periods
                    max_periods.append((avg_time, period))

            for i in range(len(min_times) - 1):
                period = min_times[i + 1] - min_times[i]
                avg_time = (min_times[i + 1] + min_times[i]) / 2
                if period > 0:  # Ensure valid periods
                    min_periods.append((avg_time, period))

            max_periods = sorted(max_periods, key=lambda x: x[0])
            min_periods = sorted(min_periods, key=lambda x: x[0])

            max_times = [time for time, period in max_periods]
            max_frequencies = [1 / period for time, period in max_periods]
            min_times = [time for time, period in min_periods]
            min_frequencies = [1 / period for time, period in min_periods]

            if export:
                return max_times, max_frequencies, min_times, min_frequencies

            # Remove any existing inset axes
            for child in self.ax.get_children():
                if isinstance(child, plt.Axes):
                    child.remove()

            # Inset for linear fit
            inset_ax = self.ax.inset_axes([0.475, 0.275, 0.5, 0.5])
            all_times = np.array(max_times + min_times)
            all_frequencies = np.array(max_frequencies + min_frequencies)
            coef = np.polyfit(all_times, all_frequencies, 1)
            poly1d_fn = np.poly1d(coef)
            inset_ax.plot(all_times, all_frequencies, 'bo')
            inset_ax.plot(all_times, poly1d_fn(all_times), '--k', label=f'y={coef[0]:.2f}x + {coef[1]:.2f}')
            inset_ax.set_title('Chirp')
            inset_ax.set_xlabel('Time (s)')
            inset_ax.set_ylabel('Frequency (Hz)')
            inset_ax.legend(loc="upper right")

            self.canvas.draw()

            self.console.insert(tk.END, "Chirp calculation and plotting completed.\n")
        except Exception as e:
            self.console.insert(tk.END, f"Error in chirp calculation: {e}\n")

    def exp_decay(self, t, A, k, t0, c):
        return A * np.exp(-k * (t - t0)) + c

    def fit_extrema(self):
        try:
            # Retrieve initial guesses from user inputs
            A_guess = float(self.A_entry.get())
            k_guess = float(self.k_entry.get())
            t0_guess = float(self.t0_entry.get())
            c_guess = float(self.c_entry.get())

            # Define initial guesses
            initial_guesses_max = [A_guess, k_guess, t0_guess, c_guess]
            initial_guesses_min = [A_guess, k_guess, t0_guess, c_guess]

            # Fit maxima
            if len(self.max_times) > 1:
                max_values = np.array([value for time, value in self.extrema_data['Average']['maxima']])
                max_times = np.array(self.max_times)

                popt_max, _ = curve_fit(self.exp_decay, max_times, max_values, p0=initial_guesses_max, maxfev=10000)
                A_max, k_max, t0_max, c_max = popt_max

                fit_max = self.exp_decay(max_times, *popt_max)
                self.ax.plot(max_times, fit_max, 'g--',
                             label=f'Max Fit: A={A_max:.2f}, k={k_max:.2f}, t0={t0_max:.2f}, c={c_max:.2f}')

            # Fit minima
            if len(self.min_times) > 1:
                min_values = np.array([value for time, value in self.extrema_data['Average']['minima']])
                min_times = np.array(self.min_times)

                popt_min, _ = curve_fit(self.exp_decay, min_times, min_values, p0=initial_guesses_min, maxfev=10000)
                A_min, k_min, t0_min, c_min = popt_min

                fit_min = self.exp_decay(min_times, *popt_min)
                self.ax.plot(min_times, fit_min, 'r--',
                             label=f'Min Fit: A={A_min:.2f}, k={k_min:.2f}, t0={t0_min:.2f}, c={c_min:.2f}')

            self.ax.legend()
            self.canvas.draw()

        except Exception as e:
            self.console.insert(tk.END, f"Error in fitting extrema: {e}\n")

    def export_graph(self):
        try:
            # Get the base filename
            base_name = os.path.splitext(os.path.basename(self.filename_entry.get()))[0]
            file_directory = self.file_directory

            # Export the current canvas as a PNG file
            png_filename = os.path.join(file_directory, f"{base_name}.png")
            self.fig.savefig(png_filename, dpi=600)
            self.console.insert(tk.END, f"Graph exported as {png_filename}\n")

            # Export the average highly sampled derivative to a CSV file
            interderivative_filename = os.path.join(file_directory, f"{base_name}_interderivative.csv")
            avg_derivative = np.mean(list(self.derivative_data.values()), axis=0)
            interderivative_df = pd.DataFrame({'Time': self.fine_time, 'Average Derivative': avg_derivative})
            interderivative_df.to_csv(interderivative_filename, index=False)
            self.console.insert(tk.END, f"Interpolated derivative data exported as {interderivative_filename}\n")

            # Export the chirp data to a CSV file
            chirp_filename = os.path.join(file_directory, f"{base_name}_chirp.csv")
            max_times, max_frequencies, min_times, min_frequencies = self.calculate_chirp(self.max_times,
                                                                                          self.min_times, export=True)
            chirp_data = {
                'Max Times': max_times,
                'Max Frequencies': max_frequencies,
                'Min Times': min_times,
                'Min Frequencies': min_frequencies
            }
            chirp_df = pd.DataFrame(chirp_data)
            chirp_df.to_csv(chirp_filename, index=False)
            self.console.insert(tk.END, f"Chirp data exported as {chirp_filename}\n")

        except Exception as e:
            self.console.insert(tk.END, f"Error exporting graph and data: {e}\n")


# Create the main window and pass it to the DataApp class
root = tk.Tk()
app = DataApp(root)
root.mainloop()
