# Python Camera Application

This application provides a flexible interface for video recording using OpenCV and PyQt5. 
It comprises four main components: `camera.py`, `videowriter.py`, `main.py`, and `camera_settings_ui.py`. 
There are other scripts in this repository that are not documented at the moment (less complex / usable / interdependent).

## Install

This software uses mostly two libraries:

* OpenCV
* imutils

Short story: YOU NEED TO INSTALL `imutils` from a specific branch

Long story: Read below

It turns out that there's a bug on the master branch of `imutils` and the camera stream was not obeying `resolution` parameters. See [this PR](https://github.com/PyImageSearch/imutils/pull/177). The class constructor totally disregards resolution and will always be set to (640x240). So we could also not get higher resolution and that's why we have to hack it by `cv2.resize()` later (see [#7](https://github.com/matiasandina/python_camera/issues/7]) and [#9](https://github.com/matiasandina/python_camera/issues/9)). 

This camera software application is somewhat dated (read from 2019!) and `imutils` is also dated/not regularly mantained. 

Nothing but patching is worth the time for now.

> [!IMPORTANT]  
> ANY NEW INSTALLS SHOULD BE DONE FROM SPECIFIC BRANCH

For GLOBAL install (*not recommended!!*)

```
sudo pip3 install git+https://github.com/karjanme/imutils.git@master
```
Inside environment

```
# conda activate  // source bin activate
(env-name)$ pip3 install git+https://github.com/karjanme/imutils.git@master
```

## Quick Start
### Running the Application
Run main.py directly from the command line with optional arguments for customization.

```
python3 main.py [arguments]
```

For a list of all possible arguments, use:

```
python3 main.py -h
```

### Using the PyQt5 UI for Easier Input:
Launch `camera_settings_ui.py` to input parameters through a graphical interface, which then starts `main.py` with the specified settings.

```
python3 camera_settings_ui.py
```

There might be some issues with pyqt5. For example, it needs pyqt5 multimedia, which needs to be installed in addition to `pyqt5`.
You can do so by running:

```
sudo apt install python3-pyqt5 python3-pyqt5.qtmultimedia libqt5multimedia5-plugins
```

This application has been developed for Raspberry Pis running debian, and is known to have issues in Ubuntu running wayland. 

## Components

### `camera.py`

**Description**: `VideoCamera()` class. Handles the camera operations including video capture and frame processing.
**Key Functionalities**: 
* Video capturing using OpenCV.
* Processing and manipulating video frames (e.g., adding timestamps to the frames). 
* Interfacing with `videowriter.py` for video recording (i.e., send frames to writing que according to desired fps).
* Filenaming
* Partition of videos (i.e., videos larger than 1 Gb will be chunked to avoid issues with handling large files)
**Interactions**:
`camera.py` is utilized by `main.py` to handle video capture and by `camera_settings_ui.py` to preview camera feed and trigger recording.

#### Troubleshooting `fps` and `resolution`:

Options for resolution and fps depend on the user knowing that the camera can provide frames at that speed/resolution. 
It's likely that slower fps can be properly handled (by dropping frames, see check_framerate() method in `camera.py`).
Frames will be timestamped using `datetime.datetime.now()` and timestamps will be saved in a text file with matching video filename.
This functionality has not been extensively tested.

#### Troubleshooting `record_enabled`:

If you want to enable recording. You need to explicitly enable it!

```
vc = VideoCamera(..., record_enabled = True)
```
or
```
vc = VideoCamera()
vc.record_enabled = True
```

Otherwise, this camera will **refuse** to record to file. It can be a bit tough to diagnose the problems that arise when this flag is set to False (the default). 
For user-friendly access, `main.py` has `record_enabled = True` hardcoded. Thus, `vc.start_recording()` will trigger the start of the recording.

### `videowriter.py`
**Description**: Manages the video recording process, including file writing and frame queue management.
**Key Functionalities**:
* Writing video frames to a file in a separate thread.
* Managing frame rate and video file properties.
**Interactions**:
Works in conjunction with `camera.py` to record and save video streams. This is a low-level class. 
Avoid modifying unless you know what you are doing!
The original comes from [this repo](https://github.com/ulrichstern/SkinnerTrax/blob/master/rt-trx/rt-trx.py) and has been modified by Matias Andina for this version.

### `main.py`
**Description**: Serves as the main executable script, combining functionalities of camera handling and user interaction.
**Key Functionalities**:
* Parsing command-line arguments for camera settings.
* Initiating video capture and handling user inputs for recording control.
**Interactions**:
Integrates `camera.py` and `videowriter.py` for complete camera operation.
Can be launched directly from command line or via `camera_settings_ui.py`.

#### Usage

Run main.py directly from the command line with optional arguments for customization.

```
python3 main.py [arguments]
```

For a list of all possible arguments, use:

```
python3 main.py -h
```


It contains minimal user interaction capabilities. Namely:

```
Press 'r' to start/stop recording, 'q' to quit.
```

### `camera_settings_ui.py`
**Description**: Provides a PyQt5-based graphical user interface for easier input of camera parameters.
**Key Functionalities**:
* Collects camera information (device name)
* Provides standard fps and resolutions combinations. **This will not work if you want to use custom ones!** For best performance, adjust camera settings according to your hardware capabilities.
* Graphical form for setting camera options.
* Launches `main.py` with the specified parameters on a separate thread.
**Interactions**:
Acts as a frontend for user interaction, passing chosen settings to `main.py`.
Additional Notes
