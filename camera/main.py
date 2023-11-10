from camera import VideoCamera
import cv2
import datetime

def main():
    vc = VideoCamera(usePiCamera=False, record=True, record_duration="00:00:10")

    print("Starting camera preview. Press 'r' to start/stop recording, 'q' to quit.")
    recording = False
    recording_start_time = None
    while True:
        frame = vc.read()
        cv2.imshow("Camera Preview", frame)

        if recording:
            if not vc.is_recording():
                recording = False
                print("\nRecording ended.")
            else:
                elapsed_time = datetime.datetime.now() - recording_start_time
                elapsed_str = str(elapsed_time).split('.')[0]  # Format as HH:MM:SS
                print(f"Status: Recording {elapsed_str} / 00:00:10", end='\r')

        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            if not recording:
                vc.start_recording()
                recording = True
                recording_start_time = datetime.datetime.now()
                print("\nRecording started.")
            else:
                vc.stop_recording()
                recording = False
                print("\nRecording stopped.")
        elif key == ord('q'):
            break

    # Cleanup
    vc.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
