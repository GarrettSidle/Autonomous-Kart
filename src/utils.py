import json
import numpy as np
import os

# Get the absolute path to the directory where the script lives
script_dir = os.path.dirname(os.path.abspath(__file__))

# Join it with your config file (whether it's in the same folder or in a subfolder like 'config')
config_path = os.path.join(script_dir, 'settings.json')  # or just 'settings.json' if in same folder

# Load the JSON config
with open(config_path, 'r') as file:
    config = json.load(file)


# Open and load the JSON config file
with open(config_path, 'r') as file:
    config = json.load(file)
HEADLESS                = config["headless"]
DISTANCE_TO_STEAR_ANGLE = config["steer-angle"]
DISTANCE_TO_BRAKE       = config["brake-distance"]
SPEED_SENSITIVITY       = config["speed-sensitivity"]

#reflector
REFLECT_LOWER_RANGE     = np.array(config["reflect-lower-range"])
REFLECT_UPPER_RANGE     = np.array(config["reflect-upper-range"])

#yellow housing
HOUSING_LOWER_RANGE     = np.array(config["housing-lower-range"])
HOUSING_UPPER_RANGE     = np.array(config["housing-upper-range"]) 
