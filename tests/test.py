import numpy as np
from scipy.spatial import KDTree
from sklearn.cluster import KMeans
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

from test_values import cones_set , cone_values_set, spline_values_set, controls_set
import graph


def separate_points(points):
    # Convert the points to a numpy array if they aren't already
    points = np.array(points)
    
    # Use KMeans to cluster the points into two clusters
    kmeans = KMeans(n_clusters=2, random_state=0)
    kmeans.fit(points)
    
    # Get the labels assigned to each point by KMeans
    labels = kmeans.labels_
    
    # Separate the points into two arrays based on their labels
    line1_points = points[labels == 0]
    line2_points = points[labels == 1]
    
    return line1_points, line2_points

# Create figure and axis
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(8, 6))

def update_plot(left, right):
    ax.clear()  # Clear previous data

    # Extract x and y values
    left_cone_x_values, left_cone_y_values = zip(*left)
    right_cone_x_values, right_cone_y_values = zip(*right)

    # Plot data
    ax.scatter(left_cone_x_values, left_cone_y_values, color='blue', label='Left Cones')
    ax.scatter(right_cone_x_values, right_cone_y_values, color='orange', label='Right Cones')

    # Formatting
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title("Dynamic Cone Positioning and Centerline Estimation")
    ax.legend()
    ax.grid(True)

    plt.draw()
    plt.pause(0.1)  # Pause to allow GUI to update


for i in range(len(cones_set)):
    if(i == 0):
        continue
    if(len(cones_set[i]) == 0):
        continue
    

    left, right = separate_points(cones_set[i])
    
    update_plot(left, right)
    time.sleep(10)
    
plt.ioff()  # Turn off interactive mode after updates
plt.show()
    
    
    
    
    
    
    
    
print("Left Cones:", left)
print("Right Cones:", right)
print("Estimated Centerline:", centerline)