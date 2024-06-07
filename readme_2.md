## Pipeline 2 (storage)

1) Sending videos to remote device
- send_vids.py must be sent to the desired directory in the raspberrypi with this command:

```bash
scp send_vids.py pi@IP:target_directory/compressed_videos
```

- local files = on rpi
- remote directory supplied should be directory within project folder for video storage
- call send_vids.py with filepaths to project folder and local_folder:

```bash
pi@raspberrypi $ ~target_directory python rpi_vid_compression.py --remote_dir <project_video_folder> --local_dir <local_folder>
```

2) Further processing on remote device
Changes to be made:
- Grayscale (optional)
- Downsize from resolution (optional) --> input preferred height AND width
- Optionally reduce fps (optional)

Parameters of video_processing.py:
source_folder --> subfolder in project directory for video storage
target_folder --> subfolder for processed videos in project directory
width, height --> desired resolution
fps --> desired frames per second
gray --> True or False, indeicate if videos should be Grayscale - default is False

-calling video_processing.py will fill target directory with processed videos
- must remove the videos from the directory if you wish to process a video with the same filepath again (does not override)

3) Cropping videos and creating clips

- Create clips first using ffmpeg
    - Choose beginning time stamp and duration for each clip:

```bash
ffmpeg -i "<processed_video_folder>/<file_name>.mp4" -ss <start> -t <duration> -c:v copy -c:a copy <output_folder>/<file_name>"
```

- Cropping clips (if needed)

    - Run cropper.py --> launches GUI that can be used for more convenient cropping
    - Choose desired clip one at a time, and drag to create a rectangle to indicate where to crop the videos
