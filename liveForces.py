import matplotlib.pyplot as plt
import numpy as np
import time
import os
import re
from collections import deque

# Constants
INTERVAL = 1.0
FILE_NAME = "postProcessing/forces/0/forces.dat"
MAX_POINTS = 1000  # Maximum number of points on the plot

def find_file(filename):
    """Search for file in multiple locations"""
    # Check in current directory
    if os.path.exists(filename):
        return filename
    
    # Check in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, filename)
    if os.path.exists(script_path):
        return script_path
    
    # Check in parent directory
    parent_dir = os.path.dirname(script_dir)
    parent_path = os.path.join(parent_dir, filename)
    if os.path.exists(parent_path):
        return parent_path
    
    # Check case-insensitive (Windows)
    if os.name == 'nt':  # Windows
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower() == filename.lower():
                    return os.path.join(root, file)
    
    return None

class ForcePlotter:
    def __init__(self):
        # Initialize plots
        plt.ion()  # Interactive mode
        self.fig, self.ax = plt.subplots(figsize=(10, 6))

        # Plot settings
        self.ax.set_title("Force")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("F, kN")
        self.ax.grid(True, alpha=0.3)

        # Data for the plot
        self.times = deque(maxlen=MAX_POINTS)
        self.forces = deque(maxlen=MAX_POINTS)

        # Plot line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)

         # Find the file
        self.file_path = find_file(FILE_NAME)

        # Variable for tracking the last read position
        self.last_position = 0
        self.file_size = 0

        # Check if file exists
        if os.path.exists(self.file_path):
            self.file_size = os.path.getsize(self.file_path)
            #self.last_position = self.file_size

        # Initial file reading
        self.read_new_data()
        self.update_plot()

        plt.show()

    def read_new_data(self):
        """Read new data from the file"""
        try:
            if not os.path.exists(self.file_path):
                return

            current_size = os.path.getsize(self.file_path)

            # If the file was truncated (became smaller), read from the beginning
            if current_size < self.last_position:
                self.last_position = 0
                self.times.clear()
                self.forces.clear()

            # If there is new data
            if current_size >= self.last_position:
                with open(self.file_path, 'r') as file:
                    file.seek(self.last_position)
                    new_data = file.read()

                    # Update position
                    self.last_position = current_size

                    # Process lines
                    lines = new_data.split('\n')
                    for line in lines:
                        # Skip empty lines
                        if not line.strip():
                            continue

                        if line[0]=='#':
                             continue

                        # Remove all types of brackets: (), [], {}
                        line = re.sub(r'[\(\)\[\]\{\}]', '', line)
                         # Remove multiple spaces and trim
                        line = re.sub(r'\s+', ' ', line).strip()

                        # Try to extract data
                        try:
                            parts = line.strip().split()

                            if len(parts) >= 5:
                                # Parse values (handling scientific notation)
                                iter_num = float(parts[0])
                                second_val = float(parts[1])
                                fifth_val = float(parts[4])

                                # Calculate time and force
                                time_val = iter_num * INTERVAL
                                force_val = second_val + fifth_val

                                self.times.append(time_val)
                                self.forces.append(force_val)

                        except (ValueError, IndexError):
                            # Skip lines that couldn't be parsed
                            continue

        except Exception as e:
            print(f"Error reading file: {e}")

    def update_plot(self):
        """Update the plot"""
        if len(self.times) > 0:
            # Convert deque to list for plotting
            times_list = list(self.times)
            forces_list = list(self.forces)

            # Update line data
            self.line.set_data(times_list, forces_list)

            # Auto-scale axes
            self.ax.relim()
            self.ax.autoscale_view()

            # Update title with point count
            self.ax.set_title(f"Force (N={len(times_list)})")

            # Redraw the plot
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def run(self):
        """Main program loop"""
        try:
            while True:
                self.read_new_data()
                self.update_plot()
                time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\nProgram stopped by user")
        finally:
            plt.close('all')

# Run the program
if __name__ == "__main__":
    plotter = ForcePlotter()
    plotter.run()



