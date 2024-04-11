import os
from pathlib import Path
import sys

from PyQt5.QtWidgets import QMainWindow, QAction, QActionGroup, QMessageBox
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import (QAudioInput, QCamera, QCameraInfo, QCameraImageCapture,
                               QMediaRecorder, QMediaMetaData)
from PyQt5.QtCore import QDateTime, QTimer, Qt, pyqtSlot

#from metadatadialog import MetaDataDialog
from imagesettings_pyqt5 import ImageSettings
from videosettings_pyqt5 import VideoSettings, is_android

if is_android:
    from android.permissions import Permission, request_permissions
    from android.activity import bind as android_bind
    from PyQt5.QtAndroidExtras import QAndroidJniObject, QAndroidIntent

    @pyqtSlot(bool)
    def androidPermissionResult(granted):
        if granted:
            # Initialize the camera and microphone
            window.initialize()
        else:
            QMessageBox.critical(None, "Permission Denied", "Camera and microphone permissions are required.")
            sys.exit(1)
else:
    from ui_camera_pyqt5 import Ui_Camera

class Camera(QMainWindow):
    def __init__(self):
        super().__init__()

        self._video_devices_group = None
        self.m_imageCapture = None
        self.m_camera = None
        self.m_mediaRecorder = None

        self.m_isCapturingImage = False
        self.m_applicationExiting = False
        self.m_doImageCapture = True

        self.m_metaDataDialog = None

        self._ui = Ui_Camera()
        self._ui.setupUi(self)
        image = Path(__file__).parent / "shutter.svg"
        self._ui.takeImageButton.setIcon(QIcon(str(image)))
        if not is_android:
            self._ui.actionAbout_Qt.triggered.connect(QApplication.aboutQt)

        # Disable all buttons by default
        self.updateCameraActive(False)
        self.readyForCapture(False)
        self._ui.recordButton.setEnabled(False)
        self._ui.pauseButton.setEnabled(False)
        self._ui.stopButton.setEnabled(False)
        self._ui.metaDataButton.setEnabled(False)

        if is_android:
            request_permissions([Permission.CAMERA, Permission.RECORD_AUDIO], androidPermissionResult)
        else:
            # Try to initialize the camera and microphone
            self.initialize()

    @pyqtSlot()
    def initialize(self):
        self.m_audioInput = QAudioInput()
        #self.m_audioInput.setAudioInput(self.m_audioInput)

        # Camera devices
        self._video_devices_group = QActionGroup(self)
        self._video_devices_group.setExclusive(True)
        self.updateCameras()

        self._video_devices_group.triggered.connect(self.updateCameraDevice)
        self._ui.captureWidget.currentChanged.connect(self.updateCaptureMode)

        self._ui.metaDataButton.clicked.connect(self.showMetaDataDialog)
        self._ui.exposureCompensation.valueChanged.connect(self.setExposureCompensation)

        default_camera_info = QCameraInfo.defaultCamera()
        if default_camera_info.isNull():
            QMessageBox.critical(None, "No Camera Found", "No camera device found.")
            sys.exit(1)
        self.setCamera(default_camera_info)

    @pyqtSlot(QCameraInfo)
    def setCamera(self, camera_info):
        self.m_camera = QCamera(camera_info)

        self.m_camera.stateChanged.connect(lambda state: self.updateCameraActive(state))
        self.m_camera.error.connect(self.displayCameraError)

        if not self.m_mediaRecorder:
            self.m_mediaRecorder = QMediaRecorder(self.m_camera)

        if not self.m_imageCapture:
            self.m_imageCapture = QCameraImageCapture(self.m_camera)
            self.m_imageCapture.imageCaptured.connect(self.processCapturedImage)
            self.m_imageCapture.imageSaved.connect(self.imageSaved)
            self.m_imageCapture.error.connect(self.displayCaptureError)

        # Set the viewfinder on the camera
        self.m_camera.setViewfinder(self._ui.viewfinder)

        self.updateCameraActive(self.m_camera.state() == QCamera.ActiveState)

        self.updateCaptureMode()

        self.m_camera.start()

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        key = event.key()
        if key == Qt.Key_CameraFocus:
            self.displayViewfinder()
            event.accept()
        elif key == Qt.Key_Camera:
            if self.m_doImageCapture:
                self.takeImage()
            else:
                if self.m_mediaRecorder.state() == QMediaRecorder.RecordingState:
                    self.stop()
                else:
                    self.record()

            event.accept()
        else:
            super().keyPressEvent(event)

    @pyqtSlot()
    def updateRecordTime(self):
        d = self.m_mediaRecorder.duration() / 1000
        self._ui.statusbar.showMessage(f"Recorded {d} sec")

    @pyqtSlot(int, QImage)
    def processCapturedImage(self, requestId, img):
        scaled_image = img.scaled(self._ui.viewfinder.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._ui.lastImagePreviewLabel.setPixmap(QPixmap.fromImage(scaled_image))

        # Display captured image for 4 seconds.
        self.displayCapturedImage()
        QTimer.singleShot(4000, self.displayViewfinder)

    @pyqtSlot()
    def configureCaptureSettings(self):
        if self.m_doImageCapture:
            self.configureImageSettings()
        else:
            self.configureVideoSettings()

    @pyqtSlot()
    def configureVideoSettings(self):
        settings_dialog = VideoSettings(self.m_mediaRecorder)

        if settings_dialog.exec_():
            settings_dialog.apply_settings()

    @pyqtSlot()
    def configureImageSettings(self):
        settings_dialog = ImageSettings(self.m_imageCapture)

        if settings_dialog.exec_():
            settings_dialog.apply_image_settings()

    @pyqtSlot()
    def record(self):
        self.m_mediaRecorder.record()
        self.updateRecordTime()

    @pyqtSlot()
    def pause(self):
        self.m_mediaRecorder.pause()

    @pyqtSlot()
    def stop(self):
        self.m_mediaRecorder.stop()

    @pyqtSlot(bool)
    def setMuted(self, muted):
        self.m_camera.setMuted(muted)

    @pyqtSlot()
    def takeImage(self):
        self.m_isCapturingImage = True
        self.m_imageCapture.capture()

    @pyqtSlot(int, QCameraImageCapture.Error, str)
    def displayCaptureError(self, id, error, errorString):
        QMessageBox.warning(self, "Image Capture Error", errorString)
        self.m_isCapturingImage = False

    @pyqtSlot()
    def startCamera(self):
        self.m_camera.start()

    @pyqtSlot()
    def stopCamera(self):
        self.m_camera.stop()

    @pyqtSlot()
    def updateCaptureMode(self):
        tab_index = self._ui.captureWidget.currentIndex()
        self.m_doImageCapture = (tab_index == 0)

    @pyqtSlot(bool)
    def updateCameraActive(self, state):
        if state == QCamera.ActiveState:
            self._ui.actionStartCamera.setEnabled(False)
            self._ui.actionStopCamera.setEnabled(True)
            self._ui.captureWidget.setEnabled(True)
            self._ui.actionSettings.setEnabled(True)
        else:
            self._ui.actionStartCamera.setEnabled(True)
            self._ui.actionStopCamera.setEnabled(False)
            self._ui.captureWidget.setEnabled(False)
            self._ui.actionSettings.setEnabled(False)

    @pyqtSlot(QMediaRecorder.State)
    def updateRecorderState(self, state):
        if state == QMediaRecorder.StoppedState:
            self._ui.recordButton.setEnabled(True)
            self._ui.pauseButton.setEnabled(True)
            self._ui.stopButton.setEnabled(False)
            self._ui.metaDataButton.setEnabled(True)
        elif state == QMediaRecorder.PausedState:
            self._ui.recordButton.setEnabled(True)
            self._ui.pauseButton.setEnabled(False)
            self._ui.stopButton.setEnabled(True)
            self._ui.metaDataButton.setEnabled(False)
        elif state == QMediaRecorder.RecordingState:
            self._ui.recordButton.setEnabled(False)
            self._ui.pauseButton.setEnabled(True)
            self._ui.stopButton.setEnabled(True)
            self._ui.metaDataButton.setEnabled(False)

    @pyqtSlot(int)
    def setExposureCompensation(self, index):
        self.m_camera.setExposureCompensation(index * 0.5)

    @pyqtSlot()
    def displayRecorderError(self):
        if self.m_mediaRecorder.error() != QMediaRecorder.NoError:
            QMessageBox.warning(self, "Capture Error", self.m_mediaRecorder.errorString())

    @pyqtSlot()
    def displayCameraError(self):
        if self.m_camera.error() != QCamera.NoError:
            QMessageBox.warning(self, "Camera Error", self.m_camera.errorString())

    @pyqtSlot(QAction)
    def updateCameraDevice(self, action):
        camera_info = action.data()
        self.setCamera(camera_info)

    @pyqtSlot()
    def displayViewfinder(self):
        self._ui.stackedWidget.setCurrentIndex(0)

    @pyqtSlot()
    def displayCapturedImage(self):
        self._ui.stackedWidget.setCurrentIndex(1)

    @pyqtSlot(bool)
    def readyForCapture(self, ready):
        self._ui.takeImageButton.setEnabled(ready)

    @pyqtSlot(int, str)
    def imageSaved(self, id, fileName):
        f = QDir.toNativeSeparators(fileName)
        self._ui.statusbar.showMessage(f"Captured \"{f}\"")

        self.m_isCapturingImage = False
        if self.m_applicationExiting:
            self.close()

    def closeEvent(self, event):
        if self.m_isCapturingImage:
            self.setEnabled(False)
            self.m_applicationExiting = True
            event.ignore()
        else:
            event.accept()

    @pyqtSlot()
    def updateCameras(self):
        self._ui.menuDevices.clear()
        available_cameras = QCameraInfo.availableCameras()
        for camera_info in available_cameras:
            video_device_action = QAction(camera_info.description(),
                                          self._video_devices_group)
            video_device_action.setCheckable(True)
            video_device_action.setData(camera_info)
            if camera_info == QCameraInfo.defaultCamera():
                video_device_action.setChecked(True)

            self._ui.menuDevices.addAction(video_device_action)

    @pyqtSlot()
    def showMetaDataDialog(self):
        if not self.m_metaDataDialog:
            self.m_metaDataDialog = MetaDataDialog(self)
        self.m_metaDataDialog.setAttribute(Qt.WA_DeleteOnClose, False)
        if self.m_metaDataDialog.exec_() == QDialog.Accepted:
            self.saveMetaData()

    @pyqtSlot()
    def saveMetaData(self):
        data = QMediaMetaData()
        for i in range(0, QMediaMetaData.NumMetaData):
            val = self.m_metaDataDialog.m_metaDataFields[i].text()
            if val:
                key = QMediaMetaData.Key(i)
                if key == QMediaMetaData.CoverArtImage:
                    cover_art = QImage(val)
                    data.insert(key, cover_art)
                elif key == QMediaMetaData.ThumbnailImage:
                    thumbnail = QImage(val)
                    data.insert(key, thumbnail)
                elif key == QMediaMetaData.Date:
                    date = QDateTime.fromString(val)
                    data.insert(key, date)
                else:
                    data.insert(key, val)

        self.m_mediaRecorder.setMetaData(data)


import os

# Set the QT_LOGGING_RULES environment variable
os.environ['QT_LOGGING_RULES'] = 'qt.*=true'

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = Camera()
    window.show()
    sys.exit(app.exec_())
