import numpy as np
from scipy.interpolate import interp1d
import math


def getSpline(cones):
    
    
    #find the first cone on our right and left
    right_start= find_start_cone(False, cones)
    left_start = find_start_cone(True, cones)
    
    


    #create a list of all cones and there distances to the start cone
    unclaimed_cones= findConeDistances(cones, left_start, right_start)
    
    #create an array in order from closest to farthest from start cone
    left_candidates = sortCandidates(unclaimed_cones, 2)
    right_candidates = sortCandidates(unclaimed_cones, 3)
    
    left_cones, right_cones = designateSides(unclaimed_cones, left_candidates, right_candidates, left_start, right_start)

    splines, spline_values, cone_values = calculate_splines(left_cones, right_cones)

    
    return splines, spline_values, cone_values
    


def find_start_cone(isLeft, cones):
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
            
            
    
    curr_start = (curr_start[0], 0)
    
    if(curr_start[0] == 100):
        curr_start = (0,0)
    
    cones.append(curr_start)
    return curr_start

def findConeDistances(cones, left_start, right_start):

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

def find_next_candidate(unclaimed_cones, candidates):
    
    while(1):
        
        if(len(candidates) == 0):
            return None
        
        closest = candidates.pop()
        
        #if the cone has been claimed
        if(unclaimed_cones[closest] == None):
            continue
        
        return closest
    
def designateSides(unclaimed_cones, left_candidates, right_candidates, left_start, right_start):
    right_cones = []
    left_cones  = []
    
    remaining = len(unclaimed_cones)
    
    while(remaining > 0 ):
        
        left_candidate  = find_next_candidate(unclaimed_cones, left_candidates)
        right_candidate = find_next_candidate(unclaimed_cones, right_candidates)
        
        
        #if they both want the same cone
        if(left_candidate == right_candidate):
            if(left_candidate == None):
                break
            
            x1, y1 = left_start
            x2, y2, _, _ = unclaimed_cones[left_candidate]
            left_distance =  math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            x1, y1 = right_start
            right_distance =  math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            #if the left distance is shorter
            if(left_distance < right_distance):
                #find right a new candidate
                right_candidate = None
            else:
                left_candidate = None
        
        
                
        if(left_candidate):
        
            remaining -= 1
            left_cones.append(unclaimed_cones[left_candidate])
            unclaimed_cones[left_candidate] = None 
        
        if(right_candidate):   
            remaining -= 1
            right_cones.append(unclaimed_cones[right_candidate])
            unclaimed_cones[right_candidate] = None 
            
    return left_cones, right_cones

def calculate_splines(left_cones, right_cones):
    # Separate and sort x and y coordinates for right cones
    right_cone_x_values = [cone[0] for cone in right_cones]
    right_cone_y_values = [cone[1] for cone in right_cones]

    # Separate and sort x and y coordinates for left cones
    left_cone_x_values = [cone[0] for cone in left_cones]
    left_cone_y_values = [cone[1] for cone in left_cones]
    
    # Create splines for left and right cones
    left_spline  = None
    right_spline = None
    print(left_cone_x_values, left_cone_y_values)
    if len(left_cone_x_values) > 2 and len(set(left_cone_x_values)) == len(left_cone_x_values):
        left_spline = interp1d(left_cone_x_values, left_cone_y_values)
        left_spline_x_values = np.linspace(min(left_cone_x_values), max(left_cone_x_values), 100)
        left_spline_y_values = left_spline(left_spline_x_values)
    else:
        left_spline_x_values, left_spline_y_values = left_cone_x_values, left_cone_y_values

    if len(right_cone_x_values) > 2 and len(set(right_cone_x_values)) == len(right_cone_x_values):
        right_spline = interp1d(right_cone_x_values, right_cone_y_values)
        right_spline_x_values = np.linspace(min(right_cone_x_values), max(right_cone_x_values), 100)
        right_spline_y_values = right_spline(right_spline_x_values)
    else:
        right_spline_x_values, right_spline_y_values = right_cone_x_values, right_cone_y_values
        
    splines = (left_spline, right_spline)
    spline_values = (
        (left_spline_x_values , left_spline_y_values),
        (right_spline_x_values, right_spline_y_values))
    cone_values = (
        (left_cone_x_values , left_cone_y_values),
        (right_cone_x_values, right_cone_y_values))
    
        
    return splines, spline_values, cone_values