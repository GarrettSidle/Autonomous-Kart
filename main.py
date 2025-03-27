import cv2
import depthai as dai
import numpy as np
import matplotlib.pyplot as plt
import math

# Default HSV range for detecting orange & yellow
LOWER_RANGE = np.array([10, 250, 110])  
UPPER_RANGE = np.array([35, 255, 180])  
THRESHOLD    = 500

HORIZONTAL_FOV = 69  
FRAME_WIDTH = 640    
CENTER_X = FRAME_WIDTH / 2 

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
        THRESHOLD = threshold
    except:
        print("Error updating scaler values")


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


plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(-320, 320)  
ax.set_ylim(0, 320)  
ax.set_xlabel("X Position ")
ax.set_ylabel("Y Position ")
scatter = ax.scatter([], [])  

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

# Connect to OAK-D
with dai.Device(pipeline) as device:
    video_queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    depth_queue = device.getOutputQueue(name="depth", maxSize=1, blocking=False)

    while True:
        video_frame = video_queue.get().getCvFrame()
        depth_frame = depth_queue.get().getFrame()

        # Convert to HSV
        hsv = cv2.cvtColor(video_frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255)  # Increase saturation by 50%

        # Apply the mask for orange detection
        mask = cv2.inRange(hsv, LOWER_RANGE, UPPER_RANGE)
        filtered_frame = cv2.bitwise_and(video_frame, video_frame, mask=mask)

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
                
                pltc = (depth_value / 10000) * 3000
                
                pltx = pltc * math.cos(90 - angle_x)
                plty = pltc * math.sin(90 - angle_x)
                
                object_positions.append((pltx, plty))
                print((pltx, plty))
                
                if(depth_value == 0):
                    print("oops")

                elif(cv2.contourArea(contour) >= (20/depth_value) * THRESHOLD ):
                    # Draw bounding box and depth value
                    cv2.rectangle(video_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(video_frame, (cx, cy), 5, (255, 0, 0), -1)
                    cv2.putText(video_frame, f"Depth: {depth_value}mm", (x, y + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Normalize depth frame for visualization
        depth_visual = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        depth_colormap = cv2.applyColorMap(depth_visual, cv2.COLORMAP_JET)

        # Resize depth image to match 480p resolution
        depth_colormap_resized = cv2.resize(depth_colormap, (640, 480))

        # Convert mask to 3-channel grayscale (so it can be stacked with color images)
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # Stack all three frames side by side
        combined_frame = np.hstack((video_frame, mask_colored, depth_colormap_resized))
        cv2.imshow("Color | Mask | Depth", combined_frame)
        
        
        scatter.set_offsets(object_positions if object_positions else np.empty((0, 2)))

        plt.draw()
        plt.pause(0.01)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()


    
