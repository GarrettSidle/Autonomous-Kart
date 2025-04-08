import cv2
import depthai as dai
import numpy as np
import math



from utils import HEADLESS, HOUSING_LOWER_RANGE, HOUSING_UPPER_RANGE, REFLECT_LOWER_RANGE, REFLECT_UPPER_RANGE



THRESHOLD    = 80

HORIZONTAL_FOV = 150 
FRAME_WIDTH = 640    
CENTER_X = FRAME_WIDTH / 2 

pipeline = None
cam = None
mono_left = None
mono_right = None
depth = None
xout_video = None
xout_depth = None

device = None

# Define kernel for morphological operations
kernel = np.ones((7,7), np.uint8) 


def camera_init():
    global pipeline, cam, mono_left, mono_right, depth, xout_depth, xout_video, device
    
    if(not HEADLESS):
        # Create OpenCV Trackbars for HSV tuning with default values for orange/yellow
        cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)  
        cv2.resizeWindow("Trackbars", 640, 300)  
        cv2.createTrackbar("Reflector H Min", "Trackbars", REFLECT_LOWER_RANGE[0], 180, update_hsv)
        cv2.createTrackbar("Reflector S Min", "Trackbars", REFLECT_LOWER_RANGE[1], 255, update_hsv)
        cv2.createTrackbar("Reflector V Min", "Trackbars", REFLECT_LOWER_RANGE[2], 255, update_hsv)
        cv2.createTrackbar("Reflector H Max", "Trackbars", REFLECT_UPPER_RANGE[0], 180, update_hsv)
        cv2.createTrackbar("Reflector S Max", "Trackbars", REFLECT_UPPER_RANGE[1], 255, update_hsv)
        cv2.createTrackbar("Reflector V Max", "Trackbars", REFLECT_UPPER_RANGE[2], 255, update_hsv)
        
        cv2.createTrackbar("Housing H Min", "Trackbars", HOUSING_LOWER_RANGE[0], 180, update_hsv)
        cv2.createTrackbar("Housing S Min", "Trackbars", HOUSING_LOWER_RANGE[1], 255, update_hsv)
        cv2.createTrackbar("Housing V Min", "Trackbars", HOUSING_LOWER_RANGE[2], 255, update_hsv)
        cv2.createTrackbar("Housing H Max", "Trackbars", HOUSING_UPPER_RANGE[0], 180, update_hsv)
        cv2.createTrackbar("Housing S Max", "Trackbars", HOUSING_UPPER_RANGE[1], 255, update_hsv)
        cv2.createTrackbar("Housing V Max", "Trackbars", HOUSING_UPPER_RANGE[2], 255, update_hsv)
        
        cv2.createTrackbar("threshold", "Trackbars", THRESHOLD, 500, update_hsv)


    # Create DepthAI pipeline
    pipeline = dai.Pipeline()

    # Create color camera node
    cam = pipeline.create(dai.node.ColorCamera)
    cam.setPreviewSize(640, 480)
    cam.setInterleaved(False)
    cam.setFps(30)

    # Create MonoCamera nodes for stereo depth
    mono_left = pipeline.create(dai.node.MonoCamera)
    mono_right = pipeline.create(dai.node.MonoCamera)
    mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)
    mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

    # Create StereoDepth node
    depth = pipeline.create(dai.node.StereoDepth)
    depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    depth.setLeftRightCheck(True)
    depth.setExtendedDisparity(True)
    depth.setSubpixel(True)

    # Link mono cameras to the depth node
    mono_left.out.link(depth.left)
    mono_right.out.link(depth.right)

    # Create XLinkOut for depth and color output
    xout_video = pipeline.create(dai.node.XLinkOut)
    xout_video.setStreamName("video")
    cam.preview.link(xout_video.input)

    xout_depth = pipeline.create(dai.node.XLinkOut)
    xout_depth.setStreamName("depth")
    depth.depth.link(xout_depth.input)
    
    device = dai.Device(pipeline)
    
    
def update_hsv(_):
    global HOUSING_LOWER_RANGE, HOUSING_UPPER_RANGE, REFLECT_LOWER_RANGE, REFLECT_UPPER_RANGE,THRESHOLD
    try:
        if(not HEADLESS):
            reflector_h_min = cv2.getTrackbarPos("Reflector H Min", "Trackbars")
            reflector_s_min = cv2.getTrackbarPos("Reflector S Min", "Trackbars")
            reflector_v_min = cv2.getTrackbarPos("Reflector V Min", "Trackbars")
            reflector_h_max = cv2.getTrackbarPos("Reflector H Max", "Trackbars")
            reflector_s_max = cv2.getTrackbarPos("Reflector S Max", "Trackbars")
            reflector_v_max = cv2.getTrackbarPos("Reflector V Max", "Trackbars")

            housing_h_min = cv2.getTrackbarPos("Housing H Min", "Trackbars")
            housing_s_min = cv2.getTrackbarPos("Housing S Min", "Trackbars")
            housing_v_min = cv2.getTrackbarPos("Housing V Min", "Trackbars")
            housing_h_max = cv2.getTrackbarPos("Housing H Max", "Trackbars")
            housing_s_max = cv2.getTrackbarPos("Housing S Max", "Trackbars")
            housing_v_max = cv2.getTrackbarPos("Housing V Max", "Trackbars")

        threshold = cv2.getTrackbarPos("threshold", "Trackbars") / 1000

        REFLECT_LOWER_RANGE = np.array([reflector_h_min, reflector_s_min, reflector_v_min])
        REFLECT_UPPER_RANGE = np.array([reflector_h_max, reflector_s_max, reflector_v_max])

        HOUSING_LOWER_RANGE = np.array([housing_h_min, housing_s_min, housing_v_min])
        HOUSING_UPPER_RANGE = np.array([housing_h_max, housing_s_max, housing_v_max])
        
        THRESHOLD = threshold / 1000
    except:
        pass
        
        
def get_cones(isTest=False, image_path = None):
    # Connect to OAK-D
    if(isTest):
        print(cv2.imread(image_path))
        video_frame = cv2.resize(cv2.imread(image_path), (640, 480))
        depth_frame = np.full((480, 640), 5000, dtype=np.uint16) 
    else:
        video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
        depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

        video_frame = video_queue.get().getCvFrame()
        depth_frame = depth_queue.get().getFrame()

    alpha = 1.2 # Contrast control (1.0-3.0)
    beta = -75    # Brightness control (0-100)

    video_frame_darkened = cv2.convertScaleAbs(video_frame, alpha=alpha, beta=beta)

    # Convert to HSV
    hsv = cv2.cvtColor(video_frame_darkened, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)  # Increase saturation by 50%

    # Apply masks for the orange reflector and yellow housing
    reflect_mask = cv2.inRange(hsv, REFLECT_LOWER_RANGE, REFLECT_UPPER_RANGE)
    housing_mask = cv2.inRange(hsv, HOUSING_LOWER_RANGE, HOUSING_UPPER_RANGE)
    
    
    # Use morphological closing to fill in holes
    reflect_mask = cv2.morphologyEx(reflect_mask, cv2.MORPH_CLOSE, kernel)
    housing_mask = cv2.morphologyEx(housing_mask, cv2.MORPH_CLOSE, kernel)

    # Combine the masks
    mask = cv2.bitwise_or(reflect_mask, housing_mask)

    # Detect contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    object_positions = []

    for contour in contours:
        if cv2.contourArea(contour) >= 0:
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
            
            angle_x = 90 - ((cx - CENTER_X) / CENTER_X) * (HORIZONTAL_FOV / 2)
            angle_x = math.radians(angle_x)
            

            
            
            # Retrieve depth value at the center of the detected object
            depth_value = depth_frame[cy, cx] if 0 <= cx < 640 and 0 <= cy < 400 else 0
            
            depth_value = (depth_value / 1000) 
            
            pltx = depth_value * math.cos(angle_x)
            plty = depth_value * math.sin(angle_x)
            
            area = cv2.contourArea(contour) / 1000.0
            if(depth_value == 0):
                pass
        
            elif(depth_value >= -0.038 * np.log((area + THRESHOLD)**2) - 0.703 * np.log(area + THRESHOLD) + 0.07 or (depth_value >= 1.5 and area != 0)):
                # Draw bounding box and depth value
                print(math.degrees(angle_x))
                print(depth_value)
                print(pltx, plty)
                
                cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.circle(video_frame, (cx, cy), 3, (255, 0, 0), -1)
                
                object_positions.append((pltx, plty))


    # Convert masks to 3-channel grayscale for display
    combined_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    # Convert depth to an 8-bit image for visualization
    depth_frame_vis = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    depth_frame_vis = cv2.applyColorMap(depth_frame_vis, cv2.COLORMAP_JET)

    

    # Stack images into a 2x2 grid
    top_row = np.hstack((video_frame, combined_colored))
    bottom_row = np.hstack((depth_frame_vis, depth_frame_vis))
    grid = np.vstack((top_row, bottom_row))

    if(not HEADLESS):
        # Show the stacked frames
        cv2.imshow("Original | Combined Mask | Depth | Chart", grid)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            
    return object_positions