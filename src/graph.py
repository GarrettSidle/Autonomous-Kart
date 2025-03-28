import matplotlib.pyplot as plt
import numpy as np

#Should return a graph of 
# left and right spline, X
# all cones and their side, X
# show distance to brake      X
# show current state of brake  X
# show curviness factor
# show current speed        
# current stearing angle    x


DISTANCE_TO_BRAKE = 2.5
STEARING_ARROW_LENGTH = 5


plt.figure(figsize=(8, 6))


def graph(spline_values, cone_values, controls):
    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    left_spline_values, right_spline_values  = spline_values
    
    left_spline_x_values , left_spline_y_values = left_spline_values
    right_spline_x_values, right_spline_y_values  = right_spline_values
    
    stearing_angle, throttle, brake = controls
    
    print(f"Steering Angle: {stearing_angle}°, Throttle: {throttle}, Brake: {brake}")
    
        
    plt.clf()
    
    plt.scatter(right_cones_x, right_cones_y, color='blue', label='Right Cones')
    plt.scatter(left_cones_x, left_cones_y, color='orange', label='Left Cones')
    
    
    # Convert the angle from degrees to radians
    angle_rad = np.radians(stearing_angle)

    # Calculate the endpoint based on the length and angle
    x_end = STEARING_ARROW_LENGTH * np.sin(angle_rad)
    y_end = STEARING_ARROW_LENGTH * np.cos(angle_rad)

    
    # Plot the vector from (0, 0) to the calculated endpoint
    plt.arrow(0, 0, x_end, y_end, head_width=0.1, head_length=0.1, fc='purple', ec='purple', label=f'{stearing_angle}°')
    
    
    
    # Plot splines
    plt.plot(left_spline_x_values , left_spline_y_values , color='orange' , linestyle='-', label='Left Spline')
    plt.plot(right_spline_x_values, right_spline_y_values, color='blue', linestyle='-', label='Right Spline')
    
    brake_color = 'green' if brake else 'red'
    plt.plot([0, 0], [0, DISTANCE_TO_BRAKE], color=brake_color, linestyle='-')
    
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("Spline Plot of Right and Left Cones")
    plt.legend()
    plt.grid(True)
    plt.show()
    