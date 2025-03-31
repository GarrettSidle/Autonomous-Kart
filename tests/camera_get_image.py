import depthai as dai
import cv2
import time
import os

# Create pipeline
pipeline = dai.Pipeline()

# Define a color camera
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
cam_rgb.setInterleaved(False)

# Create an XLinkOut node to output images
xout = pipeline.create(dai.node.XLinkOut)
xout.setStreamName("video")
cam_rgb.video.link(xout.input)

# Start the pipeline
with dai.Device(pipeline) as device:
    queue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    save_path = "test_images"
    os.makedirs(save_path, exist_ok=True)
    
    count = 0
    while True:
        frame = queue.get().getCvFrame()
        filename = os.path.join(save_path, f"image_{count:04d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        count += 1
        time.sleep(5)
