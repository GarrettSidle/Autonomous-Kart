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

from pathlib import Path

camera.camera_init()

while(1):
    
    cones = camera.get_cones(True, image_path = Path(__file__).resolve().parent.parent / "test_images" / "test.jpg")

    #create a spline for the left and right barriers
    spline_values, cone_values = spline.getSpline(cones)

    #calculate the kart controls 
    controls = car_control.get_controls(cone_values)
    
    #graph and display the values
    graph.graph(spline_values, cone_values, controls)
    
    
