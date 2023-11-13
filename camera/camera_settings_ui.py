import os
import platform
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QLineEdit
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from camera import VideoCamera
import cv2
import datetime

class CameraSettingsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Camera Source
        self.src_combo = QComboBox(self)
        self.populateCameraList()
        layout.addWidget(QLabel('Camera Source'))
        layout.addWidget(self.src_combo)

        # Manually set common resolutions
        self.resolution_combo = QComboBox(self)
        common_resolutions = ["640x480", "800x600", "1280x720", "1920x1080"]
        for res in common_resolutions:
            self.resolution_combo.addItem(res)
        layout.addWidget(QLabel('Resolution'))
        layout.addWidget(self.resolution_combo)

        # Manually set common FPS values
        self.fps_combo = QComboBox(self)
        common_fps = ["15", "24", "30", "60"]
        for fps in common_fps:
            self.fps_combo.addItem(fps)
        layout.addWidget(QLabel('FPS'))
        layout.addWidget(self.fps_combo)

        # Other Settings
        self.flip_check = QCheckBox('Flip Image', self)
        layout.addWidget(self.flip_check)
        self.usePiCamera_check = QCheckBox('Use PiCamera', self)
        layout.addWidget(self.usePiCamera_check)
        self.record_duration_input = QLineEdit(self)
        layout.addWidget(QLabel('Record Duration (HH:MM:SS)'))
        layout.addWidget(self.record_duration_input)
        self.record_name_input = QLineEdit(self)
        layout.addWidget(QLabel('Record Name'))
        layout.addWidget(self.record_name_input)

        # Start Button
        self.start_button = QPushButton('Start Camera', self)
        self.start_button.clicked.connect(self.onStartClicked)
        layout.addWidget(self.start_button)

        self.setLayout(layout)
        self.setWindowTitle('Camera Settings')

    def populateCameraList(self):
        availableCameras = QCameraInfo.availableCameras()
        for camera in availableCameras:
            self.src_combo.addItem(camera.description(), camera.deviceName())

        # Automatically update resolution and FPS when camera selection changes
        self.src_combo.currentIndexChanged.connect(self.updateCameraCapabilities)

    def updateCameraCapabilities(self):
        cameraDeviceName = self.src_combo.currentData()
        camera = QCamera(cameraDeviceName)
        camera.load()

        # Update Resolutions
        self.resolution_combo.clear()
        supportedResolutions = camera.supportedViewfinderResolutions()
        for resolution in supportedResolutions:
            self.resolution_combo.addItem(f"{resolution.width()}x{resolution.height()}")

        # Update FPS
        self.fps_combo.clear()
        supportedFrameRates = camera.supportedViewfinderFrameRateRanges()
        for range in supportedFrameRates:
            self.fps_combo.addItem(f"{range.maximumFrameRate:.2f}")

        camera.unload()

    def onStartClicked(self):
        cameraDeviceName = self.src_combo.currentData()
        resolution = self.resolution_combo.currentText()
        fps = float(self.fps_combo.currentText())
        flip = self.flip_check.isChecked()
        usePiCamera = self.usePiCamera_check.isChecked()
        record_duration = self.record_duration_input.text() or None
        record_name = self.record_name_input.text() or None
        vc = VideoCamera(src = cameraDeviceName, flip = flip, usePiCamera=usePiCamera, fps = fps, resolution = resolution, record_duration = record_duration, record_name = record_name)    
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

        print("Starting camera with the following settings:")
        print(f"src: {src}, flip: {flip}, usePiCamera: {usePiCamera}, fps: {fps}, resolution: {resolution}, record_duration: {record_duration}, record_name: {record_name}")

if __name__ == '__main__':
    # Check if the operating system is Ubuntu running GNOME on Wayland
    if platform.system() == 'Linux' and 'GNOME' in os.environ.get('XDG_CURRENT_DESKTOP', '') and os.environ.get('XDG_SESSION_TYPE', '') == 'wayland':
        os.environ['QT_QPA_PLATFORM'] = 'wayland'
    app = QApplication(sys.argv)
    ex = CameraSettingsUI()
    ex.show()
    sys.exit(app.exec_())
