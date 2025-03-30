import cv2
import depthai as dai
import numpy as np
import math

# Default HSV range for detecting orange & yellow
LOWER_RANGE = np.array([00, 79, 126])  
UPPER_RANGE = np.array([19, 255, 255])  
THRESHOLD    = 1

HORIZONTAL_FOV = 69  
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


def camera_init():
    global pipeline, cam, mono_left, mono_right, depth, xout_depth, xout_video, device
    
    # Create OpenCV Trackbars for HSV tuning with default values for orange/yellow
    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)  
    cv2.resizeWindow("Trackbars", 640, 300)  
    cv2.createTrackbar("H Min", "Trackbars", LOWER_RANGE[0], 180, update_hsv)
    cv2.createTrackbar("S Min", "Trackbars", LOWER_RANGE[1], 255, update_hsv)
    cv2.createTrackbar("V Min", "Trackbars", LOWER_RANGE[2], 255, update_hsv)
    cv2.createTrackbar("H Max", "Trackbars", UPPER_RANGE[0], 180, update_hsv)
    cv2.createTrackbar("S Max", "Trackbars", UPPER_RANGE[1], 255, update_hsv)
    cv2.createTrackbar("V Max", "Trackbars", UPPER_RANGE[2], 255, update_hsv)
    cv2.createTrackbar("threshold", "Trackbars", THRESHOLD, 10000, update_hsv)


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
    global LOWER_RANGE, UPPER_RANGE, THRESHOLD
    try:
        h_min = cv2.getTrackbarPos("H Min", "Trackbars")
        s_min = cv2.getTrackbarPos("S Min", "Trackbars")
        v_min = cv2.getTrackbarPos("V Min", "Trackbars")
        h_max = cv2.getTrackbarPos("H Max", "Trackbars")
        s_max = cv2.getTrackbarPos("S Max", "Trackbars")
        v_max = cv2.getTrackbarPos("V Max", "Trackbars")
        threshold = cv2.getTrackbarPos("threshold", "Trackbars")
    
        LOWER_RANGE = np.array([h_min, s_min, v_min])
        UPPER_RANGE = np.array([h_max, s_max, v_max])
        THRESHOLD = threshold / 1000
    except:
        pass
        
        
def get_cones():
    # Connect to OAK-D

    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

    video_frame = video_queue.get().getCvFrame()
    depth_frame = depth_queue.get().getFrame()

    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0     # Brightness control (0-100)

    video_frame = cv2.convertScaleAbs(video_frame, alpha=alpha, beta=beta)

    # Convert to HSV
    hsv = cv2.cvtColor(video_frame, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)  # Increase saturation by 50%

    # Apply the mask for orange detection
    mask = cv2.inRange(hsv, LOWER_RANGE, UPPER_RANGE)

    # Detect contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    object_positions = []

    for contour in contours:
        if cv2.contourArea(contour) >= 50:
            x, y, w, h = cv2.boundingRect(contour)
            cx, cy = x + w // 2, y + h // 2
            
            angle_x = ((cx - CENTER_X) / CENTER_X) * (HORIZONTAL_FOV / 2)
            angle_x = math.radians(angle_x)
            

            
            
            # Retrieve depth value at the center of the detected object
            depth_value = depth_frame[cy, cx] if 0 <= cx < 640 and 0 <= cy < 400 else 0
            
            depth_value = (depth_value / 1000) 
            
            pltx = depth_value * math.cos(90 - angle_x)
            plty = depth_value * math.sin(90 - angle_x)
            
            
            if(depth_value == 0):
                pass

            elif(cv2.contourArea(contour) >= (20/depth_value) * THRESHOLD ):
                # Draw bounding box and depth value
                cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(video_frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(video_frame, f"Depth: {depth_value}m", (x, y + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                
                object_positions.append((pltx, plty))


    # Convert mask to 3-channel grayscale (so it can be stacked with color images)
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Stack all three frames side by side
    combined_frame = np.hstack((video_frame, mask_colored))
    cv2.imshow("Color | Mask", combined_frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        
    return object_positions