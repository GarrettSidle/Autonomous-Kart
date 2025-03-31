from camera import *
from spline import getSpline
from car_control import get_controls
from graph import graph



camera_init()


while(True):
    #find all cones in the cameras vision
    cones = get_cones()

    #create a spline for the left and right barriers
    spline_values, cone_values = getSpline(cones)

    #calculate the kart controls 
    controls = get_controls(cone_values)
    
    #graph and display the values
    graph(spline_values, cone_values, controls)