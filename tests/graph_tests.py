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


from test_values import cone_values_set, spline_values_set, controls_set

for i in range(len(cone_values_set)):
    
    try:
        
        cone_values = cone_values_set[i]
        spline_values = spline_values_set[i]
        controls = controls_set[i]

        graph.graph(spline_values, cone_values, controls)
        time.sleep(5)
        
    except:
        print(f"failed on test {i}")