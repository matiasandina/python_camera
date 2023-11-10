import cv2
from imutils.video import VideoStream
import imutils
import time
import numpy as np
import datetime
from videowriter import VideoWriter
import os
import threading

class VideoCamera(object):
    def __init__(
    self,
    src=0,
    flip = False, usePiCamera = True,
    fps = 25,
    resolution = (640,480),
    record = False, record_duration = None, record_timestamp = True,
    record_name = None
    ):

        if resolution is None:
            resolution = (320, 240)
        self.vs = VideoStream(src=src, usePiCamera = usePiCamera, resolution = resolution).start()
        #if usePiCamera is False:
        #    # we need to change things here because it will ignore resolution if not using the piCam
        #    # https://github.com/PyImageSearch/imutils/issues/55
        #    # this is not currently working!!!!
        #    self.vs.stream.set(3, resolution[0])
        #    self.vs.stream.set(4, resolution[1])
        self.flip = flip
        # Record settings ###
        # no recording set at init
        self.rec_set = False
        self.record = record
        # trigger record
        self.trigger_record = record
        self.resolution = resolution
        self.fps = fps
        # we might be in trouble if we switch from color to grayscale
        self.isColor = self.is_color()
        self.record_start = None
        self.record_name = record_name
        if (record_duration is not None):
            session_time = datetime.datetime.strptime(record_duration, '%H:%M:%S')
            # Transform the time into number of seconds
            seconds = (session_time.hour * 60 + session_time.minute) * 60 + session_time.second
            self.record_duration = seconds
        self.record_timestamp = record_timestamp
        # this is so that all timestamped things have a consistent format
        self.timestamp_format = '%Y-%m-%dT%H-%M-%S'
        if (self.record == True):
            # we will use timestamps to prevent overwriting
            if self.record_name is None:
                self.name = datetime.datetime.now().strftime(self.timestamp_format) + "_output"
            else:
                self.name = f"{datetime.datetime.now().strftime(self.timestamp_format)}_{str(self.record_name)}_output"
            # start video_writer
            self.video_writer = VideoWriter(filename=self.name, fps=self.fps, resolution = self.resolution)



    def close(self):
        # Stop the video stream
        if hasattr(self, 'vs') and self.vs is not None:
            self.vs.stop()

        # Release the stream if it's not using PiCamera
        if hasattr(self, 'usePiCamera') and not self.usePiCamera:
            if hasattr(self.vs, 'stream') and self.vs.stream is not None:
                self.vs.stream.release()

        # Stop the video writer if recording is enabled
        if self.record and hasattr(self, 'video_writer'):
            self.video_writer.stop()

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

    def start_recording(self):
        if not self.record:
            print("Recording is not enabled.")
            return

        if not hasattr(self, 'record_thread') or not self.record_thread.is_alive():
            self.trigger_record = True
            self.record_start = datetime.datetime.now()  # Initialize record_start here
            self.record_thread = threading.Thread(target=self._record_loop)
            self.record_thread.start()
            print("Started Recording in thread.")
        else:
            print("Recording is already in progress.")

    def is_recording(self):
            return self.trigger_record

    def stop_recording(self, from_thread=False):
        self.trigger_record = False
        if not from_thread and hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join()  # Wait only if called from outside the thread
        print("Recording stopped.")

    def _record_loop(self):
        while self.trigger_record:
            frame = self.read()
            current_time = datetime.datetime.now()

            # Process the frame for recording
            self.process_frame_for_recording(frame)

            if self.record_duration and (current_time - self.record_start).total_seconds() > self.record_duration:
                break  # Stop recording once duration is reached

        # Signal that recording is done
        self.trigger_record = False
        self.video_writer.stop()  # Make sure to stop the video writer
    
    def read(self):
        # Capture the frame
        frame = self.flip_if_needed(self.vs.read())
        return frame

    def process_frame_for_recording(self, frame):
        timestamp = datetime.datetime.now()
        if self.trigger_record:
            self.check_video_filesize()
            if self.record_timestamp:
                cv2.putText(frame, timestamp.isoformat(timespec='seconds'), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
            if self.check_framerate(timestamp):
                self.video_writer.put_to_q(frame, timestamp)
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

    def check_framerate(self, timestamp):
        if not hasattr(self, 'prev_frame'):
            self.prev_frame = timestamp
            return True

        # Calculate the time difference between the current frame and the previous frame
        delta_time = (timestamp - self.prev_frame).total_seconds()

        # If the time difference is greater than or equal to the desired frame interval, process this frame
        if delta_time >= 1 / self.fps:
            self.prev_frame = timestamp
            return True

        # If the time difference is less than the desired frame interval, skip this frame
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
                if self.record_name is None:
                   self.name = datetime.datetime.now().strftime(self.timestamp_format) + "_output"
                else:
                    self.name = f"{datetime.datetime.now().strftime(self.timestamp_format)}_{str(self.record_name)}_output"
                # start the writer again
                self.video_writer = VideoWriter(filename=self.name, fps=self.fps, resolution = self.resolution)

