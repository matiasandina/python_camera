import cv2
from camera import VideoCamera
import datetime
import argparse
import time

# This function aims to reduce power consumption by deleting the camera object
# It might be more useful if running from a low power setup (raspberry pi on battery)

def save_image(frame, current_frame):
	filename = current_frame.strftime("%Y-%m-%d_%H:%M:%S") + "_capture.png"
	cv2.imwrite(filename, frame)


def timelapse(delay, duration = 1000):
	init_time = datetime.datetime.now()
	finish_time = init_time + datetime.timedelta(seconds=duration)
	# current gets assigned to init_frame
	previous_frame = current_frame = init_time
	# camera will get initiated many times in this one
	# it has a delay to make sure things are working
	# we can modify the user delay to match camera's on/off delay (2 seconds implemented as time.sleep(2))
	delay = delay - 2
	while(current_frame < finish_time):
		# take the time again
		current_frame = datetime.datetime.now() 
		elapsed_time = (current_frame - previous_frame).total_seconds()
		# print(elapsed_time)
		if(elapsed_time < delay):
			# debug
			# print("Entering delay of " + str(delay))
			time.sleep(delay)
		else:
			video_camera = VideoCamera(
			flip = False, usePiCamera = False, 
			resolution = (640, 480),
			record = False,
			record_timestamp = False,
			) 
			# read frame
			frame = video_camera.read()
			# save it
			save_image(frame, current_frame)
			# assign time
			previous_frame = current_frame
			# delete camera
			del(video_camera)


if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-delay", "--delay", required=True,
	help="Delay between photos in seconds")
	ap.add_argument("-duration", "--duration", required=False,
		default = 1000,
	help="Timelapse duration")
	args = vars(ap.parse_args())
	timelapse(delay = float(args["delay"]), duration = float(args["duration"]))