import numpy as np
from scipy.interpolate import CubicSpline
import math
from scipy.optimize import root_scalar

def get_controls(splines, cone_values):
    
    
    stearing_angle = find_stearing_angle(splines, cone_values)
    
    throttle       = find_speed(splines, cone_values)
    
    brake          = find_brake(splines, cone_values)
    
    if(brake ):
        throttle = 0
    
    return stearing_angle, throttle, brake


def find_x_given_y(y_target, spline, x_range):
    def func(x):
        return spline(x) - y_target

    result = root_scalar(func, bracket=x_range, method='brentq')
    return result.root if result.converged else None

def find_y_given_x(x_target, spline, y_range):
    def func(y):
        return spline(y) - x_target
    
    result = root_scalar(func, bracket=y_range, method='brentq')
    return result.root if result.converged else None

def find_stearing_angle(splines, cone_values):
    
    DISTANCE_TO_STEAR_ANGLE = 3.5
    
    left_spline, right_spline  = splines
    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    
    
    left_x_at_y = 0        
    right_x_at_y= 0
    if left_spline is not None:
        left_x_at_y  = find_x_given_y(DISTANCE_TO_STEAR_ANGLE, left_spline, (min(left_cones_x), max(left_cones_x)))
    if right_spline is not None:
        right_x_at_y = find_x_given_y(DISTANCE_TO_STEAR_ANGLE, right_spline, (min(right_cones_x), max(right_cones_x)))
    
    mid_point_x = (right_x_at_y + left_x_at_y) / 2
    
    angle_radian = math.atan(mid_point_x / DISTANCE_TO_STEAR_ANGLE)
    
    
    angle =  np.degrees(angle_radian)
    
    return angle
    
def find_speed(splines, cone_values):
    SPEED_SENSITIVITY = 5
    
    
    left_spline, right_spline  = splines
    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    
    if left_spline is None or right_spline is None:
        return None
    
    # Generate y-values across the range of both splines
    y_values = np.linspace(min(left_spline.x[0], right_spline.x[0]), max(left_spline.x[-1], right_spline.x[-1]), 100)
    
    # Get the x-values of the middle spline (average of left and right splines at each y)
    mid_x_values = [(left_spline(y) + right_spline(y)) / 2 for y in y_values]
    
    # Create the middle spline
    middle_spline = CubicSpline(y_values, mid_x_values)
    
    # Calculate the first and second derivatives of the spline
    dx = middle_spline.derivative(1)
    ddx = middle_spline.derivative(2)
    
    # Calculate velocity (magnitude of first derivative) at each point
    velocity = np.sqrt(dx(y_values)**2 + ddx(y_values)**2)
    
    # Calculate curvature using the standard formula
    curvature = np.abs(ddx(y_values)) / (1 + dx(y_values)**2)**(3/2)
    
    # Normalize the curvature between 0 and 1
    max_curvature = np.max(curvature)
    normalized_curvature = curvature / max_curvature if max_curvature != 0 else curvature
    

    return 1 - (SPEED_SENSITIVITY * np.mean(normalized_curvature))

def find_brake(splines, cone_values):
    DISTANCE_TO_BRAKE = 2.5
    
    return True
    
    
    left_spline, right_spline  = splines
    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    left_x_at_0  = 100
    right_x_at_0 = 100

    # Check if the left spline is available
    if left_spline is not None:
        left_x_at_0 = find_y_given_x(0, left_spline, (0, max(left_cones_x)))

    # Check if the right spline is available
    if right_spline is not None:
        right_x_at_0 = find_y_given_x(0, right_spline, (0, max(right_cones_x)))
        
        
    closest_wall = min(left_x_at_0, right_x_at_0)
    
    return (closest_wall <= DISTANCE_TO_BRAKE)