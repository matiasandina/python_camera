import os
from PyQt5.QtMultimedia import QImageEncoderSettings
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImageWriter

from ui_imagesettings_pyqt5 import Ui_ImageSettingsUi

def box_value(box):
    idx = box.currentIndex()
    return None if idx == -1 else box.itemData(idx)

def select_combo_box_item(box, value):
    idx = box.findData(value)
    if idx != -1:
        box.setCurrentIndex(idx)

class ImageSettings(QDialog):
    def __init__(self, imageCapture, parent=None):
        super().__init__(parent)
        self.imagecapture = imageCapture
        self._ui = Ui_ImageSettingsUi()
        self._ui.setupUi(self)

        # image codecs
        self._ui.imageCodecBox.addItem("Default image format", QImageWriter.supportedImageFormats()[0])
        supported_image_formats = QImageWriter.supportedImageFormats()
        for f in supported_image_formats:
            name = f.decode()
            self._ui.imageCodecBox.addItem(name, name)

        self._ui.imageQualitySlider.setRange(0, 100)

        self._ui.imageResolutionBox.addItem("Default Resolution", QSize())
        camera = imageCapture.captureSession().camera()
        supported_resolutions = camera.supportedViewfinderResolutions()
        for resolution in supported_resolutions:
            w, h = resolution.width(), resolution.height()
            self._ui.imageResolutionBox.addItem(f"{w}x{h}", resolution)

        select_combo_box_item(self._ui.imageCodecBox, imageCapture.encodingSettings().codec())
        select_combo_box_item(self._ui.imageResolutionBox, imageCapture.encodingSettings().resolution())
        self._ui.imageQualitySlider.setValue(imageCapture.encodingSettings().quality())

    def apply_image_settings(self):
        encoding_settings = self.imagecapture.encodingSettings()
        encoding_settings.setCodec(box_value(self._ui.imageCodecBox))
        encoding_settings.setQuality(self._ui.imageQualitySlider.value())
        encoding_settings.setResolution(box_value(self._ui.imageResolutionBox))
