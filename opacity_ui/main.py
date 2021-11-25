import sys
import os
from PIL import Image
import cv2
import nibabel as nib
#from PIL.ImageQt import ImageQt
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QLabel
from PySide6.QtGui import QPixmap, QImage
from opacity_ui import Ui_MainWindow
from utils import opacity_change3
# pyside6-uic mainwindow.ui > ui_mainwindow.py


class OpacityWindow(QMainWindow):
    def __init__(self):
        super(OpacityWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # slider 1
        self.ui.verticalSlider.setMinimum(0)
        self.ui.verticalSlider.setMaximum(1000)
        self.ui.verticalSlider.setTickInterval(100)
        self.ui.verticalSlider.setTickPosition(QSlider.TicksLeft)

        # slider 2
        self.ui.verticalSlider_2.setMinimum(0)
        self.ui.verticalSlider_2.setMaximum(1000)
        self.ui.verticalSlider_2.setTickInterval(100)
        self.ui.verticalSlider_2.setTickPosition(QSlider.TicksLeft)

        # whenever the sliders change, execute the opacity change
        self.ui.verticalSlider.valueChanged.connect(self.opacity_change)
        self.ui.verticalSlider_2.valueChanged.connect(self.opacity_change)
        self.ui.horizontalSlider.valueChanged.connect(self.opacity_change)
        self.ui.horizontalSlider_2.valueChanged.connect(self.opacity_change)

        # load image
        self.image_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))

        self.image_1 = None
        self.image_2 = None
        self.image_3 = None

        self.load_images()

        # slider 3
        shape = self.image_1.shape
        self.ui.horizontalSlider.setMinimum(0)
        self.ui.horizontalSlider.setMaximum(shape[2])
        self.ui.horizontalSlider.setTickInterval(int(shape[2]/10))
        self.ui.horizontalSlider.setTickPosition(QSlider.TicksBelow)

        # slider 4
        self.ui.horizontalSlider_2.setMaximum(0)
        self.ui.horizontalSlider_2.setMaximum(255)
        self.ui.horizontalSlider_2.setTickInterval(25)
        self.ui.horizontalSlider_2.setTickPosition(QSlider.TicksBelow)

        # self.image_1 = Image.open(os.path.join(self.image_folder, "black_square.png")).convert('L')
        # self.image_1 = np.asarray(self.image_1)
        # self.image_2 = np.rot90(self.image_1)
        # self.image_3 = np.rot90(self.image_2)

        self.pixmap = self.convert_np_to_pixmap(self.image_1[:, :, 0])

        self.ui.label.setPixmap(self.pixmap)

    def load_images(self):
        path_one = "C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI\\Case5\\MRI\\Case5-T1.nii"
        path_two = "C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI\\Case3\\MRI\\Case3-T1.nii"
        path_three = "C:\\Users\\fryde\\Documents\\university\\master\\thesis\\datasets\\resect\\NIFTI\\Case6\\MRI\\Case6-T1.nii"


        self.image_1 = nib.load(path_one)
        self.image_1 = np.transpose(np.asarray(self.image_1.get_fdata()))

        self.image_2 = nib.load(path_two)
        self.image_2 = np.transpose((np.asarray(self.image_2.get_fdata())))

        self.image_3 = nib.load(path_three)
        self.image_3 = np.transpose(np.asarray(self.image_3.get_fdata()))

    def convert_np_to_pixmap(self, numpy_array):
        # convert to cv2
        frame = cv2.cvtColor(np.uint8(numpy_array), cv2.COLOR_GRAY2RGB)

        # convert to qimage
        h, w = numpy_array.shape[:2]
        bytes_per_line = 3 * w
        qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        # convert to pixmap
        pixmap = QPixmap.fromImage(qimage)

        return pixmap

    def opacity_change(self):
        op1 = self.ui.verticalSlider.value() / 1000  # maximum value of slider
        op2 = self.ui.verticalSlider_2.value() / 1000
        idx = self.ui.horizontalSlider.value()  # slice index
        threshold = self.ui.horizontalSlider_2.value()

        blended = opacity_change3(self.image_1[:, :, idx], self.image_2[:, :, idx], self.image_3[:, :, idx], op1, op2, threshold)
        self.pixmap = self.convert_np_to_pixmap(blended)
        self.ui.label.setPixmap(self.pixmap)


if __name__ == "__main__":
    app = QApplication([])

    window = OpacityWindow()
    window.show()

    sys.exit(app.exec())
