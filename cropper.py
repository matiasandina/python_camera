import cv2
import tkinter as tk
from tkinter import filedialog
import os.path
from pathlib import Path

class Cropper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Select the file to work on, need to use withdraw to get rid of dialogue window
        self.videofile = filedialog.askopenfilename(filetypes=[('MP4 files', '*.mp4')])

        if not self.videofile:
            print("No file selected or file is not an MP4 file.")
            exit()

        # Open the video file
        self.cap = cv2.VideoCapture(self.videofile)

        # Check if video opened successfully
        if not self.cap.isOpened():
            print("Unable to read file!")
            exit()

        # Capture the first frame
        ret, self.frame = self.cap.read()

        # Initialize cropping variables
        self.cropping = False
        self.x_start, self.y_start, self.x_end, self.y_end = 0, 0, 0, 0
        self.oriImage = self.frame.copy()

        # Set up the window for cropping
        cv2.namedWindow("Select area, press 'q' when happy")
        cv2.setMouseCallback("Select area, press 'q' when happy", self.mouse_crop)
        self.clone = self.frame.copy()

        # Display the first frame
        while True:
            cv2.imshow("Select area, press 'q' when happy", self.clone)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Perform cropping
        self.cropped = self.oriImage[self.y_start:self.y_end, self.x_start:self.x_end]

        # Write the cropped video to a new file
        self.newFileName = os.path.join(str(Path(self.videofile).parents[0]), str(Path(self.videofile).stem) + '_cropped.mp4')
        self.frame_width = self.x_end - self.x_start
        self.frame_height = self.y_end - self.y_start
        self.fps = int(round(self.cap.get(cv2.CAP_PROP_FPS)))
        if self.fps == 0:
            self.fps = 15

        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI format
        self.out = cv2.VideoWriter(self.newFileName, fourcc, self.fps, (self.frame_width, self.frame_height))

        # Write the cropped frames to the new file
        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                break
            self.cropped = self.frame[self.y_start:self.y_end, self.x_start:self.x_end]
            self.out.write(self.cropped)

        # Release resources
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()

        print("New cropped video created:", self.newFileName)

    def mouse_crop(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y
            self.cropping = True
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.cropping:
                self.clone = self.frame.copy()
                cv2.rectangle(self.clone, (self.x_start, self.y_start), (x, y), (255, 0, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            self.x_end, self.y_end = x, y
            self.cropping = False
            cv2.rectangle(self.clone, (self.x_start, self.y_start), (self.x_end, self.y_end), (255, 0, 0), 2)

if __name__ == "__main__":
    app = Cropper()

