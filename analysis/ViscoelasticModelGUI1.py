import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv


simulation_results = {}
def run_simulation():
    try:
        # Retrieve parameters from GUI and convert them as necessary
        amplitude = inputs["Amplitude"].get()
        gamma = inputs["Gamma"].get()
        initial_omega = inputs["Omega_0"].get()
        k_ratio = inputs["K ratio"].get()
        offset = inputs["Offset"].get()
        t_0 = inputs["t_0"].get()
        v_0 = inputs["V_0"].get()
        dt = 0.002  # Assuming a fixed dt for simplicity
        total_time = 1  # Assuming a fixed total_time for simplicity

        # Call the simulation function with these parameters
        t, x = simulate_variable_frequency_offset_volume(amplitude, gamma, initial_omega, offset, k_ratio, dt, total_time)

        # Apply t_0 and filter data
        valid_indices = t >= t_0
        t = t[valid_indices] - t_0  # Adjust time series to start from t_0
        x = x[valid_indices]

        # Update the plot with new data
        fig_volume_change.clear()  # Clear previous figures
        ax_volume_change = fig_volume_change.add_subplot(111)
        ax_volume_change.plot(t, x)
        ax_volume_change.set_title('Volume Change Over Time')
        ax_volume_change.set_xlabel('Time (s)')
        ax_volume_change.set_ylabel('Volume Change (mm³)')
        canvas_volume_change.draw()  # Redraw the canvas

        # Calculate and plot cumulative volume adjusted with V_0
        integral_x = np.cumsum(x) * dt + v_0  # Start cumulative sum from V_0
        fig_cumulative_volume.clear()  # Clear previous figures
        ax_cumulative_volume = fig_cumulative_volume.add_subplot(111)
        ax_cumulative_volume.plot(t, integral_x)
        ax_cumulative_volume.set_title('Cumulative Volume Over Time')
        ax_cumulative_volume.set_xlabel('Time (s)')
        ax_cumulative_volume.set_ylabel('Cumulative Volume (mm³*s)')
        canvas_cumulative_volume.draw()  # Redraw the canvas

        global simulation_results
        simulation_results['t'] = t
        simulation_results['x'] = x
        simulation_results['dt'] = dt
        simulation_results['v_0'] = v_0

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, show this error in the GUI




# Connect this function to the Run Simulation button



# You can adjust this simulation function based on the specifics of the damping, frequency decay, and other factors.
def simulate_variable_frequency_offset_volume(amplitude, gamma, initial_omega, offset, k_ratio, dt, total_time):
    """
    Simulate the volume change with variable frequency based on the sign of volume change,
    including an offset, and handle frequency decay using a variable k ratio.

    Parameters:
    - amplitude: Initial volume change (amplitude).
    - gamma: Damping coefficient.
    - initial_omega: Initial angular frequency for x >= 0.
    - offset: Constant offset added to the volume.
    - k_ratio: Ratio of stiffness when x < 0 compared to x >= 0.
    - dt: Time step for the simulation.
    - total_time: Total time to simulate.

    Returns:
    - t: Time array.
    - x: Volume change array (including offset).
    """
    n = int(total_time / dt)
    t = np.linspace(0, total_time, n)
    x = np.zeros(n)
    x[0] = amplitude  # Start from just the amplitude
    v_half = -0.5 * dt * (initial_omega**2 * x[0] + gamma * 0)  # Initial v_half calculation

    for i in range(1, n):
        omega_squared = (initial_omega**2 if x[i-1] >= 0 else k_ratio * initial_omega**2)
        x[i] = x[i-1] + dt * v_half
        v_new = v_half - dt * (omega_squared * x[i] + gamma * v_half)
        v_half = v_new - 0.5 * dt * (omega_squared * x[i] + gamma * v_new)

    return t, x + offset  # Apply offset here for final display


# You can adjust this simulation function based on the specifics of the damping, frequency decay, and other factors.



from tkinter import filedialog

def dump_png():
    # Open a save file dialog to choose the base filename
    base_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[("PNG files", "*.png")], title="Save Plots")
    if base_path:
        # Determine the full filenames with suffixes for each plot
        volume_change_path = base_path.replace('.png', '_dV.png')
        cumulative_volume_path = base_path.replace('.png', '_Vol.png')

        # Save the current volume change plot to a PNG file at 600 dpi
        fig_volume_change.savefig(volume_change_path, dpi=600)


        # Save the current cumulative volume plot to a PNG file at 600 dpi
        fig_cumulative_volume.savefig(cumulative_volume_path, dpi=600)



def dump_csv():
    t = simulation_results['t']
    x = simulation_results['x']
    dt = simulation_results['dt']
    v_0 = simulation_results['v_0']
    cumulative_volume = np.cumsum(x) * dt + v_0
    # Open a save file dialog to choose where to save the CSV
    csv_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")], title="Save CSV")
    if csv_path:
        # Open the file in write mode
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['Time', 'Change in Volume', 'Cumulative Volume'])
            # Write the data
            cumulative_volume = np.cumsum(x) * dt + v_0  # Assuming x, dt, v_0 are accessible
            for t_val, x_val, cum_val in zip(t, x, cumulative_volume):
                writer.writerow([t_val, x_val, cum_val])

def quit_app():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Oscillator Model Simulation")

# Create frames for organization
frame_inputs = ttk.Frame(root, padding="3 3 12 12")
frame_inputs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
frame_plots = ttk.Frame(root, padding="3 3 12 12")
frame_plots.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

# Define and place input widgets
inputs = {
    "Amplitude": tk.DoubleVar(value=10),
    "Gamma": tk.DoubleVar(value=6),
    "Omega_0": tk.DoubleVar(value=25),
    "K ratio": tk.DoubleVar(value=10),
    "Offset": tk.DoubleVar(value=1.8),
    "t_0": tk.DoubleVar(value=0),
    "V_0": tk.DoubleVar(value=0)
}

row = 0
for name, var in inputs.items():
    ttk.Label(frame_inputs, text=name).grid(column=0, row=row)
    ttk.Entry(frame_inputs, textvariable=var).grid(column=1, row=row)
    row += 1

# Buttons
ttk.Button(frame_inputs, text="Run Simulation", command=run_simulation).grid(column=0, row=row)
ttk.Button(frame_inputs, text="Dump PNG", command=dump_png).grid(column=1, row=row)
ttk.Button(frame_inputs, text="Dump CSV", command=dump_csv).grid(column=1, row=row+1)  # Adjust grid positioning as needed
ttk.Button(frame_inputs, text="Quit", command=quit_app).grid(column=2, row=row)

# Canvases for plotting
fig_volume_change = plt.Figure(figsize=(5, 4), dpi=100)
fig_cumulative_volume = plt.Figure(figsize=(5, 4), dpi=100)
canvas_volume_change = FigureCanvasTkAgg(fig_volume_change, master=frame_plots)
canvas_volume_change.get_tk_widget().grid(row=0, column=0)
canvas_cumulative_volume = FigureCanvasTkAgg(fig_cumulative_volume, master=frame_plots)
canvas_cumulative_volume.get_tk_widget().grid(row=0, column=1)

root.mainloop()
