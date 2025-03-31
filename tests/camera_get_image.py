import depthai as dai
import cv2
import time
import os

# Create pipeline
pipeline = dai.Pipeline()

# Define a color camera
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
cam_rgb.setInterleaved(False)

# Define depth cameras (stereo pair)
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

left.setBoardSocket(dai.CameraBoardSocket.LEFT)
right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)

# Configure stereo depth
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.setLeftRightCheck(True)
stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
left.out.link(stereo.left)
right.out.link(stereo.right)

# Create XLinkOut nodes
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("video")
cam_rgb.video.link(xout_rgb.input)

xout_depth = pipeline.create(dai.node.XLinkOut)
xout_depth.setStreamName("depth")
stereo.depth.link(xout_depth.input)

# Start the pipeline
with dai.Device(pipeline) as device:
    queue_rgb = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    queue_depth = device.getOutputQueue(name="depth", maxSize=1, blocking=False)
    
    save_path = "test_images"
    os.makedirs(save_path, exist_ok=True)
    
    count = 0
    while True:
        rgb_frame = queue_rgb.get().getCvFrame()
        depth_frame = queue_depth.get().getFrame()
        
        # Convert depth to an 8-bit image for visualization
        depth_frame_vis = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_frame_vis = cv2.applyColorMap(depth_frame_vis, cv2.COLORMAP_JET)
        
        filename_rgb = os.path.join(save_path, f"image_{count:04d}.jpg")
        filename_depth = os.path.join(save_path, f"depth_{count:04d}.png")
        
        cv2.imwrite(filename_rgb, rgb_frame)
        cv2.imwrite(filename_depth, depth_frame_vis)
        
        print(f"Saved {filename_rgb} and {filename_depth}")
        count += 1
        time.sleep(5)