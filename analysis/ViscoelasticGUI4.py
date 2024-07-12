import math
import tkinter as tk
from tkinter import filedialog, Label, Entry, Button, Checkbutton, IntVar, StringVar, Text
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.signal import find_peaks
from scipy.stats import linregress
from scipy.optimize import curve_fit
import os
import zipfile


class DataAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Viscoelastic Data Analysis")

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

        self.console = Text(master, height=8)
        self.console.pack(fill=tk.BOTH, expand=True)

        self.start_time_var = StringVar(value="0")
        self.start_time_var.set("0.65")
        self.end_time_var = StringVar(value="0")
        self.end_time_var.set("1")
        self.baseline_var = StringVar()

        self.start_time_label = Label(control_frame, text="Start Time:")
        self.start_time_label.pack()
        self.start_time_entry = Entry(control_frame, textvariable=self.start_time_var)
        self.start_time_entry.pack()

        self.end_time_label = Label(control_frame, text="End Time:")
        self.end_time_label.pack()
        self.end_time_entry = Entry(control_frame, textvariable=self.end_time_var)
        self.end_time_entry.pack()

        self.baseline_label = Label(control_frame, text="Baseline:")
        self.baseline_label.pack()
        self.baseline_var = StringVar()
        self.baseline_var.set("2.0")
        self.baseline_entry = Entry(control_frame, textvariable=self.baseline_var, state='readonly')
        self.baseline_entry.pack()


        self.calculate_baseline_button = Button(control_frame, text="Calculate Baseline",
                                                command=self.calculate_baseline)
        self.calculate_baseline_button.pack()

        self.A_guess_var = StringVar(value="5")
        self.k_guess_var = StringVar(value="8")
        self.t0_var = StringVar(value="0")

        self.A_label = Label(control_frame, text="Initial guess for A:")
        self.A_label.pack()
        self.A_entry = Entry(control_frame, textvariable=self.A_guess_var)
        self.A_entry.pack()

        self.k_label = Label(control_frame, text="Initial guess for k:")
        self.k_label.pack()
        self.k_entry = Entry(control_frame, textvariable=self.k_guess_var)
        self.k_entry.pack()

        self.t0_label = Label(control_frame, text="t0:")
        self.t0_label.pack()
        self.t0_entry = Entry(control_frame, textvariable=self.t0_var)
        self.t0_entry.pack()

        self.fit_extrema_button = Button(control_frame, text="Fit Extrema", command=self.fit_extrema)
        self.fit_extrema_button.pack()

        self.peak_times = []
        self.peak_values = []
        self.trough_times = []
        self.trough_values = []

        self.refresh_button = Button(control_frame, text="Refresh", command=self.refresh_plot)
        self.refresh_button.pack()

        self.save_button = Button(control_frame, text="Save Report", command=self.create_report)
        self.save_button.pack()

        self.quit_button = Button(control_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack()

        self.data = None
        self.time = None
        self.fine_time = None
        self.current_derivative = None  # Initialize the current_derivative attribute
        self.freq_set = []

        self.setup_canvas_bindings() #Stuff for mouse drag
        self.line = None
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
        self.ax_raw.set_title('Area Data')
        self.ax_raw.set_xlabel('Time (s)')
        self.ax_raw.set_ylabel('mm^2')
        for column in self.data.columns[1:]:
            run_data = self.data[column]
            spline = UnivariateSpline(self.time, run_data, s=0)
            self.ax_raw.plot(fine_time, spline(fine_time), '-')

    def plot_average_data(self, fine_time):
        self.ax_raw.set_title('Area Data')
        self.ax_raw.set_xlabel('Time (s)')
        self.ax_raw.set_ylabel('mm^2')
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
        self.ax_deriv.set_title('Interpolation Derivative')
        self.ax_deriv.set_xlabel('Time (s)')
        self.ax_deriv.set_ylabel('mm^2/s')


        self.peak_times = []
        self.peak_values = []
        self.trough_times = []
        self.trough_values = []

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

            self.peak_times.extend(fine_time[peaks])
            self.peak_values.extend(derivative_avg[peaks])
            self.trough_times.extend(fine_time[troughs])
            self.trough_values.extend(derivative_avg[troughs])

            self.plot_frequencies(fine_time[peaks], fine_time[troughs])
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

                self.peak_times.extend(fine_time[peaks])
                self.peak_values.extend(derivative[peaks])
                self.trough_times.extend(fine_time[troughs])
                self.trough_values.extend(derivative[troughs])

                self.plot_frequencies(fine_time[peaks], fine_time[troughs])

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

            self.console.insert(tk.END,
                                f"Selected Fit Slope: {slope:.4f} +/- {(slope_ci[1] - slope_ci[0]) / 2:.4f}, Intercept: {intercept:.4f} +/- {(intercept_ci[1] - intercept_ci[0]) / 2:.4f}\n")
            self.console.insert(tk.END,
                                f"Slope/Intercept: {slope / intercept:.4f} +/- {-slope / intercept * math.sqrt((slope_ci[1] - slope_ci[0]) / (2 * slope) + (intercept_ci[1] - intercept_ci[0]) / (2 * intercept))}\n")

        self.canvas_freq.draw()

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
            std_dev = np.std(data_to_average)
            self.baseline_var.set(f"{baseline:.4f}")
            self.console.insert(tk.END, f"Calculated baseline: {baseline:.4f} +/- {std_dev:.4f}\n")
        except ValueError as e:
            self.console.insert(tk.END, f"Error: {str(e)}\n")

    def exp_decay_max(self, t, A, k, t0, baseline):
        return A * np.exp(-k * (t - t0)) + baseline

    def exp_decay_min(self, t, A, k, t0, baseline):
        return -A * np.exp(-k * (t - t0)) + baseline

    import numpy as np
    from scipy.optimize import curve_fit
    import tkinter as tk

    def exp_decay_max(t, A, k, t0, baseline):
        return A * np.exp(-k * (t - t0)) + baseline

    def exp_decay_min(t, A, k, t0, baseline):
        return -A * np.exp(-k * (t - t0)) + baseline

    def fit_extrema(self):
        def exp_decay_max(t, A, k):
            return A * np.exp(-k * (t - t0)) + baseline

        def exp_decay_min(t, A, k):
            return -A * np.exp(-k * (t - t0)) + baseline

        try:
            # Get initial guesses and user-defined t0
            A_guess = float(self.A_guess_var.get())
            k_guess = float(self.k_guess_var.get())
            t0 = float(self.t0_var.get())
            baseline = float(self.baseline_var.get())

            # Check if peak and trough data are available
            if not self.peak_times or not self.trough_times:
                self.console.insert(tk.END, "No peak or trough data available.\n")
                return

            # Filter peaks to include only those times larger than the first trough time
            if self.trough_times:
                min_time_threshold = min(self.trough_times)
                filtered_peak_times = [t for t in self.peak_times if t > min_time_threshold]
                filtered_peak_values = [v for t, v in zip(self.peak_times, self.peak_values) if t > min_time_threshold]
            else:
                filtered_peak_times = self.peak_times
                filtered_peak_values = self.peak_values


            # Fit peaks
            if filtered_peak_times and filtered_peak_values:
                popt_max, pcov_max = curve_fit(
                    exp_decay_max, filtered_peak_times, filtered_peak_values,
                    p0=[A_guess, k_guess],
                    bounds=([0, 0], [np.inf, np.inf])
                )
                A_max, k_max = popt_max
                std_devs_max = np.sqrt(np.diag(pcov_max))

                # Calculate confidence intervals
                ci_max = 1.96 * std_devs_max  # For 95% confidence
                A_max_low, A_max_high = A_max - ci_max[0], A_max + ci_max[0]
                k_max_low, k_max_high = k_max - ci_max[1], k_max + ci_max[1]


                self.console.insert(tk.END,
                                    f"Fit Parameters for Peaks: A = {A_max:.4f} +/- {(A_max_high - A_max_low) / 2:.4f}, k = {k_max:.4f} +/- {(k_max_high - k_max_low) / 2:.4f}\n")
                #self.console.insert(tk.END,
                                  #  f"Confidence Intervals for Peaks: A = [{A_max_low:.4f}, {A_max_high:.4f}], k = [{k_max_low:.4f}, {k_max_high:.4f}]\n")

                # Plot the fit
                fit_times = np.linspace(min(filtered_peak_times), max(filtered_peak_times) + 0.5, 100)
                fit_values = exp_decay_max(fit_times, A_max, k_max)
                self.ax_deriv.plot(fit_times, fit_values, 'r-', label='Fit for Peaks')

            # Fit troughs
            if self.trough_times and self.trough_values:
                popt_min, pcov_min = curve_fit(
                    exp_decay_min, self.trough_times, self.trough_values,
                    p0=[A_guess, k_guess],
                    bounds=([0, 0], [np.inf, np.inf])
                )
                A_min, k_min = popt_min
                std_devs_min = np.sqrt(np.diag(pcov_min))


                # Calculate confidence intervals
                ci_min = 1.96 * std_devs_min  # For 95% confidence
                A_min_low, A_min_high = A_min - ci_min[0], A_min + ci_min[0]
                k_min_low, k_min_high = k_min - ci_min[1], k_min + ci_min[1]

                self.console.insert(tk.END, f"Fit Parameters for Troughs: A = {A_min:.4f} +/- {(A_min_high-A_min_low)/2:.4f}, k = {k_min:.4f} +/- {(k_min_high-k_min_low)/2:.4f}\n")
                #self.console.insert(tk.END,
                                   # f"Confidence Intervals for Troughs: A = [{A_min_low:.4f}, {A_min_high:.4f}], k = [{k_min_low:.4f}, {k_min_high:.4f}]\n")

                # Plot the fit
                fit_times = np.linspace(min(self.trough_times), max(self.trough_times) + 0.5, 100)
                fit_values = exp_decay_min(fit_times, A_min, k_min)
                self.ax_deriv.plot(fit_times, fit_values, 'b-', label='Fit for Troughs')

            #self.ax_deriv.legend()
            self.canvas_deriv.draw()

        except Exception as e:
            self.console.insert(tk.END, f"Error in fitting extrema: {str(e)}\n")

    def generate_report_text(self):
        # Get console contents
        console_text = self.console.get(1.0, tk.END)
        return console_text

    def save_report_to_zip(self, zip_filepath):
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            # Save raw data to zip
            raw_data_csv = self.data.to_csv(index=False)
            zipf.writestr('raw_data.csv', raw_data_csv)

            # Save derivative data to zip
            enhanced_sampling = int(self.sampling_var.get())
            fine_time = np.linspace(self.time.min(), self.time.max(), len(self.time) * enhanced_sampling)
            derivatives = pd.DataFrame({'Time': fine_time})

            all_peaks_times = []
            all_peaks_values = []
            all_troughs_times = []
            all_troughs_values = []

            if self.avg_check_var.get():
                avg_data = np.mean(self.data.iloc[:, 1:], axis=1)
                spline_avg = UnivariateSpline(self.time, avg_data, s=0)
                derivative_avg = spline_avg.derivative()(fine_time)
                peaks, _ = find_peaks(derivative_avg,
                                      prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative_avg)))
                troughs, _ = find_peaks(-derivative_avg,
                                        prominence=float(self.prominence_var.get()) / 100 * max(abs(derivative_avg)))
                derivatives['Average_Derivative'] = derivative_avg

                all_peaks_times.extend(fine_time[peaks])
                all_peaks_values.extend(derivative_avg[peaks])
                all_troughs_times.extend(fine_time[troughs])
                all_troughs_values.extend(derivative_avg[troughs])
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

                    all_peaks_times.extend(fine_time[peaks])
                    all_peaks_values.extend(derivative[peaks])
                    all_troughs_times.extend(fine_time[troughs])
                    all_troughs_values.extend(derivative[troughs])

            derivative_data_csv = derivatives.to_csv(index=False)
            zipf.writestr('derivative_data.csv', derivative_data_csv)

            # Combine peaks and troughs into a single set of data with times and values
            combined_peaks = pd.DataFrame({'Times': all_peaks_times, 'Values': all_peaks_values})
            combined_troughs = pd.DataFrame({'Times': all_troughs_times, 'Values': all_troughs_values})

            combined_data = pd.concat([combined_peaks, combined_troughs]).sort_values(by='Times')
            combined_peaks_troughs_csv = combined_data.to_csv(index=False)
            zipf.writestr('combined_peaks_troughs.csv', combined_peaks_troughs_csv)

            # Save frequency data to zip
            if self.freq_set:
                times, frequencies = zip(*self.freq_set)
                frequency_data = pd.DataFrame({'Time': times, 'Frequency': frequencies})
                frequency_data_csv = frequency_data.to_csv(index=False)
                zipf.writestr('frequency_data.csv', frequency_data_csv)

            # Save the console output to zip
            # console_output = self.console.get(1.0, tk.END)
            # zipf.writestr('console_output.txt', console_output)

            # Save report text to zip
            report_text = self.generate_report_text()
            zipf.writestr('report.txt', report_text)

            # Save the graphs to the zip file
            import io

            def save_fig_to_zip(fig, zipf, filename):
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=600)
                buf.seek(0)
                zipf.writestr(filename, buf.read())

            save_fig_to_zip(self.fig_raw, zipf, 'raw_data.png')
            save_fig_to_zip(self.fig_deriv, zipf, 'derivative_data.png')
            save_fig_to_zip(self.fig_freq, zipf, 'frequency_data.png')

        self.console.insert(tk.END, f"Report created and saved to {zip_filepath}\n")

    def create_report(self):
        zip_filepath = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
        if not zip_filepath:
            return
        self.save_report_to_zip(zip_filepath)

    def refresh_plot(self):
        self.console.delete(1.0, tk.END)
        self.freq_set = []
        self.update_plot()




root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()





root = tk.Tk()
app = DataAnalyzerApp(root)
root.mainloop()
