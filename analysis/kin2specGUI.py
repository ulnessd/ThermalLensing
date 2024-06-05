import tkinter as tk
from tkinter import filedialog, messagebox, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import stft
import numpy as np
import pandas as pd
import os


# Function to load data and plot kinetics
def load_data():
    global data, canvas, ax, file_directory, filename_entry
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not filepath:
        return
    file_directory = os.path.dirname(filepath)
    base_filename = os.path.splitext(os.path.basename(filepath))[0]
    filename_entry.delete(0, tk.END)
    filename_entry.insert(0, base_filename)
    data = pd.read_csv(filepath)
    ax.clear()
    ax.plot(data['Frame Number'], data['Pixel Index'])
    ax.set_title('Kinetics Data')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Position')
    canvas.draw()


# Function to produce spectrogram
def produce_spectrogram():
    global data, canvas, ax
    try:
        window_length_seconds = float(window_size_entry.get())
        max_freq = float(max_freq_entry.get())
        min_freq = float(min_freq_entry.get())
        max_time = float(max_time_entry.get())
        min_time = float(min_time_entry.get())
    except ValueError:
        messagebox.showerror("Input error", "Please enter valid numbers.")
        return

    sampling_rate = 1 / np.mean(np.diff(data['Frame Number']))  # Estimate sampling rate
    window_length_samples = int(window_length_seconds * sampling_rate)
    overlap_samples = window_length_samples // 2

    frequencies, times, Zxx = stft(data['Pixel Index'], fs=sampling_rate, window='hann', nperseg=window_length_samples,
                                   noverlap=overlap_samples)
    mask_freq = (frequencies <= max_freq) & (frequencies >= min_freq)
    mask_time = (times <= max_time) & (times >= min_time)

    ax.clear()
    ax.pcolormesh(times[mask_time], frequencies[mask_freq], np.abs(Zxx[mask_freq][:, mask_time]), shading='gouraud')
    ax.set_title('Spectrogram')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Frequency [Hz]')
    canvas.draw()


# Function to save the current spectrogram as a PNG file
def save_spectrogram():
    global file_directory, filename_entry
    if not file_directory:
        messagebox.showerror("Save error", "Load a file first.")
        return
    filename = filename_entry.get() + '.png'
    fig.savefig(os.path.join(file_directory, filename), dpi=600)


# GUI setup
root = tk.Tk()
root.title("Spectrogram Analysis Tool")

# Matplotlib figure
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()

# Entry fields with labels
window_size_label = Label(root, text="Window Size:")
window_size_entry = tk.Entry(root)
window_size_entry.insert(0, "20")
max_freq_label = Label(root, text="Max Frequency:")
max_freq_entry = tk.Entry(root)
max_freq_entry.insert(0, "4")
min_freq_label = Label(root, text="Min Frequency:")
min_freq_entry = tk.Entry(root)
min_freq_entry.insert(0, "0")
max_time_label = Label(root, text="Max Time:")
max_time_entry = tk.Entry(root)
max_time_entry.insert(0, "120")
min_time_label = Label(root, text="Min Time:")
min_time_entry = tk.Entry(root)
min_time_entry.insert(0, "0")
filename_label = Label(root, text="Filename:")
filename_entry = tk.Entry(root)

# Buttons
load_button = tk.Button(root, text="Load File", command=load_data)
produce_button = tk.Button(root, text="Produce Spectrogram", command=produce_spectrogram)
save_button = tk.Button(root, text="Save Spectrogram", command=save_spectrogram)
quit_button = tk.Button(root, text="Quit", command=root.destroy)

# Layout
canvas_widget.grid(row=0, column=0, columnspan=6)
load_button.grid(row=1, column=0)
window_size_label.grid(row=2, column=0)
window_size_entry.grid(row=2, column=1)
max_freq_label.grid(row=2, column=2)
max_freq_entry.grid(row=2, column=3)
min_freq_label.grid(row=3, column=0)
min_freq_entry.grid(row=3, column=1)
max_time_label.grid(row=3, column=2)
max_time_entry.grid(row=3, column=3)
min_time_label.grid(row=4, column=0)
min_time_entry.grid(row=4, column=1)
filename_label.grid(row=4, column=2)
filename_entry.grid(row=4, column=3)
produce_button.grid(row=5, column=4)
save_button.grid(row=5, column=5)
quit_button.grid(row=5, column=0)

root.mainloop()
