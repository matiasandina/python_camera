import cv2
import numpy as np
import argparse

class VideoSelector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError("Unable to read file!")
        self.regions = {
            "light_cage": None,
            "dark_cage": None
        }
        self.cropping = False
        self.coords = []
        self.closed = False

    def select_areas(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to read the first frame!")

        self.oriImage = frame.copy()
        self.clone = frame.copy()
        
        cv2.namedWindow("Video Selector")
        cv2.setMouseCallback("Video Selector", self.mouse_crop)

        while not all(self.regions.values()):
            while not self.closed:
                self.update_instructions()  # Update instructions every frame
                cv2.imshow("Video Selector", self.clone)
                key = cv2.waitKey(25) 

                if key == ord('d') and self.cropping:
                    cv2.polylines(self.clone, [np.array(self.coords)], True, (130, 22, 219), 2)
                    self.cropping = False
                    self.closed = True
                    print("Polygon closed. Press 's' to save or 'q' to quit.")
                elif key == ord('q'):
                    print("User requested exit via 'q'. Exiting without saving current selection.")
                    return

            # Handle post-closure actions
            while self.closed:
                self.update_instructions()  # Update instructions every frame
                cv2.imshow("Video Selector", self.clone)
                key = cv2.waitKey(25)
                if key == ord('s'):
                    self.save_region()
                    self.reset_for_new_region()
                    break
                elif key == ord('q'):
                    print("User requested exit via 'q'. Exiting without saving current selection.")
                    return

        cv2.destroyAllWindows()

    def save_region(self):
        if self.regions["light_cage"] is None:
            self.regions["light_cage"] = self.coords.copy()
            print("Light cage coordinates saved:", self.regions["light_cage"])
        elif self.regions["dark_cage"] is None:
            self.regions["dark_cage"] = self.coords.copy()
            print("Dark cage coordinates saved:", self.regions["dark_cage"])

    def reset_for_new_region(self):
        self.clone = self.oriImage.copy()
        self.coords = []
        self.cropping = False
        self.closed = False

    def mouse_crop(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and not self.closed:
            self.coords.append((x, y))
            cv2.circle(self.clone, (x, y), 5, (130, 22, 219), -1)
            if len(self.coords) > 1:
                cv2.polylines(self.clone, [np.array(self.coords)], False, (130, 22, 219), 2)
            self.cropping = True
        elif event == cv2.EVENT_LBUTTONDBLCLK and self.cropping:
            cv2.polylines(self.clone, [np.array(self.coords)], True, (130, 22, 219), 2)
            self.cropping = False
            self.closed = True
            print("Polygon closed. Press 'd' to confirm or continue drawing.")

    def update_instructions(self):
        if self.closed:
            instruction = "Press 's' to save."
            font_color = (255, 0, 0)
            cv2.putText(self.clone, instruction, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, font_color, 2, cv2.LINE_AA)
            return
        elif self.regions["light_cage"] is None:
            instruction = "Light cage polygon. Press 'd' to close it"
            font_color = (255, 255, 255)
        elif self.regions["dark_cage"] is None:
            instruction = "Draw dark cage polygon. Press 'd' to close it"
            font_color = (0, 0, 0)
        cv2.putText(self.clone, instruction, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, font_color, 1, cv2.LINE_AA)

    def get_coords(self):
        return self.regions["light_cage"], self.regions["dark_cage"]

    def release(self):
        self.cap.release()

    def get_shape(self):
        ret, frame = self.cap.read()
        if ret:
            return frame.shape

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video ROI Selector")
    parser.add_argument('--video_path', help="Path to the video file")
    args = parser.parse_args()

    selector = VideoSelector(args.video_path)
    print(selector.get_shape())
    selector.select_areas()

    light_cage_coords, dark_cage_coords = selector.get_coords()
    selector.release()

    if light_cage_coords:
        print("Light cage coordinates:", light_cage_coords)
    if dark_cage_coords:
        print("Dark cage coordinates:", dark_cage_coords)
