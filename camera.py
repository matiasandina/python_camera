import cv2
from imutils.video import VideoStream
import imutils
import time
import numpy as np
import datetime
from videowriter import VideoWriter
import os

class VideoCamera(object):
    def __init__(
    self,
    flip = False, usePiCamera = True,
    fps = 20.0,
    resolution = (640, 480),
    record = False, record_duration = None, record_timestamp = True
    ):

        self.vs = VideoStream(usePiCamera = usePiCamera, resolution = resolution).start()
        self.flip = flip
        # Record settings ###
        # no recording set at init
        self.rec_set = False
        # trigger record
        self.trigger_record = record
        self.resolution = resolution
        self.fps = fps
        # we might be in trouble if we switch from color to grayscale
        self.isColor = self.is_color()
        self.record_start = None
        if (record_duration is not None):
            session_time = datetime.datetime.strptime(record_duration, '%H:%M:%S')
            # Transform the time into number of seconds
            seconds = (session_time.hour * 60 + session_time.minute) * 60 + session_time.second
            self.record_duration = seconds
        self.record_timestamp = record_timestamp
        if (record == True):
            # we will use timestamps to prevent overwriting
            self.name = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + "_output"
            # start video_writer
            self.video_writer = VideoWriter(filename=self.name, fps=self.fps, resolution = self.resolution)
        time.sleep(2.0)



    def __del__(self):
        self.vs.stop()

    def is_color(self):
        frame = self.vs.read()
        if (len(frame.shape) == 3):
            return True
        else:
            return False


    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def read(self):
        # this is the read function we want to do processing
        frame = self.flip_if_needed(self.vs.read())
        timestamp = datetime.datetime.now()
        if (self.trigger_record):
            # check whether the video size is ok or we need to chunk
            self.check_video_filesize()
            if (self.record_timestamp):
                cv2.putText(frame, str(timestamp),
                    (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255,255,255),
                    1)
            # let's only call it if the framerate is ok
            if (self.check_framerate(timestamp)):
                self.video_writer.put_to_q(frame, timestamp)
            # self.record(frame)
        return frame

    # This function handles the posting of .jpg through ip stream
    def get_frame(self, label_time, camera_stamp = None):
        # This function ends up converting to jpg and timestamping
        # intended for streaming 
        upload_frame = self.flip_if_needed(self.vs.read())
        if (label_time):
            cv2.putText(upload_frame, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (255,255,255),
                1)
        if (camera_stamp is not None):
            cv2.putText(upload_frame, str(camera_stamp), 
                (10, self.resolution[1] - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (255,255,255),
                1)

        ret, jpeg = cv2.imencode('.jpg', upload_frame)
        return jpeg.tobytes()

    # We can use this function if we had a classifier that was well suited
    # It might need computation power to do this in real time
    def get_object(self, classifier):
        found_objects = False
        frame = self.flip_if_needed(self.vs.read()).copy() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects)

    # The function below has problems with frame rate not being constant
    # We account for frame rate by assuming constant frame rate but that fails in real life
    def record(self, frame):
        """
        Opencv VideoWriter
        https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
        This time we create a VideoWriter object. 
        We should specify the output file name (eg: output.avi).
        Then we should specify the FourCC code (details in next paragraph).
        Then number of frames per second (fps) and frame size should be passed.
        And last one is isColor flag. If it is True, encoder expect color frame,
        otherwise it works with grayscale frame.

        Example comes from here
        https://stackoverflow.com/questions/30509573/writing-an-mp4-video-using-python-opencv
        """
        if (self.rec_set == False):
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.recorder = cv2.VideoWriter(self.name, self.fourcc, self.fps, self.resolution, self.isColor)
            self.rec_set = True
            self.prev_frame = time.time()
            self.record_start = self.prev_frame
        else:
            # account for fps
            # otherwise, we would need to account for this via waitKey(int(1000/fps)) 
            current_frame = time.time()
            if (current_frame - self.prev_frame > 1/self.fps):
                self.prev_frame = current_frame

            if (self.prev_frame - self.record_start > self.record_duration):
                print(self.prev_frame)
                print(self.record_start)
                print(self.record_duration)
                # stop the recording (not the camera)
                self.trigger_record = False

    def check_framerate(self, timestamp):
        if (self.rec_set == False):
            self.rec_set = True
            self.prev_frame = timestamp
            self.record_start = self.prev_frame
            return True
        else:
            # account for fps
            # otherwise, we would need to account for this via waitKey(int(1000/fps)) 
            delta_time = (timestamp - self.prev_frame).total_seconds() 
            if (delta_time > 1/self.fps):
                self.prev_frame = timestamp
                return True

            current_duration = (self.prev_frame - self.record_start).total_seconds()

            if (current_duration > self.record_duration):
                print(self.prev_frame)
                print(self.record_start)
                print(self.record_duration)
                # stop the recording (not the camera)
                self.video_writer.stop()
                # stop triggering record in the future
                self.trigger_record = False
        # if we got up to here and no conditions were met
        return False

    def check_video_filesize(self):
        #TODO: Potential problem harcoded extension, it's also harcoded on videowriter 
        if os.path.exists(self.name + ".avi"):
            current_size = os.stat(self.name + ".avi").st_size
            # size will be in bytes, let's have a limit of 100 Mb
            if (current_size > 100 * 1024 * 1024):
                # stop the video writer
                self.video_writer.stop()
                print("Video truncated...initializing new clip")
                # create a new filename
                self.name = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")) + "_output"
                # start the writer again
                self.video_writer = VideoWriter(filename=self.name, fps=self.fps, resolution = self.resolution)

