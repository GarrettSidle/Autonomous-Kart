# from camera import *
from spline import getSpline
from car_control import get_controls
from graph import graph

# camera_init()


# while(True):
#     cones = get_cones()

cones = [(3, 1), (-3, 1), (3, 4), (-3, 4),(3, 7), (-3, 7),(3, 10), (-3, 10)] 

cones =  [
    (-6, 0 ),(-6.5 ,  1),(-7, 2),(-7.5, 3),(-8.5, 4),(-9.5, 5),
    (3, 0 ),(2.5 ,  1),(2, 2),(1.5, 3),(.5, 4),(-.5, 5),
]



splines, spline_values, cone_values = getSpline(cones)

controls = get_controls(splines, cone_values)
graph(spline_values, cone_values, controls)