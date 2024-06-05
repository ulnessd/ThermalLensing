import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import linregress


class DataPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")

        # Create a button to load data
        self.load_button = tk.Button(root, text="Load Data", command=self.load_data)
        self.load_button.pack()

        # Canvas for plotting
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        # Label to display fit results
        self.results_label = tk.Label(root, text="")
        self.results_label.pack()

        # Variables to store click and release positions
        self.click_x = None
        self.release_x = None

        # Bind the mouse click and release events
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def load_data(self):
        # File dialog to choose a data file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path)
            self.plot_data(self.data['Frame'], self.data['Area'])

    def plot_data(self, x, y, highlight_region=None, rescale=False):
        self.ax.clear()
        self.ax.plot(x, y, label="Data", marker='o', linestyle='-')
        if highlight_region is not None and highlight_region.any():
            self.ax.plot(x[highlight_region], y[highlight_region], 'r', linewidth=2, label='Selected Region')
            if rescale:
                # Rescale plot to the selected region
                min_x = min(x[highlight_region])
                max_x = max(x[highlight_region])
                self.ax.set_xlim(min_x, max_x)
        self.ax.set_title('Area vs Frame')
        self.ax.set_xlabel('Frame (Time)')
        self.ax.set_ylabel('Area (Cross-sectional Area)')
        self.ax.legend()
        self.canvas.draw()

    def on_click(self, event):
        self.click_x = event.xdata

    def on_release(self, event):
        self.release_x = event.xdata
        if self.click_x and self.release_x:
            self.select_region()

    def select_region(self):
        # Find indices for the selected range
        start_index = int(min(self.click_x, self.release_x))
        end_index = int(max(self.click_x, self.release_x))
        region = (self.data['Frame'] >= start_index) & (self.data['Frame'] <= end_index)

        # Re-plot the data with the selected region highlighted and rescale the plot
        self.plot_data(self.data['Frame'], self.data['Area'], region, rescale=True)

        # Fit the data within the selected region
        slope, intercept, r_value, p_value, std_err = linregress(self.data['Frame'][region], self.data['Area'][region])
        self.results_label.config(text=f"Slope: {slope:.2f}, Intercept: {intercept:.2f}, R-squared: {r_value ** 2:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataPlotterApp(root)
    root.mainloop()
