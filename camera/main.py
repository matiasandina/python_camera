from camera import VideoCamera
import cv2
import datetime

def main():
    record_duration = "00:05:00" # change duration of recording here
    record_name = None # change from None to something else for naming
    vc = VideoCamera(usePiCamera=False, record=True, record_duration=record_duration, record_name = record_name)

    print("Starting camera preview. Press 'r' to start/stop recording, 'q' to quit.")
    recording = False
    recording_start_time = None
    while True:
        frame = vc.read()
        
        if recording:
            if not vc.is_recording():
                recording = False
                print("\nRecording ended.")
            else:
                elapsed_time = datetime.datetime.now() - recording_start_time
                elapsed_str = str(elapsed_time).split('.')[0]  # Format as HH:MM:SS
                print(f"Status: Recording {elapsed_str} / {record_duration}", end='\r')
        else:
            cv2.putText(frame, "NOT RECORDING", (frame.shape[0] // 5 , frame.shape[1] // 3), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.imshow("Camera Preview", frame)
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
            if recording:
                vc.stop_recording()
                recording = False
                print("\nRecording stopped.")
            break

    # Cleanup
    vc.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
