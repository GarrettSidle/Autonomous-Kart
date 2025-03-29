import sys
import os

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
    
        print(spline.getSpline(cones))
        
    except:
        print(f"failed on test {i}")