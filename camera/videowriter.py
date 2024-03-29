# video writer
# * writes frames at a fixed rate even if camera's rate varies or is imprecise,
#  possibly dropping or repeating frames in the process
#  (note: for LifeCam, the frame rate depends on the exposure)
# * also writes trajectories (which need to be in sync with frames written)
# * stop() needs to be called at the end of video, unless VideoWriter is
#  instantiated with "with"
# code comes from
# Ulrich Stern
# https://github.com/ulrichstern/SkinnerTrax/blob/master/rt-trx/rt-trx.py
# modified by Matias Andina 2023-11-14

import queue
import threading
import cv2
import time
import numpy as np

class VideoWriter:
  SUPPORTED_FORMATS = {
      '.avi': ['XVID', 'MJPG', 'DIVX'],
      # some codecs need opencv to be built from from source and not pip installed?
      # see here https://github.com/opencv/opencv-python/issues/81 
      # and here https://github.com/opencv/opencv-python/issues/207
      '.mp4': ['AVC1', 'H264', 'HEVC', 'X264', 'MP4V'],
      # .mkv VP90 is open source but it's computationally expensive!
      '.mkv': ['VP90']
  }

  def __init__(self, filename=None, fps=20.0, resolution=(640, 480), extension='.mp4', codec='mp4v'):
    self._EXT = extension.lower()
    self.codec = codec.upper()
    self.filename = filename
    self.empty_filename = filename is None
    if self.empty_filename:
      print("No filename provided. Exiting VideoWriter()")
      return
    else:
      print(f"\nReceived video name: {self.filename}{self._EXT}")

    if self._EXT not in self.SUPPORTED_FORMATS:
      raise ValueError(f"Unsupported file extension: {self._EXT}")

    if self.codec not in self.SUPPORTED_FORMATS[self._EXT]:
        raise ValueError(f"Codec {self.codec} is not supported for {self._EXT} files")

    if resolution is None:
      print("No resolution provided, defaulting to (640x480)")
      resolution = (640, 480)

    self.fourcc = cv2.VideoWriter_fourcc(*self.codec)
    # Rest of your code to initialize the VideoWriter object
    self.fps = fps
    self.dt = 1.0/fps
    self.resolution = resolution
    # We will put frames on a queue and get them from there
    self.q = queue.Queue()
    self._stop = False
    # n is the frame number
    self.n = 0 
    self.wrtr = threading.Thread(target=self.recorder)
    self.wrtr.start()

  # writer thread
  def recorder(self):
    # initialize things to None
    # we will receive tuples, lastframe_ts has the frame and timestamp
    lastframe_ts = t0 = video_writer = None
    while True:
      if self._stop:
        break
      frame_ts = lastframe_ts
      # while we have frames in queue get most recent frame
      while not self.q.empty():
        # get queue as tupple
        frame_ts = self.q.get_nowait()
      # only do things with frames that are not None
      if frame_ts is not None:
        lastframe_ts = frame_ts
        # unpack
        frame, ts = frame_ts
        if video_writer is None:
          # initialize cv2 video_writer
          video_writer = cv2.VideoWriter(self.filename + self._EXT,
            self.fourcc,
            self.fps,
            self.resolution,
            isColor= self.is_color(frame))
          t0 = time.time()
        # write frame
        video_writer.write(frame)
        # write timestamp
        self.write_timestamp(timestamp=ts)
        self.n += 1
      if t0 is None:
        dt = self.dt
      else:
        dt = max(0, t0 + self.n * self.dt - time.time())
      # Add a print statement to confirm frame rate control
      # this will put the thread to sleep to satisfy frame rate
      time.sleep(dt)

  # for "with"
  def __enter__(self): return self
  def __exit__(self, exc_type, exc_value, traceback):
    if not self.empty_filename and not self._stop:
      self.stop()

  # write frame; can be called at rate different from fps
  def put_to_q(self, frame, timestamp):
    if not self.empty_filename:
      # put frame and timestamp as tupple into queue
      self.q.put((frame, timestamp))


  # returns number (0,1,...) of next frame written to video; None if no video
  # written
  def frameNum(self): return None if self.empty_filename else self.n

  # returns the video filename (without extension), None if no video written
  def get_filename(self): return self.filename

  # stop video writer
  def stop(self):
    if not self.empty_filename:
      self._stop = True
      self.wrtr.join()

  def is_color(self, frame):
    if (len(frame.shape) == 3):
      return True
    else:
      return False

  def write_timestamp(self, timestamp):
    # '%Y-%m-%dT%H:%M:%S.%f' is better than '%Y-%m-%dT%H:%M:%S:%f'
    timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
    # this will write timestamps to file
    # mind that timestamp must be in a [] for numpy to like it
    with open(self.filename + "_timestamp.csv",'a') as outfile:
      np.savetxt(outfile, [timestamp],
      delimiter=',', fmt='%s')
