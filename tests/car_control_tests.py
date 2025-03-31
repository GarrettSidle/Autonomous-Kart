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



from test_values import cone_values_set

for i in range(len(cone_values_set)):
    
    try:
        cone_values = cone_values_set[i]

        controls = car_control.get_controls(cone_values)
        print(controls)
        
    except Exception as e:
        print(f"failed on test {i}: {e}")
    