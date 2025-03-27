import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import math

def find_track_contours(cones):
    def find_start_cone(isLeft):
        #find the closest cone for given side
        curr_start = (100, 100)
        for cone in cones:
            #if the cone is on the right and we are looking for left
            if(cone[0] > 0 and isLeft):
                continue 
            #if the cone is on the left and we are looking for right
            if(cone[0] < 0 and  not isLeft):
                continue 
                
        
            if(cone[1] < curr_start[1]):
                curr_start = cone
        return curr_start
    
    def findConeDistances():
    
        unclaimed_cones = []
        
        for cone in cones:
            x1, y1 = left_start
            x2, y2 = cone
            left_distance =  math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            x1, y1 = right_start
            right_distance =  math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            
            
            coneWithDistance = (cone[0], cone[1], left_distance, right_distance)
            
            unclaimed_cones.append(coneWithDistance)
        return unclaimed_cones
    def sortCandidates(arr, index):

        # Create a list of (value, original_index) pairs
        indexed_tuples = [(t, i) for i, t in enumerate(arr)]

        # Sort the list based on the 3rd element of the tuples
        indexed_tuples.sort(key=lambda item: item[0][index])

        # Extract the original indices
        original_indices = [index for _, index in indexed_tuples]

        return original_indices[::-1]
    
    def find_next_candidate(isLeft ):
        
        while(1):
            
            if(isLeft and len(left_candidates) == 0):
                return None
            if((not isLeft) and len(right_candidates) == 0):
                return None
            
            if(isLeft):
                closest = left_candidates.pop()
            else:
                closest = right_candidates.pop()
            
            #if the cone has been claimed
            if(unclaimed_cones[closest] == None):
                continue
            
            
            return closest
    def designateSides(unclaimed_cones, left_candidates, right_candidates):
        right_cones = []
        left_cones  = []
        
        remaining = len(unclaimed_cones)
        
        while(remaining > 0 ):
            
            left_candidate  = find_next_candidate(True )
            right_candidate = find_next_candidate(False)
            
            
            #if they both want the same cone
            if(left_candidate == right_candidate):
                if(left_candidate == None):
                    break
                
                #if the left distance is shorter
                if(unclaimed_cones[left_candidate][2] < unclaimed_cones[left_candidate][3]):
                    #find right a new candidate
                    right_candidate = find_next_candidate(False)
                else:
                    left_candidate = find_next_candidate(True)
            
            
                    
            if(left_candidate):
            
                remaining -= 1
                left_cones.append(unclaimed_cones[left_candidate])
                unclaimed_cones[left_candidate] = None 
            
            if(right_candidate):   
                remaining -= 1
                right_cones.append(unclaimed_cones[right_candidate])
                unclaimed_cones[right_candidate] = None 
        return left_cones, right_cones

    def graph(left_cones, right_cones):
        # Separate x and y coordinates for right cones
        right_cones_x = [point[0] for point in right_cones]
        right_cones_y = [point[1] for point in right_cones]

        # Separate x and y coordinates for left cones
        left_cones_x = [point[0] for point in left_cones]
        left_cones_y = [point[1] for point in left_cones]

        # Create the plot
        plt.figure(figsize=(8, 6))

        plt.scatter(right_cones_x, right_cones_y, color='blue', label='Right Cones')
        plt.scatter(left_cones_x, left_cones_y, color='red', label='Left Cones')

        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.title("Plot of Right and Left Cones")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    
    #find the first cone on our right and left
    right_start= find_start_cone(False)
    left_start = find_start_cone(True)

    #create a list of all cones and there distances to the start cone
    unclaimed_cones= findConeDistances()
    
    
    #create an array in order from closest to farthest from start cone
    left_candidates = sortCandidates(unclaimed_cones, 2)
    right_candidates = sortCandidates(unclaimed_cones, 3)
    

    left_cones, right_cones = designateSides(unclaimed_cones, left_candidates, right_candidates)

    graph(left_cones, right_cones)

            

cones = [(3, 1), (-3, 1), (3, 4), (-3, 4),(3, 7), (-3, 7),(3, 10), (-3, 10)]  # Cones in a straight lan

# Call the function with interval of 0.5 units
find_track_contours(cones)

cones =  [
    (-6, 0 ),(-6.5 ,  1),(-7, 2),(-7.5, 3),(-8.5, 4),(-9.5, 5),(-11, 6),
    (3, 0 ),(2.5 ,  1),(2, 2),(1.5, 3),(.5, 4),(-.5, 5),(-2, 6),
]

find_track_contours(cones)
