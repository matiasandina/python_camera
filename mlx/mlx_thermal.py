import time
import board
import busio
import adafruit_mlx90640
import cv2
import numpy as np
from PIL import Image
import imutils
from collections import deque
import threading
import datetime


def save_to_file(filename, area, mean_temp, max_temp):
    current_time = datetime.datetime.now().isoformat("_")
    array_to_save = np.column_stack([current_time, area, mean_temp, max_temp])
    with open(filename,'a') as outfile:
        np.savetxt(outfile, array_to_save,
        delimiter=',', fmt='%s')
    

def access_pixel_intensity(img, contours):
    # create a mask
    mask = np.zeros(img.shape, np.uint8)
    # burn contour into mask
    cv2.drawContours(mask, contours, -1, 255, -1)
    #calculate mean value
    pixel_values = img[np.where(mask == 255)]
    return pixel_values
    
# This script will usuall fail with
# RunTimeError: Too many retries

# Ideally you can run this from a thread
# use t1 = threading.Thread(target=function, args()) t1.is_alive() to check script

def thermal_cam(show_video = True, save_data = False):

    # initialize stuff here
    i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

    mlx = adafruit_mlx90640.MLX90640(i2c)
    print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_32_HZ

    frame = [0] * 768

    # thresholding parameters

    min_temp = 27
    zero_temp = 25

    # frame averaging
    mean_temp = 0
    max_temp = 0
    maxlen = 3
    multiple_frames = deque(maxlen = maxlen)
    frame_number = 0

    avg_weights = [i + 1 for i in range(0,maxlen,1)]

    # create filename
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + "_temperature.csv"

    while True:
        
        try:
            mlx.getFrame(frame)
            
            # make everything below zero_temp go to zero
            frame = [value if value > zero_temp else 0 for value in frame]
            
            # get frame in np.uint8, correct format and transpose 
            frame2 = np.array(frame, np.uint8).reshape((32, 24), order="F").T
            # flip it (camera is twisted)
            # frame2 = np.rot90(frame2)
            frame2 = np.flip(frame2, 0)
            # append to deque and 
            # resize so that we can see
            multiple_frames.append(imutils.resize(frame2, height=320))
            # calculate average of stored frames 
            big_frame = np.average(multiple_frames, axis=0, weights = avg_weights)
            # scale it to 0 to 1 scale
            max_temp = 38
            scaled_big_frame = big_frame / max_temp

            # blur
            blurr = cv2.GaussianBlur(scaled_big_frame, (5,5), 0)

            # the second element is the matrix, the first element is the threshold
            # that's why we need [1] at the end
            binary = cv2.threshold(blurr,
                                   min_temp/max_temp, # min
                                   1, # max temp will be 1 because normalizerd
                                   cv2.THRESH_BINARY)[1]
            
            
            kernel = np.ones((11,11),np.uint8)
            closed = cv2.morphologyEx(binary.copy(), cv2.MORPH_CLOSE,
                                      kernel, iterations = 3)
            
           
            # find contours cv2.cvtColor(closed, cv2.COLOR_BGR2GRAY) 
            cnts = cv2.findContours(closed.copy().astype(np.uint8),
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_NONE)
            cnts = imutils.grab_contours(cnts)
            #print(len(cnts) > 0, end="\r")
            # if we detect more than one, sort them and get the biggest
            if (len(cnts) > 0):
                # get the one with max area
                cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
                # get area
                area = cv2.contourArea(cnts)
                # get pixel values and calculate mean
                pixel_values = access_pixel_intensity(img=blurr, contours=cnts)
                mean_temp = np.mean(pixel_values) * max_temp
                max_temp = np.max(pixel_values) * max_temp
                if (save_data):
                    save_to_file(filename, area, mean_temp, max_temp)
            else:
                area = 0
                mean_temp = 0
                max_temp = 0
            #print(area, end = "\r")
            cv2.drawContours(scaled_big_frame, cnts, -1, (0, 0, 0), 3)
            cv2.putText(scaled_big_frame,str(area), 
                    (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 255, 255),
                    2)
            cv2.putText(scaled_big_frame,str([np.round(mean_temp,2), np.round(max_temp, 2)]), 
                    (10, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 255, 255),
                    2)
            if (show_video):
                # this WINDOW_NORMAL thing is needed for some reason on the pi...
                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                cv2.imshow("frame", scaled_big_frame)
                cv2.namedWindow("closed", cv2.WINDOW_NORMAL)
                cv2.imshow("closed", closed)
                #cv2.namedWindow("binary", cv2.WINDOW_NORMAL)
                #cv2.imshow("binary", binary)
                k = cv2.waitKey(1)
                if (k == ord("q")):
                    break

            
        except ValueError:
            # these happen, no biggie - retry
            continue
        except RuntimeError:
            # these happen quite a lot
            cv2.destroyAllWindows()

    cv2.destroyAllWindows()


if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    t1 = threading.Thread(target=thermal_cam, args=(True, True))
    t1.deamon = True
    t1.start()
    running = True
    while(running):
        try:
            # sleep for a second
            time.sleep(1)
            running = t1.is_alive()
            if not running:
                print("camera died, restarting")
                t1.join()
                t1 = threading.Thread(target=thermal_cam, args=(True, True))
                t1.deamon=True
                t1.start()
                running = t1.is_alive()
                print("Camera back to life")
        except:
            pass

    #thermal_cam(show_video = True, save_data = False)
