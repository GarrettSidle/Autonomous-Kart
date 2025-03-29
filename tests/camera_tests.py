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

camera.camera_init()

#implement photos to test camera module on

while(True):
    cones = camera.get_cones()
