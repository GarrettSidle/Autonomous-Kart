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


DISTANCE_TO_BRAKE = 2
STEARING_ARROW_LENGTH = 2.5


plt.ion()  # Enable interactive mode
fig, ax = plt.subplots(figsize=(8, 6))




def graph(spline_values, cone_values, controls):
    
    left_cone, right_cone  = cone_values
    
    left_cones_x , left_cones_y  = left_cone
    right_cones_x, right_cones_y = right_cone
    
    left_spline_values, right_spline_values  = spline_values
    
    left_spline_x_values , left_spline_y_values = left_spline_values
    right_spline_x_values, right_spline_y_values  = right_spline_values
    
    stearing_angle, throttle, brake = controls
    
    print(f"Steering Angle: {stearing_angle}°, Throttle: {throttle}, Brake: {brake}")
    
        
    ax.clear()  # Clear previous frame
    
    ax.scatter(right_cones_x, right_cones_y, color='blue', label='Right Cones')
    ax.scatter(left_cones_x, left_cones_y, color='orange', label='Left Cones')
    
    
    # Convert the angle from degrees to radians
    angle_rad = np.radians(stearing_angle)

    # Calculate the endpoint based on the length and angle
    x_end = STEARING_ARROW_LENGTH * np.sin(angle_rad)
    y_end = STEARING_ARROW_LENGTH * np.cos(angle_rad)

    

    ax.arrow(0, 0, x_end, y_end, head_width=0.1, head_length=0.1, fc='purple', ec='purple', label=f'{stearing_angle}°')

    # Plot splines
    ax.plot(left_spline_x_values, left_spline_y_values, color='orange', linestyle='-', label='Left Spline')
    ax.plot(right_spline_x_values, right_spline_y_values, color='blue', linestyle='-', label='Right Spline')

    brake_color = 'green' if brake else 'red'
    ax.plot([0, 0], [0, DISTANCE_TO_BRAKE], color=brake_color, linestyle='-')

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Spline Plot of Right and Left Cones")
    ax.legend()
    ax.grid(True)

    plt.draw() 
    plt.pause(0.1)  
    