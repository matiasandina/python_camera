## Pipeline 1 (acquisition)

1) Compressing video files (from large `.mp4` to smaller `.mp4` )
-rpi_vid_compression.py must be sent to directory containing videos to be compressed in rpi with this command:

```bash
scp rpi_vid_compression.py pi@IP:target_directory
```

- compression done using ffmpeg and requires a desired crf to be chosen - done with this command:

```bash
pi@raspberrypi $ ~target_directory python rpi_vid_compression.py --crf <desired_crf>
```

- compressed video files are placed in new folder "compressed_videos" within the directory that the videos are stored in
