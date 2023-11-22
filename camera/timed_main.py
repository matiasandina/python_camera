import argparse
from camera import VideoCamera
import cv2
import datetime


def handle_start_time(record_start_time):
    """
    This function will turn the record_start_time into a proper datetime object
    The idea is that if now.hour > record_start_time.hour we will adjust the ymd of record_start_time to be tomorrow
    It will return the datetime that corresponds to either today at hms or tomorrow at hms
    """

    # handle record_start_time into datetime
    now = datetime.datetime.now()
    # Determine if the recording time is for today or tomorrow
    if now.hour > record_start_time.hour or (now.hour == record_start_time.hour and now.minute >= record_start_time.minute):
        # Set to tomorrow's date
        tomorrow = now.date() + datetime.timedelta(days=1)
        record_start_datetime = datetime.datetime.combine(tomorrow, record_start_time.time())
    else:
        record_start_datetime = datetime.datetime.combine(now.date(), record_start_time.time())
    return record_start_datetime


def main():
    parser = argparse.ArgumentParser(description="Run camera with specified settings.")
    parser.add_argument("--device_name", type=str, default="0", help="Camera device name or index (default: 0)")
    parser.add_argument("--resolution", type=str, default="640x480", help="Resolution (default: 640x480)")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")
    parser.add_argument("--flip", action='store_true', help="Flip the camera feed")
    parser.add_argument("--use_pi_camera", action='store_true', default=False, help="Use PiCamera (default: True)")
    parser.add_argument("--record_duration", type=str, default=None, help="Record duration in HH:MM:SS", required=True)
    parser.add_argument("--record_name", type=str, default=None, help="Name of the record file (default: None)")
    parser.add_argument("--record_start_time", type=str, default=None, help="Time of record start in HH:MM:SS (default: None). Recording will start at the next HH:MM:SS==record_start_time and last for `record_duration`.", required=True)

    args = parser.parse_args()
    # Convert device_name to int if it's a digit, otherwise keep it as string
    device_name = int(args.device_name) if args.device_name.isdigit() else args.device_name
    # Convert resolution from string to tuple
    resolution = tuple(map(int, args.resolution.split('x')))
    # Convert "None" strings to Python None value
    record_duration = None if args.record_duration == "None" else args.record_duration
    record_name = None if args.record_name == "None" else args.record_name
    try:
        record_start_time = datetime.datetime.strptime(args.record_start_time, '%H:%M:%S')
    except ValueError:
        raise ValueError("`recording_start_time` must be in HH:MM:SS format")

    # We need a fixed record duration, otherwise this will loop
    try:
        session_time = datetime.datetime.strptime(record_duration, '%H:%M:%S')
        # Transform the time into number of seconds
        record_duration_sec = (session_time.hour * 60 + session_time.minute) * 60 + session_time.second
    except ValueError:
        raise ValueError("record_duration must be in HH:MM:SS format")

    record_start_datetime = handle_start_time(record_start_time)
    record_end_datetime = record_start_datetime + datetime.timedelta(seconds = record_duration_sec)

    # Initialize VideoCamera with parsed arguments
    vc = VideoCamera(
        src=device_name,
        flip=args.flip,
        usePiCamera=args.use_pi_camera,
        fps=args.fps,
        resolution=resolution,
        record_duration=record_duration,
        record_name=record_name,
        record_enabled = True # <- this is key to enable recordings!!!
    )

    print(f"Starting camera preview. Recording from {record_start_datetime} to {record_end_datetime}. Press 'q' to quit.")
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
        # Check for 'q' key press to quit recording or the program
        if key == ord('q'):
            if recording:
                vc.stop_recording()
                recording = False
                print("\nRecording stopped.")
            break

        now = datetime.datetime.now()
        # Check if it's time to stop the recording
        if recording and now >= record_end_datetime:
            vc.stop_recording() 
            recording = False
            print("\nRecording stopped.")

        # Check if it's time to start recording
        if not recording and now >= record_start_datetime:
            # do not trigger a new start 
            if now <= record_end_datetime:
                vc.start_recording()
                recording = True
                recording_start_time = datetime.datetime.now()
                print("\nRecording started.")
            else:
                print("Recorded Finished. Exiting.")
                break

    # Cleanup
    vc.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
