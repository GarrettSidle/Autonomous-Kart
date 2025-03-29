import sys
import os
import time

# Get the absolute path to the src directory
module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(module_dir)

# Import camera module
import camera
import spline
import car_control
import graph

from test_values import cones_set

for i in range(len(cones_set)):
    
    try:
        cones = cones_set[i]

        #create a spline for the left and right barriers
        splines, spline_values, cone_values = spline.getSpline(cones)

        #calculate the kart controls 
        controls = car_control.get_controls(splines, cone_values)
        
        #graph and display the values
        graph.graph(spline_values, cone_values, controls)
        
        time.sleep(5)
    except:
        print(f"failed on test {i}")
    