import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar, StringVar, Text
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.signal import find_peaks
from scipy.stats import linregress
import os
import zipfile


class DataAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Comprehensive Data Analysis Tool")

        # Initialize line to None
        self.line = None

        # Setting up frames for layout
        top_frame = tk.Frame(self.master)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control panel
        control_frame = tk.Frame(top_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Canvas for direct data visualization
        self.fig_raw = Figure(figsize=(5, 4))
        self.ax_raw = self.fig_raw.add_subplot(111)
        self.canvas_raw = FigureCanvasTkAgg(self.fig_raw, master=top_frame)
        self.canvas_raw.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for derivative data visualization
        self.fig_deriv = Figure(figsize=(5, 4))
        self.ax_deriv = self.fig_deriv.add_subplot(111)
        self.canvas_deriv = FigureCanvasTkAgg(self.fig_deriv, master=top_frame)
        self.canvas_deriv.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas for frequency analysis
        self.fig_freq = Figure(figsize=(5, 4))
        self.ax_freq = self.fig_freq.add_subplot(111)
        self.canvas_freq = FigureCanvasTkAgg(self.fig_freq, master=top_frame)
        self.canvas_freq.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Controls
        self.sampling_label = Label(control_frame, text="Enhanced Sampling:")
        self.sampling_label.pack()

        self.sampling_var = StringVar()
        self.sampling_var.set("50")  # Default value
        self.sampling_var.trace("w", self.update_plot_with_sampling)  # Trace changes
        self.sampling_entry = Entry(control_frame, textvariable=self.sampling_var)
        self.sampling_entry.pack()

        self.prominence_label = Label(control_frame, text="Prominence (%):")
        self.prominence_label.pack()

        self.prominence_var = StringVar()
        self.prominence_var.set("10")  # Default value
        self.prominence_var.trace("w", self.update_derivative_plot_with_prominence)  # Trace changes
        self.prominence_entry = Entry(control_frame, textvariable=self.prominence_var)
        self.prominence_entry.pack()

        self.avg_check_var = IntVar()
        self.avg_checkbox = Checkbutton(control_frame, text="Average Runs", variable=self.avg_check_var,
                                        command=self.update_plot)
        self.avg_checkbox.pack()

        self.load_button = Button(control_frame, text="Load Data", command=self.load_data)
        self.load_button.pack()

        # Adding Start Time and End Time text boxes
        self.start_time_label = Label(control_frame, text="Start Time:")
        self.start_time_label.pack()
        self.start_time_var = StringVar()
        self.start_time_var.set(".65")
        self.start_time_entry = Entry(control_frame, textvariable=self.start_time_var)
        self.start_time_entry.pack()

        self.end_time_label = Label(control_frame, text="End Time:")
        self.end_time_label.pack()
        self.end_time_var = StringVar()
        self.end_time_var.set("1")
        self.end_time_entry = Entry(control_frame, textvariable=self.end_time_var)
        self.end_time_entry.pack()

        self.calculate_baseline_button = Button(control_frame, text="Calculate Baseline", command=self.calculate_baseline)
        self.calculate_baseline_button.pack()

        self.baseline_label = Label(control_frame, text="Baseline:")
        self.baseline_label.pack()
        self.baseline_var = StringVar()
        self.baseline_var.set("2.0")
        self.baseline_entry = Entry(control_frame, textvariable=self.baseline_var, state='readonly')
        self.baseline_entry.pack()

        self.refresh_button = Button(control_frame, text="Refresh", command=self.refresh_plot)
        self.refresh_button.pack()

        self.report_button = Button(control_frame, text="Create Report", command=self.create_report)
        self.report_button.pack()

        self.dump_graphs_button = Button(control_frame, text="Dump Graphs", command=self.dump_graphs)
        self.dump_graphs_button.pack()

        self.quit_button = Button(control_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack()

        self.console = Text(master, height=8)
        self.console.pack(fill=tk.BOTH, expand=True)

        self.data = None
        self.time = None
        self.fine_time = None
        self.current_derivative = None
        self.freq_set = []

        self.setup_canvas_bindings()

    def quit_app(self):
        self.master.quit()

    def load_data(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
        self.data = pd.read_csv(filepath)
        self.time = self.data['Time']
        self.update_plot()

    def update_plot(self):
        self.update_plot_with_sampling(None, None, None)

    def update_plot_with_sampling(self, name, index, mode):
        try:
            enhanced_sampling = int(self.sampling_var.get())
        except ValueError:
            self.console.insert(tk.END, "Invalid enhanced sampling value. Please enter a valid integer.\n")
            return  # Exit if the conversion fails

        self.fine_time = np.linspace(self.time.min(), self.time.max(), len(self.time) * enhanced_sampling)

        self.ax_raw.clear()
        self.ax_deriv.clear()

        if self.avg_check_var.get():
            self.plot_average_data(self.fine_time)
        else:
            self.plot_individual_runs(self.fine_time)

        self.canvas_raw.draw()
        self.update_derivative_plot_with_prominence(None, None, None)

    def plot_individual_runs(self, fine_time):
        for column in self.data.columns[1:]:
            run_data = self.data[column]
            spline = UnivariateSpline(self.time, run_data, s=0)
            self.ax_raw.plot(fine_time, spline(fine_time), '-')

    def plot_average_data(self, fine_time):
        avg_data = np.mean(self.data.iloc[:, 1:], axis=1)
        spline_avg = UnivariateSpline(self.time, avg_data, s=0)
        self.ax_raw.plot(fine_time, spline_avg(fine_time), '-')

    def update_derivative_plot_with_prominence(self, name, index, mode):
        try:
            enhanced_sampling = int(self.sampling_var.get())
            prominence_factor = float(self.prominence_var.get()) / 100
        except ValueError:
            self.console.insert(tk.END, "Invalid input value. Please enter valid numbers.\n")
            return

        fine_time = np.linspace(self.time.min(), self.time.max(), len(self.time) * enhanced_sampling)
        self.ax_deriv.clear()
        self.ax_freq.clear()

        if self.avg_check_var.get():
            avg_data = np.mean(self.data.iloc[:, 1:], axis=1)
            spline_avg = UnivariateSpline(self.time, avg_data, s=0)
            derivative_avg = spline_avg.derivative()(fine_time)
            max_deriv_val = np.max(np.abs(derivative_avg))
            prominence_value = prominence_factor * max_deriv_val

            peaks, _ = find_peaks(derivative_avg, prominence=prominence_value)
            troughs, _ = find_peaks(-derivative_avg, prominence=prominence_value)

            self.ax_deriv.plot(fine_time, derivative_avg, '-')
            self.ax_deriv.plot(fine_time[peaks], derivative_avg[peaks], 'go')
            self.ax_deriv.plot(fine_time[troughs], derivative_avg[troughs], 'ro')

            # Print peaks and troughs times to the console
            peak_times = fine_time[peaks]
            trough_times = fine_time[troughs]
            #self.console.insert(tk.END, f"Peak times: {peak_times}\n")
            #self.console.insert(tk.END, f"Trough times: {trough_times}\n")

            self.plot_frequencies(peak_times, trough_times)
        else:
            for column in self.data.columns[1:]:
                run_data = self.data[column]
                spline = UnivariateSpline(self.time, run_data, s=0)
                derivative = spline.derivative()(fine_time)
                max_deriv_val = np.max(np.abs(derivative))
                prominence_value = prominence_factor * max_deriv_val

                peaks, _ = find_peaks(derivative, prominence=prominence_value)
                troughs, _ = find_peaks(-derivative, prominence=prominence_value)

                self.ax_deriv.plot(fine_time, derivative, '-')
                self.ax_deriv.plot(fine_time[peaks], derivative[peaks], 'go')
                self.ax_deriv.plot(fine_time[troughs], derivative[troughs], 'ro')

                # Print peaks and troughs times to the console
                peak_times = fine_time[peaks]
                trough_times = fine_time[troughs]
                #self.console.insert(tk.END, f"Peak times: {peak_times}\n")
                #self.console.insert(tk.END, f"Trough times: {trough_times}\n")

                self.plot_frequencies(peak_times, trough_times)

        self.canvas_deriv.draw()

    def plot_frequencies(self, peak_times, trough_times):
        if len(peak_times) > 1:
            peak_intervals = np.diff(peak_times)
            peak_frequencies = 1 / peak_intervals
            peak_avg_times = (peak_times[:-1] + peak_times[1:]) / 2
            self.freq_set.extend(zip(peak_avg_times, peak_frequencies))

        if len(trough_times) > 1:
            trough_intervals = np.diff(trough_times)
            trough_frequencies = 1 / trough_intervals
            trough_avg_times = (trough_times[:-1] + trough_times[1:]) / 2
            self.freq_set.extend(zip(trough_avg_times, trough_frequencies))

        # Clear the frequency plot
        self.ax_freq.clear()

        # Plotting combined freq_set
        if self.freq_set:
            times, frequencies = zip(*self.freq_set)
            self.ax_freq.plot(times, frequencies, 'ko', label='Combined Frequencies')

        self.ax_freq.set_title('Calculated Frequencies')
        self.ax_freq.set_xlabel('Time (s)')
        self.ax_freq.set_ylabel('Frequency (Hz)')
        self.canvas_freq.draw()

    def setup_canvas_bindings(self):
        self.canvas_freq.mpl_connect('button_press_event', self.on_press)
        self.canvas_freq.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas_freq.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        if event.inaxes is not self.ax_freq:
            return
        self.drag_start = event.xdata
        self.line = self.ax_freq.axvline(x=self.drag_start, color='red', linewidth=1)

    def on_motion(self, event):
        if event.inaxes is not self.ax_freq or self.line is None:
            return
        self.line.set_xdata([event.xdata, event.xdata])
        self.canvas_freq.draw()

    def on_release(self, event):
        if event.inaxes is not self.ax_freq or self.drag_start is None:
            return
        self.ax_freq.axvline(x=event.xdata, color='red', linewidth=1)
        self.selected_region = (min(self.drag_start, event.xdata), max(self.drag_start, event.xdata))
        self.highlight_region()
        self.fit_selected_region()
        self.drag_start = None
        self.line = None
        self.canvas_freq.draw()

    def highlight_region(self):
        self.ax_freq.axvspan(*self.selected_region, color='yellow', alpha=0.3)
        self.canvas_freq.draw()

    def fit_selected_region(self):
        if not self.freq_set:
            return

        times, frequencies = zip(*self.freq_set)
        times = np.array(times)
        frequencies = np.array(frequencies)

        start, end = self.selected_region
        mask = (times >= start) & (times <= end)

        selected_times = times[mask]
        selected_frequencies = frequencies[mask]

        if len(selected_times) > 1:
            slope, intercept, r_value, p_value, std_err = linregress(selected_times, selected_frequencies)

            # Calculate confidence intervals
            t_value = 1.96  # For 95% confidence
            slope_ci = (slope - t_value * std_err, slope + t_value * std_err)
            intercept_ci = (intercept - t_value * std_err, intercept + t_value * std_err)

            fit_line = np.poly1d([slope, intercept])
            fit_x = np.linspace(min(selected_times), max(selected_times), 100)
            self.ax_freq.plot(fit_x, fit_line(fit_x), 'r--')

            self.console.insert(tk.END, f"Selected Fit Slope: {slope:.4f}, Intercept: {intercept:.4f}\n")
            self.console.insert(tk.END, f"Slope CI: {slope_ci[0]:.4f} to {slope_ci[1]:.4f}\n")
            self.console.insert(tk.END, f"Intercept CI: {intercept_ci[0]:.4f} to {intercept_ci[1]:.4f}\n")
            self.console.insert(tk.END, f"Slope/Intercept: {slope/intercept:.4f}\n")

        self.canvas_freq.draw()


    def save_raw_data(self, directory):
        filepath = os.path.join(directory, 'raw_data.csv')
        self.data.to_csv(filepath, index=False)

    def save_derivative_data(self, directory):
        filepath = os.path.join(directory, 'derivative_data.csv')
        enhanced_sampling = int(self.sampling_var.get())
        fine_time = np.linspace(self.time.min(), self.time.max(), len(self.time) * enhanced_sampling)
        derivatives = pd.DataFrame({'Time': fine_time})

        if self.avg_check_var.get():
            avg_data = np.mean(self.data.iloc[:, 1:], axis=1)
            spline_avg = UnivariateSpline(self.time, avg_data, s=0)
            derivative_avg = spline_avg.derivative()(fine_time)
            peaks, _ = find_peaks(derivative_avg,
                                  prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative_avg)))
            troughs, _ = find_peaks(-derivative_avg,
                                    prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative_avg)))
            derivatives['Average_Derivative'] = derivative_avg
        else:
            for column in self.data.columns[1:]:
                run_data = self.data[column]
                spline = UnivariateSpline(self.time, run_data, s=0)
                derivative = spline.derivative()(fine_time)
                peaks, _ = find_peaks(derivative,
                                      prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative)))
                troughs, _ = find_peaks(-derivative,
                                        prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative)))
                derivatives[f'{column}_Derivative'] = derivative

        derivatives.to_csv(filepath, index=False)

        # Save peaks and troughs separately
        peaks_troughs_filepath = os.path.join(directory, 'peaks_troughs.csv')
        peaks_troughs_data = pd.DataFrame({'Peak Times': fine_time[peaks], 'Trough Times': fine_time[troughs]})
        peaks_troughs_data.to_csv(peaks_troughs_filepath, index=False)

    def save_frequency_data(self, directory):
        filepath = os.path.join(directory, 'frequency_data.csv')
        if self.freq_set:
            times, frequencies = zip(*self.freq_set)
            frequency_data = pd.DataFrame({'Time': times, 'Frequency': frequencies})
            frequency_data.to_csv(filepath, index=False)

    def calculate_baseline(self):
        try:
            start_time = float(self.start_time_var.get())
            end_time = float(self.end_time_var.get())

            if start_time >= end_time:
                self.console.insert(tk.END, "Start time must be less than end time.\n")
                return

            if self.fine_time is None:
                self.console.insert(tk.END, "No data loaded or fine_time not initialized.\n")
                return

            mask = (self.fine_time >= start_time) & (self.fine_time <= end_time)

            if self.avg_check_var.get() and self.current_derivative is not None:
                data_to_average = self.current_derivative[mask]
            else:
                data_to_average = []
                for column in self.data.columns[1:]:
                    run_data = self.data[column]
                    spline = UnivariateSpline(self.time, run_data, s=0)
                    derivative = spline.derivative()(self.fine_time)
                    data_to_average.extend(derivative[mask])

            if len(data_to_average) == 0:
                self.console.insert(tk.END, "No data points found in the specified range.\n")
                return

            baseline = np.mean(data_to_average)
            self.baseline_var.set(f"{baseline:.4f}")
            self.console.insert(tk.END, f"Calculated baseline: {baseline:.4f}\n")
        except ValueError as e:
            self.console.insert(tk.END, f"Error: {str(e)}\n")

    def save_report(self, directory, report_text):
        filepath = os.path.join(directory, 'report.txt')
        with open(filepath, 'w') as file:
            file.write(report_text)

    def generate_report_text(self):
        report_text = f"Sample Name: {self.master.title()}\n\n"
        if self.freq_set:
            times, frequencies = zip(*self.freq_set)
            slope, intercept, r_value, p_value, std_err = linregress(times, frequencies)
            slope_ci = (slope - 1.96 * std_err, slope + 1.96 * std_err)
            intercept_ci = (intercept - 1.96 * std_err, intercept + 1.96 * std_err)
            report_text += f"Slope: {slope:.4f}, CI: {slope_ci}\n"
            report_text += f"Intercept: {intercept:.4f}, CI: {intercept_ci}\n"
        return report_text

    def zip_files(self, directory):
        zip_filename = os.path.join(directory, 'report.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in ['raw_data.csv', 'derivative_data.csv', 'frequency_data.csv', 'report.txt']:
                zipf.write(os.path.join(directory, file), arcname=file)

    def create_report(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        self.save_raw_data(directory)
        self.save_derivative_data(directory)
        self.save_frequency_data(directory)
        report_text = self.generate_report_text()
        self.save_report(directory, report_text)
        self.zip_files(directory)
        self.console.insert(tk.END, f"Report created and saved to {directory}\n")

    def refresh_plot(self):
        self.console.delete(1.0, tk.END)
        self.freq_set = []
        self.update_plot()

    def save_graphs(self, directory):
        raw_graph_path = os.path.join(directory, 'raw_data.png')
        deriv_graph_path = os.path.join(directory, 'derivative_data.png')
        freq_graph_path = os.path.join(directory, 'frequency_data.png')

        self.fig_raw.savefig(raw_graph_path, dpi=600)
        self.fig_deriv.savefig(deriv_graph_path, dpi=600)
        self.fig_freq.savefig(freq_graph_path, dpi=600)

    def dump_graphs(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        self.save_graphs(directory)
        self.console.insert(tk.END, f"Graphs saved to {directory}\n")


root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
