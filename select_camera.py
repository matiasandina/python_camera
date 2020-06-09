import cv2
import time

def select_camera():

	selected_cam = []
	caps, valid_cams = detect_available()

	while(True):

		for webcam in valid_cams:
			ret, frame = caps[webcam].read()
			# Put text
			cv2.putText(frame, 'webcam ID: '+ str(webcam), (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
			1, (255, 255, 0), 2)
			cv2.putText(frame, 'press q to quit preview and continue', (10, 100), cv2.FONT_HERSHEY_SIMPLEX,
			1, (255, 255, 0), 2)
			if len(selected_cam) > 0:
				if webcam in selected_cam:
				# TODO: Nice to have, a toggle (pressing a second time removes selection)
					cv2.putText(frame, 'Selected', (10, 150), cv2.FONT_HERSHEY_SIMPLEX,
						1, (0, 0, 255), 2)

			# Display the resulting frame
			cv2.imshow('camera no. ' + str(webcam), frame)
			# try to get each camera
			k = cv2.waitKey(1)
			if k == ord(str(webcam)):
				print("Camera ID " + str(webcam) + " Selected")
				selected_cam.append(webcam)
		# break 
		if k == ord('q'):
			break
	print("Releasing cameras...")

	# When everything done, release the capture
	for cap in caps:
		cap.release()

	for x in range(10):
		time.sleep(0.1)
		cv2.destroyAllWindows()

	return selected_cam

def detect_available():

	# Begin camera selection
	print("Trying to read all available cameras in system...")

	# detect all connected webcams
	valid_cams = []
	errors_id = []

	for i in range(10):
		try:
			# The following line will print error message regardless,
			# it's an OpenCV hard-coded issue
			cap = cv2.VideoCapture(i)
			if cap.isOpened():
				(test, frame) = cap.read()
				if test:
					valid_cams.append(i)
		except:
			pass

	caps = []

	for webcam in valid_cams:
		caps.append(cv2.VideoCapture(webcam))

	return caps, valid_cams


if __name__ == '__main__':
	# select_camera.py executed as script
	# do something
	select_camera()