import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

def load_and_plot():
    global filename
    filename = filedialog.askopenfilename()
    if not filename:
        return

    try:
        data = pd.read_csv(filename)
        max_freq = float(max_freq_entry.get())
        threshold = float(threshold_entry.get())
        filtered_data = data[(data['Frequency'] >= 0) & (data['Frequency'] <= max_freq)]
        peaks, _ = find_peaks(filtered_data['Magnitude'], height=threshold)

        fig, ax = plt.subplots()
        ax.plot(filtered_data['Frequency'], filtered_data['Magnitude'], linestyle='-', color='black')
        if show_peaks_var.get():
            ax.scatter(filtered_data.iloc[peaks]['Frequency'], filtered_data.iloc[peaks]['Magnitude'], color='red')
        ax.set(title='Spectrum', xlabel='Frequency (Hz)', ylabel='Magnitude (arbitrary units)')
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=3, column=0, columnspan=4)
        canvas.draw()

        # Save peak data to variable for export
        global peak_data
        peak_data = filtered_data.iloc[peaks]
        global base_filename
        base_filename = os.path.join(os.path.dirname(filename), base_filename_entry.get())
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def export_graph():
    try:
        plt.savefig(f"{base_filename}.png", dpi=600)
        messagebox.showinfo("Export Successful", f"Graph exported as PNG to {base_filename}.png")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while exporting the graph: {e}")

def export_peaks():
    try:
        peak_data.to_csv(f"{base_filename}.peaks.csv", index=False)
        messagebox.showinfo("Export Successful", f"Peaks data exported to CSV at {base_filename}.peaks.csv")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while exporting peaks data: {e}")

# Create the main window
window = tk.Tk()
window.title("What's Shakin'")

# Layout
tk.Label(window, text="Max Frequency:").grid(row=0, column=0)
max_freq_entry = tk.Entry(window)
max_freq_entry.insert(0, '8')
max_freq_entry.grid(row=0, column=1)

tk.Label(window, text="Peak Threshold:").grid(row=1, column=0)
threshold_entry = tk.Entry(window)
threshold_entry.insert(0, '25')
threshold_entry.grid(row=1, column=1)

show_peaks_var = tk.BooleanVar()
tk.Checkbutton(window, text="Show Peaks", variable=show_peaks_var).grid(row=2, column=0)

tk.Button(window, text="Load and Plot", command=load_and_plot).grid(row=2, column=1)
tk.Button(window, text="Export Graph", command=export_graph).grid(row=2, column=2)
tk.Button(window, text="Export Peaks", command=export_peaks).grid(row=2, column=3)

tk.Label(window, text="Base Filename:").grid(row=0, column=2)
base_filename_entry = tk.Entry(window)
base_filename_entry.grid(row=0, column=3)

window.mainloop()

