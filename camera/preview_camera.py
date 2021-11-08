# This script will allow preview from a camera object

# from camera import VideoCamera
from imutils.video import VideoStream
import imutils
import cv2
import signal
import os
import time

def exit_gracefully(self, *args):
	cv2.destroyAllWindows()
	sys.exit(0)

def run():
	resolution = (320,240)
	all_dirs = os.listdir("/dev/")
	cam_dirs = [os.path.join("/dev", dir) for dir in all_dirs if "video" in dir]
	available_cams = []
	cams = [None] * len(cam_dirs)
	for i in range(len(cam_dirs)):
		src = cam_dirs[i]
		try:
			cams[i] = VideoStream(src = src, framerate=25).start()
			available_cams.append(src)
		except:
			print(f"An exception occurred in cam {src}") 
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)
	cams = [cam for cam in cams if cam is not None]
	#for some reason this is giving more cameras than it should
	#print(available_cams)
	# used to record the time when we processed last frame
	prev_frame_time = [0] * len(available_cams)
	# used to record the time at which we processed current frame
	new_frame_time = [0] * len(available_cams)
	fps = [0] * len(available_cams)
	while(True):
		if (len(cams) > 0):
			for i in range(len(available_cams)):
				frame = cams[i].read()
				# resize to speed things up a bit
				# time when we finish processing for this frame
				if frame is not None:
					frame = imutils.resize(frame, width=resolution[0], height=resolution[1])
					new_frame_time[i] = time.time()
					time_delta = new_frame_time[i]-prev_frame_time[i]
					fps[i] = int(1/(time_delta))
					prev_frame_time[i] = new_frame_time[i]
					window_title = available_cams[i]
					cv2.putText(frame, "Preview camera:" + window_title,(10, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
					cv2.putText(frame, "press 'q' to quit",(10, 100),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
					cv2.imshow(window_title, frame)
					print(f"fps: {fps}", end="\r")
			k = cv2.waitKey(1)
			if k == ord("q"):
				cv2.destroyAllWindows()
				break
		else:
			print("No cams detected")
			break
	# When everything done, release the capture
	for cam in cams:
		cam.stop()
		cv2.destroyAllWindows()

if __name__ == '__main__':
	run()
