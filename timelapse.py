import cv2
from camera import VideoCamera
import datetime
import argparse
import time

# creates a camera object, don't flip vertically
video_camera = VideoCamera(
	flip = False, 
	usePiCamera = False, 
	resolution = (640, 480),
	record = False,
	record_timestamp = False,
	record_duration = "00:05:00" # "HH:MM:SS"
	) 

def save_image(frame, current_frame):
	filename = current_frame.strftime("%Y-%m-%d_%H:%M:%S") + "_capture.png"
	cv2.imwrite(filename, frame)


def timelapse(delay, duration = 1000, show_feed = True):
	init_time = datetime.datetime.now()
	finish_time = init_time + datetime.timedelta(seconds=duration)
	# current gets assigned to init_frame
	previous_frame = current_frame = init_time
	while(current_frame < finish_time):
		# take the time again
		current_frame = datetime.datetime.now() 
		elapsed_time = (current_frame - previous_frame).total_seconds()
		if(elapsed_time < delay):
			time.sleep(delay)
		else:
			# only capture if meets delay
			# read frame
			frame = video_camera.read()
			# show feed (this would not be continuous feed, so likely unnecessary)
			if (show_feed):
				cv2.imshow("feed", frame)
				# adding at least ms to the actual delay
				# don't think it's crucial to adjust
				k = cv2.waitKey(1)
				if k == 27:
					break
			save_image(frame, current_frame)
			previous_frame = current_frame



cv2.destroyAllWindows()


if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-delay", "--delay", required=True,
	help="Delay between photos in seconds")
	ap.add_argument("-duration", "--duration", required=False,
		default = 1000,
	help="Timelapse duration")
	ap.add_argument("-show_feed", "--show_feed",
		required=False,
		type=lambda x: (str(x).lower() == 'true'),
		default = True,
	help="boolean: Whether to show the video feed or not (default is True).")
	args = vars(ap.parse_args())
	timelapse(delay = float(args["delay"]), duration = float(args["duration"]), show_feed = args["show_feed"])