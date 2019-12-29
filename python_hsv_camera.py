from __future__ import print_function
try:
    # for python 2
    import Tkinter as tkinter
except ImportError:
    # for python 3
    import tkinter as tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
try:
    # for python 2
    import tkMessageBox
except ImportError:
    # for python 3
    from tkinter import messagebox as tkMessageBox
import pandas as pd
import time
import numpy as np

def makeentry(parent, caption, width=None, pack_side=tkinter.TOP, **options):
    tkinter.Label(parent, text=caption).pack(side=tkinter.LEFT)
    entry = tkinter.Entry(parent, **options)
    if width:
        entry.config(width=width)
    entry.pack(side=pack_side)
    return entry

# TODO: add the possibility to record video

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        # Create pop-up for controls
        self.top = tkinter.Toplevel()
        self.top.protocol("WM_DELETE_WINDOW", disable_event)

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        self.canvas = tkinter.Canvas(window, width= 1.1 * self.vid.width,
                                     height=1.1 * self.vid.height, borderwidth=0, background="#ffffff")
        self.frame = tkinter.Frame(self.canvas, background="#ffffff")
        self.vsb = tkinter.Scrollbar(window, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", 
                                  tags="self.frame")
        
       
        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.taking_image_var = tkinter.IntVar()
        self.taking_video_var = tkinter.IntVar()

        self.taking_image = tkinter.Checkbutton(self.top, text="Capture Image", variable = self.taking_image_var)
        self.taking_image.pack(side=tkinter.TOP)

        self.taking_video = tkinter.Checkbutton(self.top, text="Capture Video", variable = self.taking_video_var)
        self.taking_video.pack(side=tkinter.TOP)



        # Entry box
        self.entry = makeentry(self.top, "Filename", 50, pack_side=tkinter.TOP)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tkinter.Button(self.top, text="Capture", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)

        # region Sliders ####

        # H min
        self.H_min_slider = tkinter.Scale(self.top, from_=0, to=255,
                                      orient=tkinter.HORIZONTAL,
                                      sliderlength=15, length=200,
                                      label= "H_min")
        self.H_min_slider.pack(anchor=tkinter.CENTER, expand = True)

        # H max
        self.H_max_slider = tkinter.Scale(self.top, from_=0, to=255,
                                      orient=tkinter.HORIZONTAL,
                                      sliderlength=15, length=200,
                                      label="H_max")
        self.H_max_slider.set(255)
        self.H_max_slider.pack(anchor=tkinter.CENTER, expand=True, pady=2)

        # S min
        self.S_min_slider = tkinter.Scale(self.top, from_=0, to=255,
                                          orient=tkinter.HORIZONTAL,
                                          sliderlength=15, length=200,
                                          label= "S_min")
        self.S_min_slider.pack(anchor=tkinter.CENTER, expand=True, pady=2)

        # S max
        self.S_max_slider = tkinter.Scale(self.top, from_=0, to=255,
                                          orient=tkinter.HORIZONTAL,
                                          sliderlength=15, length=200,
                                          label="S_max")
        self.S_max_slider.set(255)
        self.S_max_slider.pack(anchor=tkinter.CENTER, expand=True, pady=2)

        # V min
        self.V_min_slider = tkinter.Scale(self.top, from_=0, to=255,
                                          orient=tkinter.HORIZONTAL,
                                          sliderlength=15, length=200,
                                          label="V_min")
        self.V_min_slider.pack(anchor=tkinter.CENTER, expand=True, pady=2)

        # V max
        self.V_max_slider = tkinter.Scale(self.top, from_=0, to=255,
                                          orient=tkinter.HORIZONTAL,
                                          sliderlength=15, length=200,
                                          label="V_max")
        self.V_max_slider.set(255)
        self.V_max_slider.pack(anchor=tkinter.CENTER, expand=True, pady=2)

        # endregion

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def snapshot(self):
        # if video is selected, call video writer, else capture image
        if(self.taking_video_var.get() == 1):
        	self.videoWriter(self)
        else:
            # Get a frame from the video source
            ret, frame = self.vid.get_frame()
    
            if ret:
                # look for entry
                filename = self.entry.get()

                if len(filename) > 0:

                    # Get the HSV values

                    hsv_name = "HSV_values_" +\
                           filename + ".csv"

                    df = pd.DataFrame({"HSV_min": self.HSV_min, "HSV_max": self.HSV_max})

                    df.to_csv(hsv_name, columns=['HSV_min', 'HSV_max'], index=False)
    
                    pic_filename = time.strftime("%Y-%m-%d-%H-%M-%S") + "_" + filename + ".png"

                    cv2.imwrite(pic_filename,
                          cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    tkMessageBox.showinfo("All set :)", "Picture saved as: " + pic_filename)
                    tkMessageBox.showinfo("All set :)", "HSV filter values saved as: " + hsv_name)
                else:
                    tkMessageBox.showinfo("Error", "Please enter a filename")
    
    def videoWriter(self, event):
        print("Recording video")
        cap = cv2.VideoCapture(0)
        #width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        #height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (self.vid.width, self.vid.height)
        # TODO: codecs might be a problem here
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # write at 30 fps
        out = cv2.VideoWriter('your_video.avi', fourcc, 30, (640, 480))

        while(True):
            _, frame = cap.read()
            #cv2.imshow('Recording...', frame)
            out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # TODO: this might be a problem, we might want to define recording time
                break

        # Release stuff
        cap.release()
        out.release()
        #cv2.destroyAllWindows()

    def slider_values(self):

        self.HSV_min = (self.H_min_slider.get(), self.S_min_slider.get(), self.V_min_slider.get())
        self.HSV_max = (self.H_max_slider.get(), self.S_max_slider.get(), self.V_max_slider.get())

        return

    def do_contour_math(self):

        ret, image = self.vid.get_frame()

        # Make the mask
        binarymask = cv2.inRange(image.copy(), self.HSV_min, self.HSV_max)

        # Perform some smoothing

        binarymask = cv2.medianBlur(binarymask, 3)

        kernel = np.ones((5, 5), np.uint8)

        # Marbles have holes inside, we will close them
        # We iterate 3 times to make "sure" that they are indeed closed
        mask = cv2.morphologyEx(binarymask, cv2.MORPH_CLOSE, kernel,
                                iterations=3)
        # Get contours
        contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, 2)

        return contours


    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        video_state = self.taking_video_var.get()
        image_state = self.taking_image_var.get()

        # If we changed from video to image, this will be true
        if(image_state == 1 and self.capture_mode == "video"):
            self.taking_video.deselect()
            self.capture_mode = "image"
            video_state = self.taking_video

        if(video_state == 1):
            # remove selection from the other one
            self.taking_image.deselect()
            self.capture_mode = "video"

        # Get slider values
        self.slider_values()

        # Do image processing
        binarymask = cv2.inRange(frame.copy(), self.HSV_min, self.HSV_max)

        # Convert binary mask to RGB
        binarymask = cv2.cvtColor(binarymask, cv2.COLOR_GRAY2RGB)

        # get contours

        contours = self.do_contour_math()

        # Draw the contours onto binary mask
        for cts in range(0, len(contours)):
            cv2.drawContours(binarymask, contours,
                             cts,  # cont i
                             (0, 0, 255),  # blue on RGB
                             2)  # thickness

        # store them
        self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        self.binarymask = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(binarymask))


        # Create photos once
        if not hasattr(self, "iid_photo"):
            self.iid_photo = self.canvas.create_image(0, 5, image=self.photo, anchor=tkinter.NW)
            self.iid_mask = self.canvas.create_image(self.vid.width + 5, 5, image=self.binarymask, anchor=tkinter.NW)
        else:
            # just update them
            self.canvas.itemconfig(self.iid_photo, image=self.photo)
            self.canvas.itemconfig(self.iid_mask, image=self.binarymask)

        self.window.after(self.delay, self.update)


    def close_window(self):
        ret, frame = self.vid.get_frame()
        # close window
        if ret:
            # do something
            print("click on close window")

    def on_closing(self):
        if tkMessageBox.askyesno("Quit", "Do you want to quit?"):
            self.window.destroy()
            time.sleep(1)
            # Force deletion of the video object
            self.vid.__del__()
    

# This will prevent the user from closing the top window (which stalls the program)
def disable_event():
    tkMessageBox.showinfo("Info", "You cannot close this window, to quit close the other window.")
    pass



class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to RGB
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  #  cv2.COLOR_BGR2HSV
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            # Try many times to release the camera
            for i in range(0, 10):
                time.sleep(0.05)
                self.vid.release()
    print("Exiting App...")


# APP CODE FINISHED ##################################

# Begin camera selection + call to app
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
selected_cam = []

for webcam in valid_cams:
    caps.append(cv2.VideoCapture(webcam))

while True:
    # Capture frame-by-frame
    for webcam in valid_cams:
        ret, frame = caps[webcam].read()
        # Display the resulting frame
        cv2.putText(frame, 'Preview webcam ID: '+str(webcam), (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)
        cv2.putText(frame, 'press q to quit and start app', (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 0), 2)
        if len(selected_cam) > 0:
            if webcam in selected_cam:
                # TODO: Nice to have, a toggle (pressing a second time removes selection)
                cv2.putText(frame, 'Selected', (50, 150), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2)
        cv2.imshow('webcam'+str(webcam), frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break
    if k == ord(str(webcam)):
        print("Camera ID " + str(webcam) + " Selected")
        selected_cam.append(webcam)


print("Releasing cameras...")

# When everything done, release the capture
for cap in caps:
    cap.release()

for x in range(10):
    time.sleep(0.2)
    cv2.destroyAllWindows()

print("Starting app...")

time.sleep(2)

# TODO: Fix after building a toggle
# We keep the first selected element...
selected_video_source = int(np.unique(selected_cam)[0])

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Image/Video Capture", video_source=selected_video_source)
