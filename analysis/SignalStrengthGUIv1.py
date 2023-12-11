import cv2
import numpy as np
import os
import csv
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


selected_files = []
#processed_data = None


def process_videos():
    global selected_files

    # Grab values from the GUI
    start_col = int(start_entry.get())
    end_col = int(stop_entry.get())

    lensframestart= int(lensstart_entry.get())
    lensframestop= int(lensstop_entry.get())

    aggregated_background = None
    aggregated_signal = None

    # Process all selected files
    for current_filename in selected_files:
        cap = cv2.VideoCapture(current_filename)
        background_frames = []
        signal_frames = []

        for i in range(lensframestop+5):
            ret, frame = cap.read()
            if not ret:
                break

            # As OpenCV loads images in BGR, we'll get the red channel
            red_channel = frame[:, :, 2]

            if i < int(background_entry.get()):
                background_frames.append(red_channel)
            elif lensframestart <= i <= lensframestop:
                signal_frames.append(red_channel)

        cap.release()

        # Average frames and sum over specified columns
        if background_frames:
            average_background = np.mean(background_frames, axis=0)
            summed_background = np.sum(average_background[:, start_col:end_col], axis=1)

            if aggregated_background is None:
                aggregated_background = summed_background
            else:
                aggregated_background += summed_background

        if signal_frames:
            average_signal = np.mean(signal_frames, axis=0)
            summed_signal = np.sum(average_signal[:, start_col:end_col], axis=1)

            if aggregated_signal is None:
                aggregated_signal = summed_signal
            else:
                aggregated_signal += summed_signal

    # Get average values after iterating through all files
    aggregated_background /= len(selected_files)
    aggregated_signal /= len(selected_files)

    # Perform the division
    result = np.divide(aggregated_signal, aggregated_background, out=np.zeros_like(aggregated_signal),
                       where=aggregated_background != 0)

    return result


def save_to_csv(data, output_filename):
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for value in data:
            writer.writerow([value])


def generate_report(data):
    min_row = np.argmin(data)
    min_value = data[min_row]

    low_max_value = np.max(data[:min_row])
    low_max_row = np.argmax(data[:min_row])

    high_max_value = np.max(data[min_row:])
    high_max_row = min_row + np.argmax(data[min_row:])

    report_dict = {
        'min_row': min_row,
        'min_value': min_value,
        'low_max_row': low_max_row,
        'low_max_value': low_max_value,
        'high_max_row': high_max_row,
        'high_max_value': high_max_value
    }

    report_str = (f"Minimum value: {min_value:.4f} at row {min_row}\n"
                  f"Maximum value below min: {low_max_value:.4f} at row {low_max_row}\n"
                  f"Maximum value above min: {high_max_value:.4f} at row {high_max_row}\n")

    return report_dict, report_str

def save_report(report, filename):
    with open(filename, 'w') as f:
        f.write(report)


def process_and_fit_data(data, min_row, low_max_row, high_max_row):
    if data is None:
        raise ValueError("Received 'None' for data. Data should be a valid list or array.")
    # Grab values from the GUI
    spline_value = float(spline_entry.get())

    # Truncate data
    truncated_x = np.arange(low_max_row - 40, high_max_row + 40)
    truncated_y = data[low_max_row - 40: high_max_row + 40]

    # Create a B-spline with the GUI-specified smoothness
    spline = UnivariateSpline(truncated_x, truncated_y, s=spline_value)
    interpolated_data = spline(truncated_x)

    return truncated_x, truncated_y, interpolated_data

def select_files():
    global selected_files
    files = filedialog.askopenfilenames(title="Select video files", filetypes=[("H264 files", "*.h264"), ("All files", "*.*")])
    selected_files = list(files)
    console.insert(tk.END, f"{len(selected_files)} files selected.\n")

def save_to_textfile():
    report = console.get("1.0", tk.END)
    if not report.strip():
        console.insert(tk.END, "No report to save.\n")
        return
    save_path = filedialog.asksaveasfilename(title="Save Report", filetypes=[("Text files", "*.txt"), ("All files", "*.*")], defaultextension=".txt")
    if not save_path:
        return
    with open(save_path, "w") as file:
        file.write(report)
    console.insert(tk.END, f"Report saved to {save_path}\n")


report_dict = None  # Define it at the beginning of your script along with selected_files

def process_data():
    global report_dict, processed_data  # Declare it as global here

    data = process_videos()
    report_dict, report_str = generate_report(data)
    console.insert(tk.END, report_str)

    # Updating the global variable with the processed data
    processed_data = data

    min_row = report_dict['min_row']
    low_max_row = report_dict['low_max_row']
    high_max_row = report_dict['high_max_row']

    truncated_x, truncated_y, interpolated_data = process_and_fit_data(data, min_row, low_max_row, high_max_row)
    # Add any additional code here to handle the processed and fitted data as needed.


def generate_plot_callback():
    global report_dict, processed_data

    # Ensure that the previous messages are cleared from the console.
    #console.delete(1.0, tk.END)

    # Extracting the details for fitting
    min_row = report_dict['min_row']
    low_max_row = report_dict['low_max_row']
    high_max_row = report_dict['high_max_row']

    # Fetching user input
    spline_value = float(spline_entry.get())
    calibration_value = float(calibration_entry.get())

    # Processing data and obtaining interpolation
    processed_x, original_data, interpolated_data = process_and_fit_data(processed_data, min_row, low_max_row, high_max_row)

    # Create a new Figure and Axes to plot the data
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    ax.plot(processed_x, original_data, 'o', label='Original Data',c='black')
    ax.plot(processed_x, interpolated_data, '-', label='Interpolated Curve')
    ax.set_title("Original Data vs. Interpolated Curve")
    ax.set_xlabel("Row Number")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

    # Embed the plot in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=app)  # 'app' should be your main tkinter window
    canvas_widget = canvas.get_tk_widget()

    # Specify a grid or pack location for canvas_widget as per your GUI layout
    canvas_widget.pack()
    canvas.draw()

    # Calculating values
    interp_max = np.max(interpolated_data)
    interp_min = np.min(interpolated_data)
    difference = interp_max - interp_min

    spline = UnivariateSpline(processed_x, original_data - interpolated_data, s=spline_value)
    zeros = spline.roots()

    zeros_right_of_min = zeros[zeros > min_row]
    zeros_left_of_min = zeros[zeros < min_row]

    first_zero_right = zeros_right_of_min[0] if zeros_right_of_min.size > 0 else None
    first_zero_left = zeros_left_of_min[-1] if zeros_left_of_min.size > 0 else None

    zero_difference = first_zero_right - first_zero_left if first_zero_left is not None and first_zero_right is not None else None

    # Constructing the report
    console_text = (f"Thermal lens strength: {difference:.4f}\n"
                    f"Thermal lens width (mm): {(zero_difference * calibration_value) if zero_difference else 'N/A'}\n")

    console.insert(tk.END, console_text,"red")



app = tk.Tk()
app.title("Video Processor")

file_button = tk.Button(app, text="Select Video Files", command=select_files)
file_button.pack(pady=10)

background_label = tk.Label(app, text="Background Frames")
background_label.pack()
background_entry = tk.Entry(app)
background_entry.pack(pady=5)
background_entry.insert(0, "120")

start_label = tk.Label(app, text="Marginal Start")
start_label.pack()
start_entry = tk.Entry(app)
start_entry.pack(pady=5)
start_entry.insert(0, "0")

stop_label = tk.Label(app, text="Marginal Stop")
stop_label.pack()
stop_entry = tk.Entry(app)
stop_entry.pack(pady=5)
stop_entry.insert(0, "719")

lensstart_label = tk.Label(app, text="Thermal Lens Start")
lensstart_label.pack()
lensstart_entry = tk.Entry(app)
lensstart_entry.pack(pady=5)
lensstart_entry.insert(0, "202")

lensstop_label = tk.Label(app, text="Thermal Lens Stop")
lensstop_label.pack()
lensstop_entry = tk.Entry(app)
lensstop_entry.pack(pady=5)
lensstop_entry.insert(0, "209")

spline_label = tk.Label(app, text="Spline Value")
spline_label.pack()
spline_entry = tk.Entry(app)
spline_entry.pack(pady=5)
spline_entry.insert(0, "0.01")

calibration_label = tk.Label(app, text="Calibration (mm)")
calibration_label.pack()
calibration_entry = tk.Entry(app)
calibration_entry.pack(pady=5)
calibration_entry.insert(0, "0.007")

process_button = tk.Button(app, text="Process", command=process_data)
process_button.pack(pady=10)

console = scrolledtext.ScrolledText(app, width=80, height=10)
console.pack(pady=10)
console.tag_configure("red", foreground="red")

plot_button = tk.Button(app, text="Generate Interpolation Plot", command=generate_plot_callback)
plot_button.pack()


save_button = tk.Button(app, text="Save Report", command=save_to_textfile)
save_button.pack(pady=10)

quit_button = tk.Button(app, text="Quit", command=app.quit)
quit_button.pack(pady=20)

app.mainloop()
