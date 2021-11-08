from camera import VideoCamera
import cv2
import datetime
import os

# Modify these parameters
cam_dirs = ["/dev/video0", "/dev/video2"] # check preview_camera.py!
# this will grab the "videoi" so we can identify which recording comes from what camera
# it's not a perfect match with an animal's id, but it's good enough to move videos quickly to folders 
video_names = [os.path.basename(dir) for dir in cam_dirs]
hours = 5
minutes = 0
seconds = 0

record_start = datetime.datetime.now()
record_duration_delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
record_duration = "{:0>8}".format(str(record_duration_delta))
print(f"Record Duration: {record_duration}")

if (len(cam_dirs) == 1):
    resolution = (640, 480)
else:
    resolution = (640, 480)
print(resolution)

# Define cam objects
cams = []
for i in range(len(cam_dirs)):
    cams.append(
        VideoCamera(
        src = cam_dirs[i], 
        resolution = resolution,
        fps = 20.0,
        flip = False,
        usePiCamera=False,
        record = True,
        record_name = video_names[i],
        record_timestamp = False,
        record_duration = record_duration # HH:MM:SS
        )
    )

while(True):
    for i in range(len(cam_dirs)):
        frame = cams[i].read()
        now = datetime.datetime.now()
        if (now - record_start < record_duration_delta):
            cv2.rectangle(frame, (5,5), (25,25), (0,0,255), -1)
        window_title = cam_dirs[i]
        cv2.imshow(window_title, frame)
    k = cv2.waitKey(1)
    if k == ord("q"):
        [cam.__del__() for cam in cams]
        cv2.destroyAllWindows()
        print("Stop command detected...Exit")
        break
