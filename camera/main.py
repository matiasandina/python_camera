import argparse
from camera import VideoCamera
import cv2

def main():
    parser = argparse.ArgumentParser(description="Run camera with specified settings.")
    parser.add_argument("--device_name", type=str, default="0", help="Camera device name or index (default: 0)")
    parser.add_argument("--resolution", type=str, default="640x480", help="Resolution (default: 640x480)")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")
    parser.add_argument("--flip", action='store_true', help="Flip the camera feed")
    parser.add_argument("--use_pi_camera", action='store_true', default=False, help="Use PiCamera (default: True)")
    parser.add_argument("--record_duration", type=str, default=None, help="Record duration in HH:MM:SS (default: None)")
    parser.add_argument("--record_name", type=str, default=None, help="Name of the record file (default: None)")

    args = parser.parse_args()
    
    # Convert device_name to int if it's a digit, otherwise keep it as string
    device_name = int(args.device_name) if args.device_name.isdigit() else args.device_name
    # Convert resolution from string to tuple
    resolution = tuple(map(int, args.resolution.split('x')))
    # Convert "None" strings to Python None value
    record_duration = None if args.record_duration == "None" else args.record_duration
    record_name = None if args.record_name == "None" else args.record_name

    # Initialize VideoCamera with parsed arguments
    vc = VideoCamera(
        src=device_name,
        flip=args.flip,
        usePiCamera=args.use_pi_camera,
        fps=args.fps,
        resolution=resolution,
        record_duration=record_duration,
        record_name=record_name
    )

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
