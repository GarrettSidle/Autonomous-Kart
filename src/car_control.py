import numpy as np
import math

from utils import DISTANCE_TO_STEAR_ANGLE, DISTANCE_TO_BRAKE, SPEED_SENSITIVITY

def get_controls(cone_values):
    
    
    stearing_angle = find_stearing_angle(cone_values)
    
    throttle       = find_speed(cone_values)
    
    brake          = find_brake(cone_values)
    
    if(brake ):
        throttle = 0
    
    return stearing_angle, throttle, brake


def find_x_given_y(y_value, x_coords, y_coords):
    
    sorted_pairs = sorted(zip(x_coords, y_coords))
    x_coords, y_coords = zip(*sorted_pairs)  # Unzip back into separate lists
    
    
    below_x = None
    above_x = None
    
    # Iterate over the y values and find the closest points
    for i in range(1, len(y_coords)):
        if y_coords[i] >= y_value:
            above_x = x_coords[i]
            below_x = x_coords[i - 1]
            break

    # If closest points are found, return the average
    if below_x is not None and above_x is not None:
        return (below_x + above_x) / 2
    else:
        return 0  # In case no valid points are found



def find_y_given_x(x_value, x_coords, y_coords):
    sorted_pairs = sorted(zip(x_coords, y_coords))
    x_coords, y_coords = zip(*sorted_pairs)  # Unzip back into separate lists
    
    below_x, below_y = None, None
    above_x, above_y = None, None
    
    
    # Find the closest points above and below x_value
    for i in range(1, len(x_coords)):
        if x_coords[i] >= x_value:
            above_x, above_y = x_coords[i], y_coords[i]
            below_x, below_y = x_coords[i - 1], y_coords[i - 1]
            break

    # If we found two valid points, calculate the y-intercept
    if below_x is not None and above_x is not None and below_x != above_x:
        m = (above_y - below_y) / (above_x - below_x)  # Slope
        b = below_y - m * below_x  # y-intercept
        return b
    
    return 100 # Return None if no valid points were found

def find_stearing_angle(cone_values):
    
    
    left_cones, right_cones  = cone_values

    
    left_x_at_y = 0        
    right_x_at_y= 0
    if len(left_cones[0]) != 0:
        left_x_at_y  = find_x_given_y(DISTANCE_TO_STEAR_ANGLE, left_cones[0], left_cones[1])
    if len(right_cones[0]) != 0:
        right_x_at_y = find_x_given_y(DISTANCE_TO_STEAR_ANGLE, right_cones[0], right_cones[1])
    
    mid_point_x = (right_x_at_y + left_x_at_y) / 2
    
    angle_radian = math.atan(mid_point_x / DISTANCE_TO_STEAR_ANGLE)
    
    
    angle =  math.degrees(angle_radian)
    return angle
    
def find_speed(cone_values):
    
    
    curviness = ((calculate_curviness(cone_values[1][0],cone_values[1][1]) + calculate_curviness(cone_values[0][0],cone_values[0][1])))/2
    out = curviness * SPEED_SENSITIVITY
    if(out > 1):
        out = 1
    
    return 1 - out
    
def calculate_curviness(x, y):
    if len(x) < 3 or len(y) < 3 or len(x) != len(y):
        return 0  # Need at least 3 points to measure curvature

    angles = []

    for i in range(1, len(x) - 1):
        p1 = np.array([x[i - 1], y[i - 1]])
        p2 = np.array([x[i], y[i]])
        p3 = np.array([x[i + 1], y[i + 1]])

        # Compute vectors
        v1 = p2 - p1
        v2 = p3 - p2

        # Compute angle between vectors
        dot_product = np.dot(v1, v2)
        magnitude = np.linalg.norm(v1) * np.linalg.norm(v2)

        if magnitude == 0:
            continue  # Avoid division by zero

        cos_theta = np.clip(dot_product / magnitude, -1, 1)
        angle = np.arccos(cos_theta)  # Angle in radians

        angles.append(angle)

    if not angles:
        return 0  # No valid angles found

    # Sum absolute angles and normalize
    total_curvature = sum(angles) / (len(x) - 2)
    max_possible_curvature = np.pi  # Theoretical max per turn

    return min(total_curvature / max_possible_curvature, 1)

def find_brake(cone_values):

    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    left_y_at_0  = 100
    right_y_at_0 = 100

    if len(left_cones_x) != 0:
        left_y_at_0 = find_y_given_x(0, left_cones_x, left_cones_y)


    if len(right_cones_x) != 0:
        right_y_at_0 = find_y_given_x(0, right_cones_x, right_cones_y)
        
        
    closest_wall = min(left_y_at_0, right_y_at_0)
    
    return (closest_wall <= DISTANCE_TO_BRAKE)