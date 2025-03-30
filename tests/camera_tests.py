import sys
import os
import matplotlib.pyplot as plt
import time

# Get the absolute path to the src directory
module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(module_dir)

# Import camera module
import camera
import spline
import car_control
import graph

camera.camera_init()

plt.ion()
fig, ax = plt.subplots()

#implement photos to test camera module on

while(True):
    cones = camera.get_cones()
    print(cones)
    
    
    ax.clear()  # Clear previous points
    x_coords, y_coords = zip(*cones) if cones else ([], [])  # Handle empty case

    ax.scatter(x_coords, y_coords, color='blue', label='Points')
    
    # Set axis limits
    ax.set_xlim(-10, 10)
    ax.set_ylim(0, 10)

    # Labels and grid
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Live Coordinate Updates')
    ax.grid(True)
    
    plt.draw()
    plt.pause(0.1)  # Pause for a brief moment to update the figure
